#!/usr/bin/env python3
"""
Writing Agent - 写作专用Agent

职责：
- 读取纲要 + 研究笔记
- 撰写章节正文
- 确保风格统一
- 处理章节衔接

用法：
    python writing_agent.py <书籍根目录> <节号>

示例：
    python writing_agent.py . 1.1
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class WritingAgent:
    """写作Agent - 撰写章节内容"""

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.skill_dir = self.book_dir / '.claude' / 'skills' / 'book-writer'

    def write(self, section_id: str) -> bool:
        """
        撰写指定小节。

        Args:
            section_id: 小节编号，如 "1.1"

        Returns:
            写作是否成功
        """
        print(f"✏️ WritingAgent: 开始撰写 {section_id}")

        try:
            # 1. 加载研究笔记
            research = self._load_research(section_id)
            if research:
                print(f"   已加载研究笔记")

            # 2. 加载纲要
            outline = self._get_outline(section_id)
            print(f"   已加载纲要")

            # 3. 加载风格指南
            style_guide = self._load_style_guide()

            # 4. 查找前一节内容（用于衔接）
            prev_content = self._get_previous_section_content(section_id)

            # 5. 撰写内容
            content = self._compose_content(section_id, outline, research, style_guide, prev_content)

            # 6. 写入文件
            section_file = self._find_section_file(section_id)
            if not section_file:
                # 创建新文件
                section_file = self._create_section_file(section_id)

            section_file.write_text(content, encoding='utf-8')

            # 7. 更新状态
            word_count = self._count_words(content)
            self._update_frontmatter(section_file, {
                'status': 'draft',
                'word_count': word_count,
                'updated_at': datetime.now().isoformat(),
                'written_by': 'WritingAgent'
            })

            print(f"✅ WritingAgent: 完成撰写 {section_id}")
            print(f"   字数: {word_count}")
            print(f"   文件: {section_file}")
            return True

        except Exception as e:
            print(f"❌ WritingAgent: 撰写失败 {section_id} - {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_research(self, section_id: str) -> str:
        """加载研究笔记。"""
        research_file = self.skill_dir / 'assets' / 'research' / f"{section_id}_research.md"
        if research_file.exists():
            return research_file.read_text(encoding='utf-8')
        return ""

    def _get_outline(self, section_id: str) -> str:
        """从outline.md获取纲要。"""
        outline_file = self.skill_dir / 'references' / 'outline.md'

        if not outline_file.exists():
            return ""

        content = outline_file.read_text(encoding='utf-8')

        # 查找该节的详细描述
        patterns = [
            rf"{section_id.replace('.', r'\.')}[.\s:]+(.+?)(?=\n\d\.\d|\Z)",
            rf"###?\s*{section_id.replace('.', r'\.')}[.\s\n]+(.+?)(?=\n###?|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""

    def _load_style_guide(self) -> Dict[str, Any]:
        """加载风格指南。"""
        style_file = self.skill_dir / 'references' / 'style-guide.md'

        if not style_file.exists():
            return {}

        content = style_file.read_text(encoding='utf-8')

        # 解析关键风格要求
        guide = {
            'tone': '对话式、深入浅出',
            'avoid': ['学术腔', '综上所述', '本节将介绍'],
            'structure': ['痛点开头', '场景化', '代码示例', '小结过渡'],
        }

        return guide

    def _get_previous_section_content(self, section_id: str) -> str:
        """获取前一节的内容摘要（用于衔接）。"""
        # 解析节号
        parts = section_id.split('.')
        if len(parts) != 2:
            return ""

        chapter, section = int(parts[0]), int(parts[1])

        if section > 1:
            prev_id = f"{chapter}.{section - 1}"
        else:
            # 前一章的最后一节
            prev_id = f"{chapter - 1}.9"  # 假设最多9节

        prev_file = self._find_section_file(prev_id)
        if prev_file and prev_file.exists():
            content = prev_file.read_text(encoding='utf-8')
            # 提取小结部分
            match = re.search(r'##?\s*小结.*?(?=##?|$)', content, re.DOTALL)
            if match:
                return match.group(0)[:500]  # 前500字符
        return ""

    def _compose_content(self, section_id: str, outline: str, research: str,
                        style_guide: Dict, prev_content: str) -> str:
        """
        撰写章节内容。

        实际写作由AI完成，此函数准备写作上下文。
        """
        # 获取目标字数
        target_words = self._get_target_words(section_id)

        # 解析小节标题
        title = self._extract_title(outline) or f"第{section_id}节"

        content = f"""---
section_id: {section_id}
title: {title}
status: draft
target_words: {target_words}
word_count: 0
updated_at: {datetime.now().isoformat()}
written_by: WritingAgent
---

# {title}

## 引言

（此处撰写引言，以痛点/钩子开头，抓住读者注意力）

## 正文

（根据纲要撰写正文内容）

### 纲要要点
{outline}

### 研究资料
{research[:1000] if research else '（待补充研究资料）'}

## 小结

（总结本节要点，自然过渡到下一节）
"""
        return content

    def _get_target_words(self, section_id: str) -> int:
        """获取目标字数。"""
        section_map = self.skill_dir / 'references' / 'section-map.md'
        if section_map.exists():
            content = section_map.read_text(encoding='utf-8')
            # 查找该节的目标字数
            pattern = rf"{section_id.replace('.', r'\.')}.*?(\d+)\s*字"
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))
        return 3000  # 默认值

    def _extract_title(self, outline: str) -> str:
        """从纲要提取标题。"""
        # 纲要第一行通常是标题
        lines = outline.strip().split('\n')
        if lines:
            title = lines[0].strip()
            # 去除编号前缀
            title = re.sub(r'^[-*\d.\s]+', '', title)
            return title
        return ""

    def _find_section_file(self, section_id: str) -> Optional[Path]:
        """查找小节文件。"""
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

    def _create_section_file(self, section_id: str) -> Path:
        """创建新的小节文件。"""
        # 根据节号确定目录
        parts = section_id.split('.')
        chapter_num = int(parts[0])

        chapter_map = {
            0: "序章",
            1: "第一部分", 2: "第一部分", 3: "第一部分",
            4: "第二部分", 5: "第二部分", 6: "第二部分", 7: "第二部分",
            8: "第三部分", 9: "第三部分", 10: "第三部分",
            11: "第四部分", 12: "第四部分", 13: "第四部分",
            14: "终章", 15: "终章",
        }

        chapter_dir = self.book_dir / chapter_map.get(chapter_num, "第一部分")
        chapter_dir.mkdir(parents=True, exist_ok=True)

        return chapter_dir / f"{section_id}_待命名.md"

    def _count_words(self, content: str) -> int:
        """统计字数。"""
        # 中文字符 + 英文单词
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        return chinese_chars + english_words

    def _update_frontmatter(self, file_path: Path, updates: Dict[str, Any]):
        """更新文件的frontmatter。"""
        content = file_path.read_text(encoding='utf-8')

        for key, value in updates.items():
            pattern = rf'^{key}:\s*.+$'
            replacement = f'{key}: {value}'
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                # 在frontmatter末尾添加
                content = re.sub(r'^(---\s*\n.*?)\n---\s*\n',
                                rf'\1\n{replacement}\n---\n',
                                content, flags=re.DOTALL)

        file_path.write_text(content, encoding='utf-8')


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    section_id = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    agent = WritingAgent(book_dir)
    success = agent.write(section_id)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
