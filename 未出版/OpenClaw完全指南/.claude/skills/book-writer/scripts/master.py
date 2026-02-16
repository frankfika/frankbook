#!/usr/bin/env python3
"""
Master Agent - 主协调Agent

职责：
- 任务分配
- 进度追踪
- 质量控制
- 协调其他Agent

用法：
    python master.py <书籍根目录> <命令> [参数]

命令：
    status              - 查看全书进度
    plan                - 生成写作计划
    assign <节号>       - 分配任务
    assemble <章号>     - 组装章节
    export              - 导出完整书籍

示例：
    python master.py . status
    python master.py . plan
    python master.py . assemble 1
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SectionInfo:
    section_id: str
    title: str
    chapter: str
    status: str
    word_count: int
    target_words: int


class MasterAgent:
    """主协调Agent - 管理全书写作流程"""

    STATUS_LABELS = {
        "outline": "📋 纲要",
        "researched": "🔍 已研究",
        "draft": "✏️ 初稿",
        "reviewed": "✅ 已审查",
        "final": "🎉 定稿",
    }

    CHAPTER_DIRS = {
        "0": "序章",
        "1": "第一部分",
        "2": "第二部分",
        "3": "第三部分",
        "4": "第四部分",
        "5": "终章",
        "6": "附录",
    }

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.skill_dir = self.book_dir / '.claude' / 'skills' / 'book-writer'

    def get_status(self) -> Dict:
        """获取全书进度状态。"""
        sections = self._scan_sections()

        stats = {
            'total': len(sections),
            'by_status': {},
            'by_chapter': {},
            'total_words': 0,
            'total_target': 0,
        }

        for s in sections:
            # 状态统计
            stats['by_status'][s.status] = stats['by_status'].get(s.status, 0) + 1

            # 章节统计
            if s.chapter not in stats['by_chapter']:
                stats['by_chapter'][s.chapter] = {
                    'count': 0,
                    'words': 0,
                    'target': 0,
                }
            stats['by_chapter'][s.chapter]['count'] += 1
            stats['by_chapter'][s.chapter]['words'] += s.word_count
            stats['by_chapter'][s.chapter]['target'] += s.target_words

            # 总字数
            stats['total_words'] += s.word_count
            stats['total_target'] += s.target_words

        return stats, sections

    def print_status(self):
        """打印进度报告。"""
        stats, sections = self.get_status()

        print("=" * 70)
        print("📚 《OpenClaw：自进化AI完全指南》写作进度报告")
        print("=" * 70)

        # 总体进度
        completed = stats['by_status'].get('reviewed', 0) + stats['by_status'].get('final', 0)
        total = stats['total']
        pct = (completed / total * 100) if total > 0 else 0

        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\n总体进度: [{bar}] {pct:.0f}% ({completed}/{total} 节完成)")
        print(f"总字数: {stats['total_words']:,} / {stats['total_target']:,} 目标字数")

        # 状态分布
        print(f"\n{'状态分布':^30}")
        print("-" * 40)
        for status, label in self.STATUS_LABELS.items():
            count = stats['by_status'].get(status, 0)
            if count > 0:
                print(f"  {label:<12} {count:>3} 节")

        # 按章节详情
        for chapter_name, cdata in sorted(stats['by_chapter'].items()):
            tw = cdata['words']
            tt = cdata['target']
            cpct = (tw / tt * 100) if tt > 0 else 0
            print(f"\n{'─' * 70}")
            print(f"📖 {chapter_name}  ({tw:,}/{tt:,} 字, {cpct:.0f}%)")
            print(f"{'─' * 70}")

            # 该章的小节
            chapter_sections = [s for s in sections if s.chapter == chapter_name]
            print(f"  {'节号':<8} {'标题':<28} {'状态':<10} {'字数':>12}")
            print(f"  {'─'*8} {'─'*28} {'─'*10} {'─'*12}")
            for s in chapter_sections[:10]:  # 最多显示10个
                status_label = self.STATUS_LABELS.get(s.status, s.status)
                title = s.title[:26] if s.title else "(无标题)"
                words = f"{s.word_count:,}/{s.target_words:,}"
                print(f"  {s.section_id:<8} {title:<28} {status_label:<10} {words:>12}")

        # 保存JSON
        self._save_progress_json(sections)

    def _scan_sections(self) -> List[SectionInfo]:
        """扫描所有章节文件。"""
        sections = []

        chapter_dirs = [
            "序章", "第一部分", "第二部分",
            "第三部分", "第四部分", "终章", "附录"
        ]

        for chapter_name in chapter_dirs:
            chapter_path = self.book_dir / chapter_name
            if not chapter_path.exists():
                continue

            for md_file in sorted(chapter_path.glob("*.md")):
                # 跳过组装后的文件
                if "_完整" in md_file.name or "_第" in md_file.name:
                    continue

                fm = self._parse_frontmatter(md_file)
                if fm:
                    sections.append(SectionInfo(
                        section_id=fm.get('section_id', '?'),
                        title=fm.get('title', md_file.stem),
                        chapter=chapter_name,
                        status=fm.get('status', 'outline'),
                        word_count=int(fm.get('word_count', 0)),
                        target_words=int(fm.get('target_words', 0)),
                    ))

        return sections

    def _parse_frontmatter(self, file_path: Path) -> Optional[Dict]:
        """解析Markdown文件的YAML frontmatter。"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return None

        import re
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        fm = {}
        for line in match.group(1).strip().split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                fm[key.strip()] = value.strip().strip('"').strip("'")
        return fm

    def _count_words(self, content: str) -> int:
        """统计字数。"""
        import re
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        return chinese_chars + english_words

    def _save_progress_json(self, sections: List[SectionInfo]):
        """保存进度到JSON文件。"""
        progress_file = self.book_dir / 'progress.json'
        data = {
            'updated_at': datetime.now().isoformat(),
            'total_sections': len(sections),
            'sections': [
                {
                    'section_id': s.section_id,
                    'title': s.title,
                    'chapter': s.chapter,
                    'status': s.status,
                    'word_count': s.word_count,
                    'target_words': s.target_words,
                }
                for s in sections
            ]
        }
        progress_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def print_plan(self):
        """打印写作计划。"""
        stats, _ = self.get_status()

        print("=" * 70)
        print("📝 《OpenClaw》写作计划")
        print("=" * 70)

        # 阶段划分
        phases = [
            ("Phase 1: 研究阶段", 'researched', "对所有章节进行NotebookLM研究"),
            ("Phase 2: 撰写阶段", 'draft', "撰写所有章节初稿"),
            ("Phase 3: 审查阶段", 'reviewed', "6维度审查所有章节"),
            ("Phase 4: 校对阶段", 'final', "责任编辑三审三校"),
        ]

        for i, (name, target_status, desc) in enumerate(phases, 1):
            completed = sum(stats['by_status'].get(s, 0) for s in ['researched', 'draft', 'reviewed', 'final'])
            if target_status == 'researched':
                completed = stats['by_status'].get('researched', 0) + stats['by_status'].get('draft', 0) + stats['by_status'].get('reviewed', 0) + stats['by_status'].get('final', 0)
            elif target_status == 'draft':
                completed = stats['by_status'].get('draft', 0) + stats['by_status'].get('reviewed', 0) + stats['by_status'].get('final', 0)
            elif target_status == 'reviewed':
                completed = stats['by_status'].get('reviewed', 0) + stats['by_status'].get('final', 0)
            elif target_status == 'final':
                completed = stats['by_status'].get('final', 0)

            total = stats['total']
            pct = (completed / total * 100) if total > 0 else 0

            status_icon = "✅" if pct >= 100 else "🔄" if pct > 0 else "⏳"
            print(f"\n{status_icon} {name}")
            print(f"   进度: {completed}/{total} ({pct:.0f}%)")
            print(f"   说明: {desc}")

            # 推荐并行策略
            if pct < 100:
                if target_status == 'researched':
                    print(f"   建议: python batch.py . research part1 --parallel=5")
                elif target_status == 'draft':
                    print(f"   建议: python batch.py . write part1 --parallel=3")
                elif target_status == 'reviewed':
                    print(f"   建议: python batch.py . review all --parallel=5")

        # 下一阶段建议
        print("\n" + "=" * 70)
        print("💡 下一步行动建议")
        print("=" * 70)

        outline_count = stats['by_status'].get('outline', 0)
        researched_count = stats['by_status'].get('researched', 0)
        draft_count = stats['by_status'].get('draft', 0)
        reviewed_count = stats['by_status'].get('reviewed', 0)

        if outline_count > 0:
            print(f"1. 先完成研究阶段: {outline_count} 个章节待研究")
            print(f"   命令: python batch.py . research all --parallel=5")
        elif researched_count > 0:
            print(f"1. 进入撰写阶段: {researched_count} 个章节待撰写")
            print(f"   命令: python batch.py . write all --parallel=3")
        elif draft_count > 0:
            print(f"1. 进入审查阶段: {draft_count} 个章节待审查")
            print(f"   命令: python batch.py . review all --parallel=5")
        elif reviewed_count > 0:
            print(f"1. 进入校对阶段: {reviewed_count} 个章节待校对")
            print(f"   命令: python batch.py . proofread all --parallel=3")
        else:
            print("1. ✅ 所有章节已完成！可以导出PDF了")
            print(f"   命令: python master.py . export")

    def assemble_chapter(self, chapter_num: str):
        """组装指定章节。"""
        chapter_name = self.CHAPTER_DIRS.get(chapter_num)
        if not chapter_name:
            print(f"错误: 无效的章号 {chapter_num}")
            print(f"有效章号: {', '.join(self.CHAPTER_DIRS.keys())}")
            return False

        chapter_path = self.book_dir / chapter_name
        if not chapter_path.exists():
            print(f"错误: 章节目录不存在 {chapter_path}")
            return False

        print(f"📦 正在组装: {chapter_name}")

        # 收集所有小节
        sections = []
        for md_file in sorted(chapter_path.glob("*.md")):
            if "_完整" in md_file.name or "_第" in md_file.name:
                continue

            content = md_file.read_text(encoding='utf-8')
            fm = self._parse_frontmatter(md_file)

            if fm:
                sections.append({
                    'file': md_file,
                    'section_id': fm.get('section_id', '?'),
                    'title': fm.get('title', md_file.stem),
                    'content': content,
                })

        if not sections:
            print("  未找到小节文件")
            return False

        # 生成组装后的文件
        output_name = f"{chapter_name}_完整.md"
        output_path = chapter_path / output_name

        lines = [
            f"# {chapter_name}",
            "",
            f"> 组装时间: {datetime.now().isoformat()}",
            f"> 小节数: {len(sections)}",
            "",
            "---",
            "",
        ]

        for s in sections:
            # 移除frontmatter，保留正文
            content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', s['content'], flags=re.DOTALL)
            lines.append(f"## {s['section_id']} {s['title']}")
            lines.append("")
            lines.append(content.strip())
            lines.append("")
            lines.append("---")
            lines.append("")

        output_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"  ✅ 已组装: {output_path}")
        print(f"  包含 {len(sections)} 个小节")
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

    agent = MasterAgent(book_dir)

    if command == 'status':
        agent.print_status()
    elif command == 'plan':
        agent.print_plan()
    elif command == 'assemble':
        if len(sys.argv) < 4:
            print("用法: master.py <目录> assemble <章号>")
            print(f"章号: 0=序章, 1=第一部分, 2=第二部分, ...")
            sys.exit(1)
        chapter_num = sys.argv[3]
        agent.assemble_chapter(chapter_num)
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    import re
    main()
