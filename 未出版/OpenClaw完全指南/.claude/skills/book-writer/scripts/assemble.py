#!/usr/bin/env python3
"""
章节组装工具

将各小节合并为完整章节。

用法：
    python assemble.py <书籍根目录> <章号>

章号对应：
    0 = 序章
    1 = 第一部分
    2 = 第二部分
    3 = 第三部分
    4 = 第四部分
    5 = 终章
    6 = 附录
    all = 组装所有章节

示例：
    python assemble.py . 1
    python assemble.py . all
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict


CHAPTER_MAP = {
    "0": {"dir": "序章", "title": "序章"},
    "1": {"dir": "第一部分", "title": "第一部分"},
    "2": {"dir": "第二部分", "title": "第二部分"},
    "3": {"dir": "第三部分", "title": "第三部分"},
    "4": {"dir": "第四部分", "title": "第四部分"},
    "5": {"dir": "终章", "title": "终章"},
    "6": {"dir": "附录", "title": "附录"},
}


def parse_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """解析Markdown文件的YAML frontmatter。"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None

    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def get_section_files(chapter_path: Path) -> List[Path]:
    """获取章节下所有小节文件，按节号排序。"""
    sections = []

    for md_file in chapter_path.glob("*.md"):
        # 跳过组装后的文件
        if "_完整" in md_file.name or "_第" in md_file.name:
            continue

        # 尝试从文件名或frontmatter获取节号
        section_id = None
        content = md_file.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)

        if fm and 'section_id' in fm:
            section_id = fm['section_id']
        else:
            # 从文件名提取节号
            match = re.match(r'(\d+\.\d+)', md_file.name)
            if match:
                section_id = match.group(1)

        if section_id:
            sections.append((section_id, md_file))

    # 按节号排序
    def sort_key(item):
        sid = item[0]
        parts = sid.split('.')
        return (int(parts[0]), int(parts[1]))

    sections.sort(key=sort_key)
    return [f for _, f in sections]


def assemble_chapter(book_dir: Path, chapter_num: str) -> bool:
    """组装指定章节。"""
    chapter_info = CHAPTER_MAP.get(chapter_num)
    if not chapter_info:
        print(f"错误: 无效的章号 {chapter_num}")
        print(f"有效章号: {', '.join(CHAPTER_MAP.keys())}")
        return False

    chapter_name = chapter_info['dir']
    chapter_path = book_dir / chapter_name

    if not chapter_path.exists():
        print(f"错误: 章节目录不存在 {chapter_path}")
        return False

    print(f"📦 正在组装: {chapter_name}")
    print("=" * 60)

    # 获取所有小节
    section_files = get_section_files(chapter_path)

    if not section_files:
        print("  未找到小节文件")
        return False

    print(f"  找到 {len(section_files)} 个小节")

    # 收集所有内容
    assembled_sections = []
    total_words = 0

    for i, section_file in enumerate(section_files, 1):
        content = section_file.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)

        section_id = fm.get('section_id', '?') if fm else '?'
        title = fm.get('title', section_file.stem) if fm else section_file.stem
        word_count = int(fm.get('word_count', 0)) if fm else 0

        # 移除frontmatter，保留正文
        body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

        assembled_sections.append({
            'index': i,
            'section_id': section_id,
            'title': title,
            'file': section_file.name,
            'body': body.strip(),
            'word_count': word_count,
        })

        total_words += word_count
        print(f"  [{i}] {section_id} {title} ({word_count}字)")

    # 生成组装后的文件
    output_name = f"{chapter_name}_完整.md"
    output_path = chapter_path / output_name

    lines = [
        f"# {chapter_info['title']}",
        "",
        f"> 组装时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 小节数: {len(assembled_sections)}",
        f"> 总字数: {total_words:,}",
        "",
        "---",
        "",
    ]

    for section in assembled_sections:
        lines.append(f"## {section['index']}. {section['title']}")
        lines.append("")
        lines.append(f"*> 节号: {section['section_id']} | 原文件: {section['file']}*")
        lines.append("")
        lines.append(section['body'])
        lines.append("")
        lines.append("---")
        lines.append("")

    output_path.write_text('\n'.join(lines), encoding='utf-8')

    print("\n" + "=" * 60)
    print(f"✅ 组装完成: {output_path}")
    print(f"   总字数: {total_words:,}")
    print(f"   包含 {len(assembled_sections)} 个小节")

    return True


def assemble_all(book_dir: Path) -> bool:
    """组装所有章节。"""
    print("📚 开始组装所有章节...")
    print("=" * 60)

    success_count = 0
    for chapter_num in CHAPTER_MAP.keys():
        if assemble_chapter(book_dir, chapter_num):
            success_count += 1
        print()

    print("=" * 60)
    print(f"✅ 成功组装 {success_count}/{len(CHAPTER_MAP)} 个章节")
    return success_count == len(CHAPTER_MAP)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    chapter_arg = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    if chapter_arg == 'all':
        success = assemble_all(book_dir)
    else:
        success = assemble_chapter(book_dir, chapter_arg)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
