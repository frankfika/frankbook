#!/usr/bin/env python3
"""
Editor Agent - 校对专用Agent

职责：
- 术语一致性检查
- 禁用词检查
- 格式规范检查
- 三审三校流程

用法：
    python editor_agent.py <书籍根目录> <节号>
    python editor_agent.py <书籍根目录> terminology
    python editor_agent.py <书籍根目录> checklist

示例：
    python editor_agent.py . 1.1
    python editor_agent.py . terminology
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set


class EditorAgent:
    """校对Agent - 责任编辑检查"""

    # 术语表 - 确保全文统一
    TERMINOLOGY = {
        'OpenClaw': ['OpenClaw', 'openclaw'],
        'Gateway': ['Gateway', 'gateway'],
        'Agent': ['Agent', 'agent'],
        'GEPA': ['GEPA', 'gepa'],
        'Skill': ['Skill', 'skill'],
        'ClawdHub': ['ClawdHub', 'clawdhub'],
        'Lobster': ['Lobster', 'lobster'],
        'Moltbook': ['Moltbook', 'moltbook'],
        'OPC': ['OPC', 'opc'],
    }

    # 禁用词列表
    FORBIDDEN_WORDS = [
        '本节将介绍',
        '综上所述',
        '值得一提的是',
        '不难发现',
        '显而易见',
        '简而言之',
        '换句话说',
        '从某种意义上说',
        '众所周知',
        '本文',
        '笔者',
        '我们',
    ]

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.skill_dir = self.book_dir / '.claude' / 'skills' / 'book-writer'
        self.edit_dir = self.skill_dir / 'assets' / 'edit'
        self.edit_dir.mkdir(parents=True, exist_ok=True)

    def proofread(self, section_id: str) -> bool:
        """
        校对指定小节。

        Args:
            section_id: 小节编号，如 "1.1"

        Returns:
            校对是否成功完成
        """
        print(f"📋 EditorAgent: 开始校对 {section_id}")

        try:
            # 1. 读取章节内容
            section_file = self._find_section_file(section_id)
            if not section_file:
                print(f"❌ 未找到小节文件: {section_id}")
                return False

            content = section_file.read_text(encoding='utf-8')
            print(f"   已加载: {section_file.name}")

            # 2. 执行校对检查
            results = self._proofread_content(content)

            # 3. 生成校对报告
            report = self._generate_report(section_id, results)

            # 4. 保存报告
            edit_file = self.edit_dir / f"{section_id}_edit.md"
            edit_file.write_text(report, encoding='utf-8')

            # 5. 更新状态
            if results['critical_issues'] == 0:
                self._update_section_status(section_id, 'final')
                print(f"✅ EditorAgent: 校对通过 {section_id}")
            else:
                print(f"⚠️ EditorAgent: 发现严重问题 {section_id}")

            print(f"   报告: {edit_file}")
            print(f"   问题统计: 严重={results['critical_issues']}, 警告={results['warnings']}, 建议={results['suggestions']}")
            return True

        except Exception as e:
            print(f"❌ EditorAgent: 校对失败 {section_id} - {e}")
            import traceback
            traceback.print_exc()
            return False

    def _proofread_content(self, content: str) -> Dict[str, Any]:
        """执行校对检查。"""
        results = {
            'critical_issues': 0,
            'warnings': 0,
            'suggestions': 0,
            'checks': {}
        }

        # 1. 术语一致性
        term_result = self._check_terminology(content)
        results['checks']['术语一致性'] = term_result
        results['warnings'] += len(term_result.get('inconsistent', []))

        # 2. 禁用词
        forbidden_result = self._check_forbidden_words(content)
        results['checks']['禁用词'] = forbidden_result
        results['critical_issues'] += len(forbidden_result.get('found', []))

        # 3. 格式规范
        format_result = self._check_format(content)
        results['checks']['格式规范'] = format_result
        results['warnings'] += len(format_result.get('issues', []))

        # 4. 标点符号
        punctuation_result = self._check_punctuation(content)
        results['checks']['标点符号'] = punctuation_result
        results['suggestions'] += len(punctuation_result.get('issues', []))

        # 5. 内容质量
        quality_result = self._check_quality(content)
        results['checks']['内容质量'] = quality_result
        results['suggestions'] += len(quality_result.get('suggestions', []))

        return results

    def _check_terminology(self, content: str) -> Dict:
        """检查术语一致性。"""
        result = {'inconsistent': [], 'details': []}

        for standard, variants in self.TERMINOLOGY.items():
            # 统计每种写法出现次数
            counts = {}
            for variant in variants:
                count = len(re.findall(rf'\b{re.escape(variant)}\b', content))
                if count > 0:
                    counts[variant] = count

            if len(counts) > 1:
                # 有不一致的写法
                main_form = max(counts, key=counts.get)
                for variant in counts:
                    if variant != main_form:
                        result['inconsistent'].append({
                            'term': standard,
                            'found': variant,
                            'should_be': main_form,
                            'count': counts[variant]
                        })

        return result

    def _check_forbidden_words(self, content: str) -> Dict:
        """检查禁用词。"""
        result = {'found': []}

        for word in self.FORBIDDEN_WORDS:
            if word in content:
                # 找到所有出现位置
                for match in re.finditer(re.escape(word), content):
                    line_num = content[:match.start()].count('\n') + 1
                    result['found'].append({
                        'word': word,
                        'line': line_num,
                        'context': content[max(0, match.start()-20):match.end()+20]
                    })

        return result

    def _check_format(self, content: str) -> Dict:
        """检查格式规范。"""
        result = {'issues': []}

        # 检查代码块语言标记
        code_blocks = re.findall(r'```\s*\n', content)
        if code_blocks:
            result['issues'].append(f"有 {len(code_blocks)} 个代码块未指定语言，应添加如 ```python")

        # 检查标题层级
        h1_count = len(re.findall(r'^#\s', content, re.MULTILINE))
        if h1_count > 1:
            result['issues'].append(f"有 {h1_count} 个一级标题，应只有一个")

        # 检查空行
        consecutive_blank = re.findall(r'\n{4,}', content)
        if consecutive_blank:
            result['issues'].append(f"有 {len(consecutive_blank)} 处连续空行超过3个")

        # 检查行尾空格
        trailing_spaces = len(re.findall(r' +\n', content))
        if trailing_spaces > 10:
            result['issues'].append(f"有 {trailing_spaces} 行包含行尾空格")

        return result

    def _check_punctuation(self, content: str) -> Dict:
        """检查标点符号。"""
        result = {'issues': []}

        # 检查中英文标点混用
        if re.search(r'[\u4e00-\u9fff][!,;:?]', content):
            result['issues'].append("中英文标点混用: 中文后使用了英文标点")

        # 检查连续标点
        consecutive = re.findall(r'[。，！？]{2,}', content)
        if consecutive:
            result['issues'].append(f"有 {len(consecutive)} 处连续标点")

        # 检查括号不匹配
        open_paren = content.count('（') + content.count('(')
        close_paren = content.count('）') + content.count(')')
        if open_paren != close_paren:
            result['issues'].append(f"括号不匹配: 左{open_paren}个，右{close_paren}个")

        return result

    def _check_quality(self, content: str) -> Dict:
        """检查内容质量。"""
        result = {'suggestions': []}

        # 统计字数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

        if chinese_chars < 500:
            result['suggestions'].append(f"内容较短 ({chinese_chars}字)，建议扩充")

        # 检查图片
        images = re.findall(r'!\[.*?\]\(.*?\)', content)
        if not images and chinese_chars > 2000:
            result['suggestions'].append("长章节建议添加图表说明")

        # 检查链接
        links = re.findall(r'\[.*?\]\(.*?\)', content)
        if len(links) < 2 and chinese_chars > 2000:
            result['suggestions'].append("建议添加更多参考链接")

        # 检查段落长度
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        long_paras = [p for p in paragraphs if len(p) > 600]
        if len(long_paras) > 2:
            result['suggestions'].append(f"有 {len(long_paras)} 个段落较长，建议拆分")

        return result

    def _generate_report(self, section_id: str, results: Dict) -> str:
        """生成校对报告。"""
        lines = [
            f"# {section_id} 校对报告",
            "",
            f"校对时间: {datetime.now().isoformat()}",
            f"Agent: EditorAgent",
            "",
            "## 检查统计",
            "",
            f"- 严重问题: {results['critical_issues']}",
            f"- 警告: {results['warnings']}",
            f"- 建议: {results['suggestions']}",
            "",
            "## 详细检查结果",
            "",
        ]

        for check_name, check_result in results['checks'].items():
            has_issues = False

            if check_name == '术语一致性' and check_result.get('inconsistent'):
                has_issues = True
                lines.append(f"### ❌ {check_name}")
                lines.append("")
                for item in check_result['inconsistent']:
                    lines.append(f"- '{item['found']}' 应统一为 '{item['should_be']}' (出现{item['count']}次)")
                lines.append("")

            elif check_name == '禁用词' and check_result.get('found'):
                has_issues = True
                lines.append(f"### ❌ {check_name}")
                lines.append("")
                for item in check_result['found'][:10]:  # 最多显示10个
                    lines.append(f"- 第{item['line']}行: \"{item['word']}\"")
                if len(check_result['found']) > 10:
                    lines.append(f"- ... 还有 {len(check_result['found'])-10} 处")
                lines.append("")

            elif check_name == '格式规范' and check_result.get('issues'):
                has_issues = True
                lines.append(f"### ⚠️ {check_name}")
                lines.append("")
                for issue in check_result['issues']:
                    lines.append(f"- {issue}")
                lines.append("")

            elif check_name == '标点符号' and check_result.get('issues'):
                lines.append(f"### 💡 {check_name}")
                lines.append("")
                for issue in check_result['issues']:
                    lines.append(f"- {issue}")
                lines.append("")

            elif check_name == '内容质量' and check_result.get('suggestions'):
                lines.append(f"### 💡 {check_name}")
                lines.append("")
                for sug in check_result['suggestions']:
                    lines.append(f"- {sug}")
                lines.append("")

            if not has_issues and check_name in ['术语一致性', '禁用词', '格式规范']:
                lines.append(f"### ✅ {check_name}")
                lines.append("")
                lines.append("检查通过，未发现明显问题。")
                lines.append("")

        # 出版检查清单
        lines.extend([
            "## 出版检查清单",
            "",
            "### 三审",
            "- [ ] 初审: 内容完整性、逻辑性",
            "- [ ] 复审: 技术准确性、案例合理性",
            "- [ ] 终审: 政治导向、版权合规",
            "",
            "### 三校",
            "- [ ] 一校: 错别字、标点符号",
            "- [ ] 二校: 格式统一、图表编号",
            "- [ ] 三校: 全书统稿、术语一致",
            "",
            "## 总结",
            "",
        ])

        if results['critical_issues'] == 0:
            lines.append("✅ **校对通过** - 该节已达到出版标准")
        else:
            lines.append(f"❌ **需要修改** - 请先处理 {results['critical_issues']} 个严重问题")

        lines.append("")
        return '\n'.join(lines)

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

    def _update_section_status(self, section_id: str, status: str):
        """更新小节状态。"""
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            content = section_file.read_text(encoding='utf-8')
            content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            section_file.write_text(content, encoding='utf-8')

    def print_terminology(self):
        """打印术语表。"""
        print("# OpenClaw 书籍术语表")
        print()
        print("| 标准写法 | 允许变体 | 说明 |")
        print("|----------|----------|------|")

        for standard, variants in self.TERMINOLOGY.items():
            variants_str = ', '.join(variants[1:]) if len(variants) > 1 else '-'
            print(f"| **{standard}** | {variants_str} | 统一使用首字母大写 |")

    def print_checklist(self):
        """打印出版检查清单。"""
        print("""
