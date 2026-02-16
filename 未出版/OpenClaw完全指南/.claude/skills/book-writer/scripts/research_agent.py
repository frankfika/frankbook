#!/usr/bin/env python3
"""
Research Agent - 研究专用Agent

职责：
- 读取研究主题清单
- 使用NotebookLM查询资料
- 整理研究笔记
- 标注信息来源

用法：
    python research_agent.py <书籍根目录> <节号>

示例：
    python research_agent.py . 1.1
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class ResearchAgent:
    """研究Agent - 使用NotebookLM查询资料"""

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.research_dir = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'assets' / 'research'
        self.research_dir.mkdir(parents=True, exist_ok=True)

    def research(self, section_id: str) -> bool:
        """
        对指定小节进行研究。

        Args:
            section_id: 小节编号，如 "1.1"

        Returns:
            研究是否成功
        """
        print(f"🔍 ResearchAgent: 开始研究 {section_id}")

        try:
            # 1. 获取研究主题
            topics = self._get_research_topics(section_id)
            print(f"   研究主题: {len(topics)} 个")

            # 2. 获取纲要描述
            outline = self._get_outline(section_id)

            # 3. 执行NotebookLM查询（实际使用时通过skill调用）
            research_data = self._query_notebooklm(section_id, topics, outline)

            # 4. 生成研究笔记
            research_file = self.research_dir / f"{section_id}_research.md"
            research_file.write_text(research_data, encoding='utf-8')

            # 5. 更新小节状态
            self._update_section_status(section_id, 'researched')

            print(f"✅ ResearchAgent: 完成研究 {section_id}")
            print(f"   研究笔记: {research_file}")
            return True

        except Exception as e:
            print(f"❌ ResearchAgent: 研究失败 {section_id} - {e}")
            return False

    def _get_research_topics(self, section_id: str) -> List[str]:
        """从research-topics.md获取研究主题。"""
        topics_file = (self.book_dir / '.claude' / 'skills' / 'book-writer' /
                      'references' / 'research-topics.md')

        if not topics_file.exists():
            return [f"{section_id} 相关主题"]

        content = topics_file.read_text(encoding='utf-8')

        # 查找该节的主题列表
        # 格式: "1.1 主题名称" 或 "## 1.1"
        patterns = [
            rf"{section_id.replace('.', r'\.')}[.\s:]+(.+?)(?=\n\d|\Z)",
            rf"##?\s*{section_id.replace('.', r'\.')}[.\s\n]+(.+?)(?=\n##?|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_content = match.group(1)
                # 提取列表项
                topics = []
                for line in section_content.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line):
                        topic = re.sub(r'^[-*\d.\s]+', '', line)
                        if topic:
                            topics.append(topic)
                return topics or [f"{section_id} 相关主题"]

        return [f"{section_id} 相关主题"]

    def _get_outline(self, section_id: str) -> str:
        """从outline.md获取纲要描述。"""
        outline_file = (self.book_dir / '.claude' / 'skills' / 'book-writer' /
                       'references' / 'outline.md')

        if not outline_file.exists():
            return ""

        content = outline_file.read_text(encoding='utf-8')

        # 查找该节的纲要
        pattern = rf"{section_id.replace('.', r'\.')}[.\s:]+(.+?)(?=\n\d\.\d|\Z)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()
        return ""

    def _query_notebooklm(self, section_id: str, topics: List[str], outline: str) -> str:
        """
        生成研究笔记框架。

        注意：实际的NotebookLM查询通过 /notebooklm skill 执行。
        此Agent脚本负责整理查询结果。
        """
        lines = [
            f"# {section_id} 研究笔记",
            "",
            f"生成时间: {datetime.now().isoformat()}",
            f"Agent: ResearchAgent",
            "",
            "## 研究主题",
            "",
        ]

        for topic in topics:
            lines.append(f"- {topic}")

        lines.extend([
            "",
            "## 纲要要求",
            "",
            outline if outline else "（待补充）",
            "",
            "## NotebookLM查询结果",
            "",
            "> 注：实际查询请使用 `/notebooklm` skill",
            ">",
            "> 示例查询：",
        ])

        for topic in topics[:3]:  # 前3个主题作为示例
            lines.append(f"> - {topic}")

        lines.extend([
            "",
            "## 关键资料",
            "",
            "### 来源1：",
            "- 文档：",
            "- 关键信息：",
            "- 引用位置：",
            "",
            "### 来源2：",
            "- 文档：",
            "- 关键信息：",
            "- 引用位置：",
            "",
            "## 写作建议",
            "",
            "- 重点强调：",
            "- 案例选择：",
            "- 数据引用：",
            "",
        ])

        return '\n'.join(lines)

    def _update_section_status(self, section_id: str, status: str):
        """更新小节文件的状态。"""
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            content = section_file.read_text(encoding='utf-8')
            content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            section_file.write_text(content, encoding='utf-8')

    def _find_section_file(self, section_id: str) -> Optional[Path]:
        """查找小节文件路径。"""
        chapter_dirs = [
            "序章", "第一部分", "第二部分", "第三部分", "第四部分", "终章", "附录"
        ]
        for chapter_name in chapter_dirs:
            chapter_path = self.book_dir / chapter_name
            if chapter_path.exists():
                for md_file in chapter_path.glob("*.md"):
                    if section_id in md_file.name:
                        return md_file
        return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    section_id = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    agent = ResearchAgent(book_dir)
    success = agent.research(section_id)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
