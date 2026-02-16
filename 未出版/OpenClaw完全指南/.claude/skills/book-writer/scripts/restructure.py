#!/usr/bin/env python3
"""
目录重组工具

支持调整章节顺序、合并/拆分小节、新增/删除章节。

用法：
    python restructure.py <书籍根目录> <命令> [参数]

命令：
    move <节号> <新节号>     - 移动/重命名小节
    swap <节号1> <节号2>     - 交换两个小节的位置
    insert <节号> <标题>     - 在指定位置插入新小节
    delete <节号>            - 删除小节
    list                     - 列出所有小节

示例：
    python restructure.py . move 1.2.5 1.3.1
    python restructure.py . swap 2.1 2.2
    python restructure.py . insert 1.1.4 "新增小节标题"
    python restructure.py . delete 1.1.4
    python restructure.py . list
"""

import sys
import re
import shutil
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Section:
    """章节数据结构"""
    section_id: str
    title: str
    file_path: Path
    chapter: str


def get_chapter_info(section_id: str) -> tuple[str, str]:
    """根据节号获取章节目录和名称。"""
    if section_id == "引言":
        return "引言", "引言"

    match = re.match(r"^(\d+)", section_id)
    if not match:
        raise ValueError(f"无效的节号: {section_id}")

    chapter_num = match.group(1)
    chapter_map = {
        "1": ("第一章_认识Agent_Skill", "第一章 认识 Agent Skill"),
        "2": ("第二章_Skill的分类与生态", "第二章 Skill 的分类与生态"),
        "3": ("第三章_Agent_Skill开发实战", "第三章 Agent Skill 开发实战"),
    }

    return chapter_map.get(chapter_num, (f"第{chapter_num}章", f"第{chapter_num}章"))


def parse_section_filename(filename: str) -> tuple[str, str]:
    """从文件名解析节号和标题。"""
    # 移除 .md 后缀
    name = filename.replace(".md", "")

    # 尝试匹配节号模式 (00_, 1.1.1_, 2.1_)
    match = re.match(r"^(\d+(?:\.\d+)*|00)_(.+)$", name)
    if match:
        section_id = match.group(1)
        if section_id == "00":
            section_id = "引言"
        title = match.group(2).replace("_", " ")
        return section_id, title

    return "", name


def find_all_sections(book_dir: Path) -> list[Section]:
    """查找所有小节。"""
    sections = []
    chapter_dirs = [
        "引言",
        "第一章_认识Agent_Skill",
        "第二章_Skill的分类与生态",
        "第三章_Agent_Skill开发实战",
    ]

    for chapter_dir in chapter_dirs:
        chapter_path = book_dir / chapter_dir
        if not chapter_path.exists():
            continue

        for md_file in sorted(chapter_path.glob("*.md")):
            if md_file.name.endswith("_完整.md"):
                continue

            section_id, title = parse_section_filename(md_file.name)
            if section_id:
                sections.append(Section(
                    section_id=section_id,
                    title=title,
                    file_path=md_file,
                    chapter=chapter_dir
                ))

    return sections


def read_section_map(book_dir: Path) -> str:
    """读取 section-map.md 内容。"""
    map_path = book_dir / ".claude" / "skills" / "book-writer" / "references" / "section-map.md"
    if map_path.exists():
        return map_path.read_text(encoding="utf-8")
    return ""


def write_section_map(book_dir: Path, content: str):
    """写入 section-map.md。"""
    map_path = book_dir / ".claude" / "skills" / "book-writer" / "references" / "section-map.md"
    map_path.write_text(content, encoding="utf-8")


def cmd_list(book_dir: Path):
    """列出所有小节。"""
    sections = find_all_sections(book_dir)

    print("=" * 70)
    print("📚 当前书籍结构")
    print("=" * 70)

    current_chapter = ""
    for sec in sections:
        if sec.chapter != current_chapter:
            current_chapter = sec.chapter
            print(f"\n📁 {current_chapter}")
            print("-" * 50)

        print(f"  {sec.section_id:<10} {sec.title}")

    print(f"\n共 {len(sections)} 个小节")


