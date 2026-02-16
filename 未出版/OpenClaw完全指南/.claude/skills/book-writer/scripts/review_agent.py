#!/usr/bin/env python3
"""
Review Agent - 审查专用Agent

职责：
- 6维度内容审查
- 生成审查报告
- 提出修改建议

用法：
    python review_agent.py <书籍根目录> <节号>

示例：
    python review_agent.py . 1.1
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class ReviewAgent:
    """审查Agent - 6维度内容审查"""

    # 6个审查维度
    DIMENSIONS = [
        ("完整性", "对照纲要，检查是否覆盖了所有要求的内容点"),
        ("准确性", "事实性内容（数据、日期、仓库地址）是否正确"),
        ("风格", "是否符合style-guide要求（对话式、场景化、有节奏感）"),
        ("衔接", "与前后节的过渡是否自然"),
        ("字数", "是否在目标范围内（±20%）"),
        ("示例", "代码和案例是否充实、原创、可运行"),
    ]

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.skill_dir = self.book_dir / '.claude' / 'skills' / 'book-writer'
        self.review_dir = self.skill_dir / 'assets' / 'review'
        self.review_dir.mkdir(parents=True, exist_ok=True)

    def review(self, section_id: str) -> bool:
        """
        审查指定小节。

        Args:
            section_id: 小节编号，如 "1.1"

        Returns:
            审查是否成功完成
        """
        print(f"👁️ ReviewAgent: 开始审查 {section_id}")

        try:
            # 1. 读取章节内容
            section_file = self._find_section_file(section_id)
            if not section_file:
                print(f"❌ 未找到小节文件: {section_id}")
                return False

            content = section_file.read_text(encoding='utf-8')
            print(f"   已加载: {section_file.name}")

            # 2. 读取参考文件
            outline = self._get_outline(section_id)
            style_guide = self._load_style_guide()

            # 3. 6维度审查
            results = self._review_dimensions(section_id, content, outline, style_guide)

            # 4. 生成审查报告
            report = self._generate_report(section_id, results, content)

            # 5. 保存报告
            report_file = self.review_dir / f"{section_id}_review.md"
            report_file.write_text(report, encoding='utf-8')

            # 6. 更新状态（如果全部通过）
            if all(r['passed'] for r in results.values()):
                self._update_section_status(section_id, 'reviewed')
                print(f"✅ ReviewAgent: 审查通过 {section_id}")
            else:
                print(f"⚠️ ReviewAgent: 审查发现问题 {section_id}")

            print(f"   报告: {report_file}")
            return True

        except Exception as e:
            print(f"❌ ReviewAgent: 审查失败 {section_id} - {e}")
            import traceback
            traceback.print_exc()
            return False

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

    def _get_outline(self, section_id: str) -> str:
        """获取纲要。"""
        outline_file = self.skill_dir / 'references' / 'outline.md'
        if not outline_file.exists():
            return ""

        content = outline_file.read_text(encoding='utf-8')
        pattern = rf"{section_id.replace('.', r'\.')}[.\s:]+(.+?)(?=\n\d\.\d|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _load_style_guide(self) -> Dict[str, Any]:
        """加载风格指南。"""
        style_file = self.skill_dir / 'references' / 'style-guide.md'

        guide = {
            'required_elements': ['痛点开头', '场景化', '代码示例', '小结'],
            'forbidden_words': ['本节将介绍', '综上所述', '值得一提的是'],
            'tone': '对话式、深入浅出',
        }

        if style_file.exists():
            content = style_file.read_text(encoding='utf-8')
            # 解析禁用词
            if '禁用' in content or '避免' in content:
                # 提取禁用词列表
                matches = re.findall(r'["\']([^"\']+(?:将介绍|综上所述)[^"\']*)["\']', content)
                if matches:
                    guide['forbidden_words'].extend(matches)

        return guide

    def _review_dimensions(self, section_id: str, content: str,
                          outline: str, style_guide: Dict) -> Dict[str, Dict]:
        """6维度审查。"""
        results = {}

        # 解析frontmatter
        fm = self._parse_frontmatter(content)

        for dim_name, dim_desc in self.DIMENSIONS:
            result = {
                'name': dim_name,
                'description': dim_desc,
                'passed': True,
                'score': 10,
                'issues': [],
                'suggestions': []
            }

            if dim_name == "完整性":
                result = self._check_completeness(result, content, outline)
            elif dim_name == "准确性":
                result = self._check_accuracy(result, content)
            elif dim_name == "风格":
                result = self._check_style(result, content, style_guide)
            elif dim_name == "衔接":
                result = self._check_transition(result, content)
            elif dim_name == "字数":
                result = self._check_word_count(result, content, fm)
            elif dim_name == "示例":
                result = self._check_examples(result, content)

            results[dim_name] = result

        return results

    def _check_completeness(self, result: Dict, content: str, outline: str) -> Dict:
        """检查完整性。"""
        # 检查纲要要点是否覆盖
        outline_points = self._extract_outline_points(outline)

        missing = []
        for point in outline_points[:5]:  # 检查前5个要点
            keywords = self._extract_keywords(point)
            if keywords and not any(kw in content for kw in keywords):
                missing.append(point)

        if missing:
            result['passed'] = False
            result['score'] = 6
            result['issues'].append(f"未覆盖纲要要点: {len(missing)} 处")
            result['suggestions'].append("请补充以下内容：" + "; ".join(missing[:3]))

        # 检查必要结构
        required_sections = ['引言', '正文', '小结']
        for section in required_sections:
            if section not in content:
                result['passed'] = False
                result['issues'].append(f"缺少{section}部分")

        return result

    def _check_accuracy(self, result: Dict, content: str) -> Dict:
        """检查准确性。"""
        issues = []

        # 检查GitHub链接格式
        github_links = re.findall(r'github\.com/[^\s)]+', content)
        for link in github_links:
            if ' ' in link or not link.count('/') >= 2:
                issues.append(f"GitHub链接格式可能不正确: {link}")

        # 检查日期格式
        dates = re.findall(r'\d{4}[年/-]\d{1,2}[月/-]?\d{0,2}', content)
        # 可以添加日期合理性检查

        # 检查版本号格式
        versions = re.findall(r'v?\d+\.\d+\.\d+', content)

        if issues:
            result['passed'] = False
            result['score'] = 7
            result['issues'].extend(issues)

        return result

    def _check_style(self, result: Dict, content: str, style_guide: Dict) -> Dict:
        """检查风格。"""
        issues = []

        # 检查禁用词
        for word in style_guide.get('forbidden_words', []):
            if word in content:
                issues.append(f"使用了禁用词: '{word}'")

        # 检查段落长度（避免过长段落）
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500]
        if len(long_paragraphs) > 3:
            issues.append(f"有 {len(long_paragraphs)} 个段落过长，建议拆分")

        # 检查代码块
        code_blocks = re.findall(r'```[\w]*\n', content)
        if not code_blocks:
            issues.append("缺少代码示例")

        if issues:
            result['passed'] = False
            result['score'] = 6
            result['issues'].extend(issues)

        return result

    def _check_transition(self, result: Dict, content: str) -> Dict:
        """检查衔接。"""
        # 检查开头是否有过渡
        if re.search(r'^(在这一节|前面我们|上一节|接下来)', content, re.MULTILINE):
            result['suggestions'].append("开头过渡自然")
        else:
            result['suggestions'].append("建议开头添加与上节的衔接")

        # 检查结尾是否有过渡
        if '小结' in content or '下一节' in content or '敬请期待' in content:
            pass  # 正常
        else:
            result['suggestions'].append("建议结尾添加与下节的过渡")

        return result

    def _check_word_count(self, result: Dict, content: str, fm: Dict) -> Dict:
        """检查字数。"""
        # 计算实际字数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        actual = chinese_chars + english_words

        target = fm.get('target_words', 3000)

        if target > 0:
            ratio = actual / target
            if ratio < 0.8:
                result['passed'] = False
                result['score'] = 5
                result['issues'].append(f"字数不足: {actual}/{target} ({ratio:.0%})")
                result['suggestions'].append(f"需要补充约 {target - actual} 字")
            elif ratio > 1.5:
                result['score'] = 7
                result['suggestions'].append(f"字数偏多: {actual}/{target}，建议精简")
            else:
                result['suggestions'].append(f"字数达标: {actual}/{target} ({ratio:.0%})")

        return result

    def _check_examples(self, result: Dict, content: str) -> Dict:
        """检查示例质量。"""
        issues = []

        # 检查代码块
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        if not code_blocks:
            issues.append("缺少代码示例")
        elif len(code_blocks) < 2:
            issues.append("代码示例较少，建议增加")

        # 检查代码块语言标记
        code_headers = re.findall(r'```(\w*)\n', content)
        empty_headers = [h for h in code_headers if not h]
        if empty_headers:
            issues.append(f"有 {len(empty_headers)} 个代码块未指定语言")

        # 检查案例描述
        if '案例' not in content and '例子' not in content and '场景' not in content:
            issues.append("缺少具体案例或场景描述")

        if issues:
            result['passed'] = False
            result['score'] = 6
            result['issues'].extend(issues)

        return result

    def _extract_outline_points(self, outline: str) -> List[str]:
        """提取纲要要点。"""
        points = []
        for line in outline.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or
                        re.match(r'^\d+\.', line)):
                points.append(re.sub(r'^[-*\d.\s]+', '', line))
            elif line and len(points) < 10:
                points.append(line)
        return points

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词。"""
        # 简单的关键词提取
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        return [w for w in words if len(w) >= 2][:3]

    def _parse_frontmatter(self, content: str) -> Dict:
        """解析frontmatter。"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}

        fm = {}
        for line in match.group(1).strip().split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                fm[key] = value
        return fm

    def _generate_report(self, section_id: str, results: Dict[str, Dict],
                        content: str) -> str:
        """生成审查报告。"""
        lines = [
            f"# {section_id} 审查报告",
            "",
            f"审查时间: {datetime.now().isoformat()}",
            f"Agent: ReviewAgent",
            "",
            "## 6维度评分",
            "",
        ]

        # 评分表
        lines.append("| 维度 | 状态 | 分数 | 问题数 |")
        lines.append("|------|------|------|--------|")

        all_passed = True
        for dim_name, result in results.items():
            status = "✅" if result['passed'] else "❌"
            score = result['score']
            issues_count = len(result['issues'])
            lines.append(f"| {dim_name} | {status} | {score}/10 | {issues_count} |")
            if not result['passed']:
                all_passed = False

        lines.extend([
            "",
            "## 详细反馈",
            "",
        ])

        for dim_name, result in results.items():
            status_icon = "✅" if result['passed'] else "❌"
            lines.append(f"### {status_icon} {dim_name}")
            lines.append(f"*{result['description']}*")
            lines.append("")

            if result['issues']:
                lines.append("**问题：**")
                for issue in result['issues']:
                    lines.append(f"- ⚠️ {issue}")
                lines.append("")

            if result['suggestions']:
                lines.append("**建议：**")
                for sug in result['suggestions']:
                    lines.append(f"- 💡 {sug}")
                lines.append("")

        # 总结
        lines.extend([
            "## 总结",
            "",
        ])

        if all_passed:
            lines.append("✅ **全部通过** - 该节已达到发布标准")
        else:
            failed = [r['name'] for r in results.values() if not r['passed']]
            lines.append(f"❌ **需要改进** - 请处理以下维度: {', '.join(failed)}")

        lines.append("")
        return '\n'.join(lines)

    def _update_section_status(self, section_id: str, status: str):
        """更新小节状态。"""
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            content = section_file.read_text(encoding='utf-8')
            content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            section_file.write_text(content, encoding='utf-8')


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    section_id = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    agent = ReviewAgent(book_dir)
    success = agent.review(section_id)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