# OpenClaw 书籍出版检查清单

## 三审流程

### 初审（内容审查）
- [ ] 纲要完整性：是否覆盖所有要求的内容点
- [ ] 逻辑清晰：章节之间逻辑是否通顺
- [ ] 语言流畅：读起来是否自然
- [ ] 无敏感内容：政治、宗教、色情等

### 复审（技术审查）
- [ ] 技术准确性：命令、代码、版本号正确
- [ ] 案例合理性：案例是否真实可信
- [ ] 数据准确性：引用的数据来源可靠
- [ ] 链接有效性：所有链接可访问

### 终审（合规审查）
- [ ] 版权声明：版权声明页完整
- [ ] 授权合规：图片、代码引用已授权
- [ ] 品牌规范：商标、Logo使用正确
- [ ] ISBN申请：已申请ISBN号

## 三校流程

### 一校（文字校对）
- [ ] 错别字检查
- [ ] 标点符号统一
- [ ] 中英文混排规范
- [ ] 数字格式统一

### 二校（格式校对）
- [ ] 标题层级正确
- [ ] 代码块语言标记
- [ ] 图表编号连续
- [ ] 页眉页脚统一

### 三校（统稿）
- [ ] 术语全文统一
- [ ] 人名地名统一
- [ ] 引用格式统一
- [ ] 目录页码正确

## 印刷前检查

- [ ] 封面设计定稿
- [ ] 内文排版完成
- [ ] 彩插位置确认
- [ ] 纸张规格确定
- [ ] 印数确定
        """)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    command = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    agent = EditorAgent(book_dir)

    if command == 'terminology':
        agent.print_terminology()
    elif command == 'checklist':
        agent.print_checklist()
    else:
        # 假设是节号
        success = agent.proofread(command)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
