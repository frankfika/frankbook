#!/usr/bin/env python3
"""
初始化新小节工具

创建新的章节文件，包含标准 frontmatter。

用法：
    python init.py <书籍根目录> <节号> <标题> [目标字数]

示例：
    python init.py . 1.4.1 "新增小节标题" 2000
    python init.py . 2.4 "Skill调试技巧" 1500
"""

import sys
import re
from pathlib import Path


def get_chapter_dir(section_id: str) -> tuple[str, str]:
    """根据节号确定章节目录和章号。"""
    # 匹配节号模式：引言, 1.1.1, 2.1, 3.1 等
    if section_id == "引言":
        return "引言", "0"

    match = re.match(r"^(\d+)", section_id)
    if not match:
        raise ValueError(f"无效的节号格式: {section_id}")

    chapter_num = match.group(1)
    chapter_map = {
        "1": ("第一章_认识Agent_Skill", "1"),
        "2": ("第二章_Skill的分类与生态", "2"),
        "3": ("第三章_Agent_Skill开发实战", "3"),
    }

    if chapter_num not in chapter_map:
        raise ValueError(f"不支持的章号: {chapter_num}")

    return chapter_map[chapter_num]


def create_section_file(book_dir: Path, section_id: str, title: str, target_words: int) -> Path:
    """创建新的小节文件。"""
    chapter_dir, _ = get_chapter_dir(section_id)

    # 确定文件名
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
    if section_id == "引言":
        filename = f"00_{safe_title}.md"
    else:
        filename = f"{section_id}_{safe_title}.md"

    # 确保目录存在
    section_dir = book_dir / chapter_dir
    section_dir.mkdir(parents=True, exist_ok=True)

    file_path = section_dir / filename

    # 如果文件已存在，提示并退出
    if file_path.exists():
        print(f"⚠️ 文件已存在: {file_path}")
        print("如需重新创建，请先删除该文件。")
        return file_path

    # 创建 frontmatter
    frontmatter = f"""---
section_id: "{section_id}"
title: "{title}"
status: outline
word_count: 0
target_words: {target_words}
---

"""

    file_path.write_text(frontmatter, encoding="utf-8")
    print(f"✅ 已创建: {file_path}")
    print(f"   节号: {section_id}")
    print(f"   标题: {title}")
    print(f"   目标字数: {target_words}")

    return file_path


def update_section_map(book_dir: Path, section_id: str, title: str, filename: str, target_words: int):
    """更新 section-map.md 文件。"""
    section_map_path = book_dir / ".claude" / "skills" / "book-writer" / "references" / "section-map.md"

    if not section_map_path.exists():
        print(f"⚠️ section-map.md 不存在: {section_map_path}")
        return

    content = section_map_path.read_text(encoding="utf-8")

    # 确定章号
    if section_id == "引言":
        chapter_marker = "## 引言"
        table_row = f'| {section_id} | {title} | 引言/{filename} | - | {target_words} | - |\n'
    else:
        chapter_num = section_id.split(".")[0]
        chapter_names = {
            "1": "第一章 认识 Agent Skill",
            "2": "第二章 Skill 的分类与生态",
            "3": "第三章 Agent Skill 开发实战",
        }
        chapter_marker = f"## {chapter_names.get(chapter_num, f'第{chapter_num}章')}"

        # 获取目录名
        chapter_dir, _ = get_chapter_dir(section_id)

        # 计算组装序号（简化处理，实际应该解析现有表格）
        table_row = f'| {section_id} | {title} | {chapter_dir}/{filename} | - | {target_words} | - |\n'

    # 在对应章节表格末尾添加新行
    # 查找章节表格并添加行
    chapter_pattern = rf"({re.escape(chapter_marker)}.*?\n)(\|[-]+\|[-]+\|[-]+\|[-]+\|[-]+\|[-]+\|\n)"

    match = re.search(chapter_pattern, content, re.DOTALL)
    if match:
        # 在表头分隔行后插入新行
        insert_pos = match.end()
        new_content = content[:insert_pos] + table_row + content[insert_pos:]
        section_map_path.write_text(new_content, encoding="utf-8")
        print(f"✅ 已更新 section-map.md")
    else:
        print(f"⚠️ 未找到章节表格: {chapter_marker}")
        print("请手动更新 section-map.md")


def main():
    if len(sys.argv) < 4:
        print("用法: python init.py <书籍根目录> <节号> <标题> [目标字数]")
        print("示例: python init.py . 1.4.1 '新增小节标题' 2000")
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    section_id = sys.argv[2]
    title = sys.argv[3]
    target_words = int(sys.argv[4]) if len(sys.argv) > 4 else 1500

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    try:
        file_path = create_section_file(book_dir, section_id, title, target_words)
        update_section_map(book_dir, section_id, title, file_path.name, target_words)
        print(f"\n💡 接下来可以运行: /book-writer research {section_id}")
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
