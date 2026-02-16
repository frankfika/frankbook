#!/usr/bin/env python3
"""
书籍写作进度追踪工具

扫描所有章节文件，读取 YAML frontmatter，生成进度报告。

用法：
    python progress.py <书籍根目录>
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict

STATUS_LABELS = {
    "outline": "📋 纲要",
    "researched": "🔍 已研究",
    "draft": "✏️ 初稿",
    "reviewed": "✅ 已审查",
    "final": "🎉 定稿",
}

STATUS_ORDER = ["outline", "researched", "draft", "reviewed", "final"]


def parse_frontmatter(file_path):
    """解析 Markdown 文件的 YAML frontmatter。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None

    frontmatter = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value

    return frontmatter


def count_words(file_path):
    """统计 Markdown 文件的正文字数（排除 frontmatter）。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return 0

    # 移除 frontmatter
    content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)

    # 移除空行和纯空白
    content = content.strip()
    if not content:
        return 0

    # 中文字符数 + 英文单词数
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", content))
    english_words = len(re.findall(r"[a-zA-Z]+", content))
    return chinese_chars + english_words


def find_section_files(book_dir):
    """查找所有章节小节文件。"""
    sections = []
    chapter_dirs = [
        "序章",
        "第一部分",
        "第二部分",
        "第三部分",
        "第四部分",
        "终章",
        "附录",
    ]

    for chapter_name in chapter_dirs:
        chapter_path = book_dir / chapter_name
        if not chapter_path.exists():
            continue

        for md_file in sorted(chapter_path.glob("*.md")):
            # 跳过组装后的完整章节文件（如 第1章_核心框架.md）
            if "_完整.md" in md_file.name or "_第" in md_file.name:
                continue
            sections.append((chapter_name, md_file))

    return sections


def generate_progress_report(book_dir):
    """生成进度报告。"""
    book_path = Path(book_dir)
    sections = find_section_files(book_path)

    if not sections:
        print(f"未找到章节文件。请检查目录: {book_path}")
        return

    # 统计数据
    stats = defaultdict(lambda: {"count": 0, "words": 0, "target": 0})
    chapter_stats = defaultdict(lambda: {"sections": [], "total_words": 0, "total_target": 0})
    all_sections = []

    for chapter_name, file_path in sections:
        fm = parse_frontmatter(file_path)
        actual_words = count_words(file_path)

        section_info = {
            "chapter": chapter_name,
            "file": file_path.name,
            "section_id": fm.get("section_id", "?") if fm else "?",
            "title": fm.get("title", file_path.stem) if fm else file_path.stem,
            "status": fm.get("status", "outline") if fm else "outline",
            "target_words": int(fm.get("target_words", 0)) if fm else 0,
            "actual_words": actual_words,
        }

        all_sections.append(section_info)
        status = section_info["status"]
        stats[status]["count"] += 1
        stats[status]["words"] += actual_words

        chapter_stats[chapter_name]["sections"].append(section_info)
        chapter_stats[chapter_name]["total_words"] += actual_words
        chapter_stats[chapter_name]["total_target"] += section_info["target_words"]

    # 输出报告
    total = len(all_sections)
    completed = sum(1 for s in all_sections if s["status"] in ("reviewed", "final"))
    total_words = sum(s["actual_words"] for s in all_sections)
    total_target = sum(s["target_words"] for s in all_sections)

    print("=" * 70)
    print("📚 《OpenClaw：自进化AI完全指南》写作进度报告")
    print("=" * 70)

    # 总体进度
    pct = (completed / total * 100) if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\n总体进度: [{bar}] {pct:.0f}% ({completed}/{total} 节完成)")
    print(f"总字数: {total_words:,} / {total_target:,} 目标字数")

    # 状态分布
    print(f"\n{'状态分布':^30}")
    print("-" * 40)
    for status in STATUS_ORDER:
        count = stats[status]["count"]
        label = STATUS_LABELS.get(status, status)
        if count > 0:
            print(f"  {label:<12} {count:>3} 节")

    # 按章节详情
    for chapter_name, cdata in chapter_stats.items():
        tw = cdata["total_words"]
        tt = cdata["total_target"]
        cpct = (tw / tt * 100) if tt > 0 else 0
        print(f"\n{'─' * 70}")
        print(f"📖 {chapter_name}  ({tw:,}/{tt:,} 字, {cpct:.0f}%)")
        print(f"{'─' * 70}")
        print(f"  {'节号':<8} {'标题':<28} {'状态':<10} {'字数':>8}")
        print(f"  {'─'*8} {'─'*28} {'─'*10} {'─'*8}")

        for s in cdata["sections"]:
            sid = s["section_id"]
            title = s["title"][:26]
            status_label = STATUS_LABELS.get(s["status"], s["status"])
            words = f"{s['actual_words']:,}/{s['target_words']:,}"
            print(f"  {sid:<8} {title:<28} {status_label:<10} {words:>12}")

    # 保存 JSON 进度文件
    progress_file = book_path / "progress.json"
    progress_data = {
        "total_sections": total,
        "completed_sections": completed,
        "total_words": total_words,
        "total_target": total_target,
        "sections": all_sections,
    }
    try:
        progress_file.write_text(json.dumps(progress_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n💾 进度数据已保存到: {progress_file}")
    except Exception as e:
        print(f"\n⚠️ 保存进度文件失败: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python progress.py <书籍根目录>")
        sys.exit(1)

    generate_progress_report(sys.argv[1])
