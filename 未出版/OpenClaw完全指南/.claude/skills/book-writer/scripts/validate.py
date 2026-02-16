#!/usr/bin/env python3
"""
内容验证工具

对照纲要检查各小节的内容完整度、字数、状态。

用法：
    python validate.py <书籍根目录> [节号]

不指定节号则验证全部小节。
"""

import sys
import re
from pathlib import Path


def parse_frontmatter(file_path):
    """解析 YAML frontmatter。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None, ""

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content

    frontmatter = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value

    return frontmatter, match.group(2)


def count_words(text):
    """统计字数。"""
    text = text.strip()
    if not text:
        return 0
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english = len(re.findall(r"[a-zA-Z]+", text))
    return chinese + english


def validate_section(file_path):
    """验证单个小节，返回问题列表。"""
    issues = []

    if not file_path.exists():
        return [("ERROR", "文件不存在")]

    fm, body = parse_frontmatter(file_path)

    if fm is None:
        issues.append(("WARN", "缺少 YAML frontmatter"))
        return issues

    # 检查必要的 frontmatter 字段
    required_fields = ["section_id", "title", "status", "target_words"]
    for field in required_fields:
        if field not in fm:
            issues.append(("WARN", f"frontmatter 缺少字段: {field}"))

    # 检查状态
    status = fm.get("status", "outline")
    valid_statuses = ["outline", "researched", "draft", "reviewed", "final"]
    if status not in valid_statuses:
        issues.append(("ERROR", f"无效状态: {status}，有效值: {', '.join(valid_statuses)}"))

    # 检查字数
    target = int(fm.get("target_words", 0))
    actual = count_words(body)

    if status in ("draft", "reviewed", "final"):
        if actual == 0:
            issues.append(("ERROR", f"状态为 {status} 但正文为空"))
        elif target > 0:
            ratio = actual / target
            if ratio < 0.5:
                issues.append(("WARN", f"字数严重不足: {actual}/{target} ({ratio:.0%})"))
            elif ratio < 0.8:
                issues.append(("INFO", f"字数偏少: {actual}/{target} ({ratio:.0%})"))
            elif ratio > 1.5:
                issues.append(("INFO", f"字数偏多: {actual}/{target} ({ratio:.0%})"))

    # 检查内容质量标记
    if status in ("draft", "reviewed", "final"):
        # 检查是否有代码示例（对技术章节）
        section_id = fm.get("section_id", "")
        if section_id.startswith(("1.2", "2.")):
            if "```" not in body:
                issues.append(("INFO", "技术章节建议包含代码示例"))

        # 检查是否有禁忌表达
        forbidden = ["本节将介绍", "综上所述", "众所周知", "毋庸置疑", "一言以蔽之"]
        for phrase in forbidden:
            if phrase in body:
                issues.append(("WARN", f"包含禁忌表达: '{phrase}'"))

    if not issues:
        issues.append(("OK", "验证通过"))

    return issues


def find_all_sections(book_dir):
    """查找所有小节文件。"""
    chapter_dirs = [
        "引言",
        "第一章_认识Agent_Skill",
        "第二章_Skill的分类与生态",
        "第三章_Agent_Skill开发实战",
    ]

    sections = []
    for chapter_name in chapter_dirs:
        chapter_path = book_dir / chapter_name
        if not chapter_path.exists():
            continue
        for md_file in sorted(chapter_path.glob("*.md")):
            if md_file.name.endswith("_完整.md"):
                continue
            sections.append(md_file)
    return sections


def main():
    if len(sys.argv) < 2:
        print("用法: python validate.py <书籍根目录> [节号]")
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    target_section = sys.argv[2] if len(sys.argv) > 2 else None

    if target_section:
        # 验证指定小节
        sections = find_all_sections(book_dir)
        found = False
        for sf in sections:
            fm, _ = parse_frontmatter(sf)
            if fm and fm.get("section_id") == target_section:
                found = True
                print(f"\n🔍 验证: {sf.name}")
                issues = validate_section(sf)
                for level, msg in issues:
                    icon = {"OK": "✅", "INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌"}.get(level, "?")
                    print(f"  {icon} [{level}] {msg}")
                break
        if not found:
            print(f"未找到节号为 {target_section} 的文件")
    else:
        # 验证全部
        sections = find_all_sections(book_dir)
        if not sections:
            print("未找到章节文件")
            sys.exit(1)

        error_count = 0
        warn_count = 0
        ok_count = 0

        print("=" * 60)
        print("📋 全书内容验证报告")
        print("=" * 60)

        for sf in sections:
            issues = validate_section(sf)
            has_problems = any(level in ("ERROR", "WARN") for level, _ in issues)

            if has_problems:
                print(f"\n📄 {sf.name}")
                for level, msg in issues:
                    if level in ("ERROR", "WARN", "INFO"):
                        icon = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌"}.get(level)
                        print(f"  {icon} [{level}] {msg}")
                        if level == "ERROR":
                            error_count += 1
                        elif level == "WARN":
                            warn_count += 1
            else:
                ok_count += 1

        print(f"\n{'─' * 60}")
        print(f"验证结果: ✅ {ok_count} 通过 | ⚠️ {warn_count} 警告 | ❌ {error_count} 错误")
        print(f"共验证 {len(sections)} 个文件")


if __name__ == "__main__":
    main()