def cmd_move(book_dir: Path, old_id: str, new_id: str):
    """移动/重命名小节。"""
    sections = find_all_sections(book_dir)

    # 查找源小节
    source = None
    for sec in sections:
        if sec.section_id == old_id:
            source = sec
            break

    if not source:
        print(f"❌ 未找到小节: {old_id}")
        return False

    # 检查目标是否已存在
    for sec in sections:
        if sec.section_id == new_id:
            print(f"❌ 目标节号已存在: {new_id}")
            return False

    # 确定新路径
    new_chapter_dir, _ = get_chapter_info(new_id)
    new_chapter_path = book_dir / new_chapter_dir
    new_chapter_path.mkdir(parents=True, exist_ok=True)

    # 生成新文件名
    safe_title = re.sub(r'[\\/*?:"<>|]', "", source.title).replace(" ", "_")
    if new_id == "引言":
        new_filename = f"00_{safe_title}.md"
    else:
        new_filename = f"{new_id}_{safe_title}.md"

    new_file_path = new_chapter_path / new_filename

    # 移动文件
    shutil.move(str(source.file_path), str(new_file_path))
    print(f"✅ 已移动: {source.file_path.name} -> {new_filename}")

    # 更新文件内的 section_id
    content = new_file_path.read_text(encoding="utf-8")
    content = re.sub(
        r'^section_id:\s*"[^"]*"',
        f'section_id: "{new_id}"',
        content,
        flags=re.MULTILINE
    )
    new_file_path.write_text(content, encoding="utf-8")
    print(f"✅ 已更新文件内的 section_id")

    # 更新 section-map.md
    map_content = read_section_map(book_dir)
    if map_content:
        # 替换节号
        map_content = re.sub(
            rf'\| {re.escape(old_id)} \|',
            f'| {new_id} |',
            map_content
        )
        # 更新文件路径
        old_rel_path = str(source.file_path.relative_to(book_dir)).replace("\\", "/")
        new_rel_path = str(new_file_path.relative_to(book_dir)).replace("\\", "/")
        map_content = map_content.replace(old_rel_path, new_rel_path)

        write_section_map(book_dir, map_content)
        print(f"✅ 已更新 section-map.md")

    print(f"\n💡 如果研究笔记存在，请手动重命名: assets/research/{old_id}_research.md")

    return True


def cmd_swap(book_dir: Path, id1: str, id2: str):
    """交换两个小节的位置（临时互换节号）。"""
    # 实际实现：先移动第一个到临时ID，再移动第二个到第一个的ID，最后移动临时ID到第二个的ID
    temp_id = f"_temp_{id1}"

    print(f"🔄 交换 {id1} 和 {id2}...")

    if cmd_move(book_dir, id1, temp_id):
        if cmd_move(book_dir, id2, id1):
            if cmd_move(book_dir, temp_id, id2):
                print(f"✅ 交换完成")
                return True
            else:
                print(f"⚠️ 交换失败，请检查状态")
                return False
    return False


def cmd_delete(book_dir: Path, section_id: str):
    """删除小节。"""
    sections = find_all_sections(book_dir)

    target = None
    for sec in sections:
        if sec.section_id == section_id:
            target = sec
            break

    if not target:
        print(f"❌ 未找到小节: {section_id}")
        return False

    # 确认
    print(f"⚠️ 将要删除: {target.file_path}")
    print(f"   标题: {target.title}")
    response = input("确认删除? (y/N): ")

    if response.lower() != 'y':
        print("已取消")
        return False

    # 删除文件
    target.file_path.unlink()
    print(f"✅ 已删除文件: {target.file_path.name}")

    # 从 section-map.md 中移除
    map_content = read_section_map(book_dir)
    if map_content:
        # 删除该行
        lines = map_content.split('\n')
        new_lines = []
        for line in lines:
            if f"| {section_id} |" not in line:
                new_lines.append(line)
        write_section_map(book_dir, '\n'.join(new_lines))
        print(f"✅ 已更新 section-map.md")

    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    command = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    if command == "list":
        cmd_list(book_dir)
    elif command == "move":
        if len(sys.argv) < 5:
            print("用法: restructure.py <目录> move <旧节号> <新节号>")
            sys.exit(1)
        cmd_move(book_dir, sys.argv[3], sys.argv[4])
    elif command == "swap":
        if len(sys.argv) < 5:
            print("用法: restructure.py <目录> swap <节号1> <节号2>")
            sys.exit(1)
        cmd_swap(book_dir, sys.argv[3], sys.argv[4])
    elif command == "delete":
        if len(sys.argv) < 4:
            print("用法: restructure.py <目录> delete <节号>")
            sys.exit(1)
        cmd_delete(book_dir, sys.argv[3])
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
