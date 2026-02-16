#!/usr/bin/env python3
"""
批量更新章节文件的目标字数

用法：
    python update_targets.py <书籍根目录>
"""

import sys
import re
from pathlib import Path

# 新的目标字数映射（从 section-map.md 提取）
TARGET_WORDS = {
    # 引言
    "00_引言.md": 2500,
    # 第一章
    "1.1.1_重复性工作的痛点.md": 3500,
    "1.1.2_知识和经验的碎片化.md": 3500,
    "1.1.3_提示词管理的困境.md": 3500,
    "1.2.1_从Prompt到Skill.md": 4500,
    "1.2.2_Claude_Code与Skill的发展历程.md": 4500,
    "1.2.3_Progressive_Disclosure架构原理.md": 4500,
    "1.2.4_Skill_MCP_Subagents_Command的对比.md": 4500,
    "2.1_核心组成架构.md": 3500,
    "2.2.1_文件结构.md": 2500,
    "2.2.2_核心字段.md": 2500,
    "2.2.3_触发与权限控制.md": 2500,
    "2.2.4_高级配置.md": 2500,
    "2.2.5_Markdown正文.md": 2500,
    "2.2.6_确定性与创造性分离.md": 2500,
    "2.2.7_验证闭环设计.md": 2500,
    "2.3.1_scripts目录.md": 2500,
    "2.3.2_references按需加载.md": 2500,
    "2.3.3_扁平化引用结构.md": 2500,
    # 第二章
    "3.1_Skill_Creator.md": 2000,
    "3.2_Document_Skills.md": 2000,
    "3.3_Image_Skills.md": 2000,
    "3.4_Git_Skills.md": 2000,
    "3.5_PPTX_Generator.md": 2000,
    "3.6_PDF_Toolkit.md": 2000,
    "3.7_WebApp_Testing.md": 2000,
    "4.1_Codebase_Visualizer.md": 2500,
    "4.2_Database_Query.md": 2500,
    "4.3_Content_Generator.md": 2500,
    "4.4_Testing_Helper.md": 2500,
    "4.5_Superpowers.md": 2500,
    "4.6_X_Article_Publisher.md": 2500,
    "4.7_NotebookLM_Bridge.md": 2500,
    "4.8_Obsidian_Skills.md": 2500,
    # 第三章
    "1.1_为什么是GitHub.md": 4000,
    "1.2_完整工作流.md": 4000,
    "1.3_视频下载Skill实战.md": 5000,
    "2.1_OPC_AI_Skill三角关系.md": 4000,
    "2.2_OPC的典型工作流.md": 4000,
    "2.3_游戏存档模式.md": 4000,
    "2.4_构建Skills军团.md": 4000,
    "2.5_常见陷阱.md": 3000,
}


def update_frontmatter(file_path, new_target):
    """更新文件的 target_words 字段。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  读取失败: {e}")
        return False

    # 检查是否有 frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        print(f"  无 frontmatter，跳过")
        return False

    # 替换 target_words
    new_content = re.sub(
        r"^target_words:\s*\d+",
        f"target_words: {new_target}",
        content,
        flags=re.MULTILINE
    )

    if new_content == content:
        print(f"  无需更新")
        return True

    try:
        file_path.write_text(new_content, encoding="utf-8")
        print(f"  更新为 {new_target} 字")
        return True
    except Exception as e:
        print(f"  写入失败: {e}")
        return False


def main(book_dir):
    book_path = Path(book_dir)
    chapter_dirs = [
        "引言",
        "第一章_认识Agent_Skill",
        "第二章_Skill的分类与生态",
        "第三章_Agent_Skill开发实战",
    ]

    updated = 0
    skipped = 0

    for chapter_name in chapter_dirs:
        chapter_path = book_path / chapter_name
        if not chapter_path.exists():
            print(f"目录不存在: {chapter_path}")
            continue

        print(f"\n📁 {chapter_name}")
        for md_file in sorted(chapter_path.glob("*.md")):
            if md_file.name.endswith("_完整.md"):
                continue

            target = TARGET_WORDS.get(md_file.name)
            if target is None:
                print(f"  ⚠️ {md_file.name}: 未找到目标字数配置")
                skipped += 1
                continue

            print(f"  {md_file.name}:", end=" ")
            if update_frontmatter(md_file, target):
                updated += 1
            else:
                skipped += 1

    print(f"\n{'='*50}")
    print(f"✅ 更新完成: {updated} 个文件")
    print(f"⏭️ 跳过: {skipped} 个文件")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python update_targets.py <书籍根目录>")
        sys.exit(1)
    main(sys.argv[1])
