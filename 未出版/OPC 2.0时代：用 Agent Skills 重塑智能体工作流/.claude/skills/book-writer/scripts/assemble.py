#!/usr/bin/env python3
"""
章节组装工具

将各小节文件按顺序合并为完整章节文件。

用法：
    python assemble.py <书籍根目录> <章号>

章号：
    0 = 引言
    1 = 第一章
    2 = 第二章
    3 = 第三章
"""

import sys
import re
from pathlib import Path

CHAPTER_CONFIG = {
    "0": {
        "dir": "引言",
        "title": "引言",
        "output": "引言/引言_完整.md",
    },
    "1": {
        "dir": "第一章_认识Agent_Skill",
        "title": "第一章 认识 Agent Skill",
        "output": "第一章_认识Agent_Skill/第一章_完整.md",
    },
    "2": {
        "dir": "第二章_Skill的分类与生态",
        "title": "第二章 Skill 的分类与生态",
        "output": "第二章_Skill的分类与生态/第二章_完整.md",
    },
    "3": {
        "dir": "第三章_Agent_Skill开发实战",
        "title": "第三章 Agent Skill 开发实战",
        "output": "第三章_Agent_Skill开发实战/第三章_完整.md",
    },
}


def strip_frontmatter(content):
    """移除 YAML frontmatter。"""
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL).strip()


def count_words(text):
    """统计字数（中文字符 + 英文单词）。"""
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english = len(re.findall(r"[a-zA-Z]+", text))
    return chinese + english


def get_sort_key(filename):
    """从文件名提取排序键。"""
    # 匹配 "00_", "1.1.1_", "2.1_", "3.1_" 等模式
    match = re.match(r"^(\d+(?:\.\d+)*)", filename)
    if match:
        parts = match.group(1).split(".")
        return tuple(int(p) for p in parts)
    return (999,)


def assemble_chapter(book_dir, chapter_num):
    """组装指定章节。"""
    book_path = Path(book_dir)

    if chapter_num not in CHAPTER_CONFIG:
        print(f"无效的章号: {chapter_num}")
        print("可用章号: 0(引言), 1(第一章), 2(第二章), 3(第三章)")
        return False

    config = CHAPTER_CONFIG[chapter_num]
    chapter_dir = book_path / config["dir"]

    if not chapter_dir.exists():
        print(f"章节目录不存在: {chapter_dir}")
        return False

    # 收集所有小节文件（排除 _完整.md）
    section_files = []
    for md_file in chapter_dir.glob("*.md"):
        if md_file.name.endswith("_完整.md"):
            continue
        section_files.append(md_file)

    # 按文件名中的数字排序
    section_files.sort(key=lambda f: get_sort_key(f.name))

    if not section_files:
        print(f"未找到小节文件: {chapter_dir}")
        return False

    # 组装
    parts = []
    parts.append(f"# {config['title']}\n")

    total_words = 0
    for i, sf in enumerate(section_files):
        content = sf.read_text(encoding="utf-8")
        body = strip_frontmatter(content)

        if not body:
            print(f"  ⚠️ 跳过空文件: {sf.name}")
            continue

        words = count_words(body)
        total_words += words
        print(f"  ✅ {sf.name} ({words:,} 字)")

        parts.append(body)

        # 在小节之间添加分隔
        if i < len(section_files) - 1:
            parts.append("\n---\n")

    # 写入完整章节文件
    output_path = book_path / config["output"]
    assembled = "\n\n".join(parts)
    output_path.write_text(assembled, encoding="utf-8")

    print(f"\n{'=' * 50}")
    print(f"📖 {config['title']} 组装完成")
    print(f"   小节数: {len(section_files)}")
    print(f"   总字数: {total_words:,}")
    print(f"   输出到: {output_path}")
    print(f"{'=' * 50}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python assemble.py <书籍根目录> <章号>")
        print("章号: 0=引言, 1=第一章, 2=第二章, 3=第三章")
        sys.exit(1)

    success = assemble_chapter(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
