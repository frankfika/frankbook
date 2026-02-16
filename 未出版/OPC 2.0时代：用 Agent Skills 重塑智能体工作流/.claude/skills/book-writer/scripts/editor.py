#!/usr/bin/env python3
"""
责任编辑工具 - 出版级质量检查

执行责任编辑的三审三校检查，确保出版质量。

用法：
    python editor.py <书籍根目录> <命令> [参数]

命令：
    proofread <节号>       - 对指定小节进行校对检查
    terminology             - 术语一致性检查
    checklist               - 生成出版检查清单
    preface                 - 生成/检查前言、内容简介等辅文

示例：
    python editor.py . proofread 1.2.1
    python editor.py . terminology
    python editor.py . checklist
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


# 术语规范检查规则
TERMINOLOGY_RULES = [
    # (模式, 正确形式, 说明)
    (r'SKILL\.md', 'SKILL.md', '文件名应全大写'),
    (r'^[Ss]kill(?!\.)', 'Skill', '句中 Skill 首字母大写'),
    (r'claude(?!\s|[-])', 'Claude', 'Claude 产品名首字母大写'),
    (r'anthropic(?!\s)', 'Anthropic', 'Anthropic 公司名首字母大写'),
    (r'github', 'GitHub', 'GitHub H 大写'),
    (r'\bagent\b(?!\s[Ss]kill)', 'Agent', 'Agent 专有名词首字母大写'),
    (r'插件|脚本|宏(?=.*[Ss]kill)', '[避免混用]', '统一用 Skill/技能'),
    (r'本节将介绍|综上所述|众所周知', '[禁用词]', '避免学术腔'),
    (r'一言以蔽之|毋庸置疑|显而易见', '[禁用词]', '避免陈词滥调'),
    (r'显然|易得|简单(?=.*读者)', '[禁用词]', '不要居高临下'),
]


# 首次出现需解释的术语
TERMS_NEED_EXPLANATION = [
    'Agent Skill',
    'Progressive Disclosure',
    'MCP',
    'Subagent',
    'YAML Frontmatter',
    'Context Window',
    'Fork',
    'Hook',
]


@dataclass
class Issue:
    level: str  # ERROR, WARN, INFO
    message: str
    suggestion: str = ""


def parse_frontmatter(file_path: Path) -> Tuple[dict, str]:
    """解析 frontmatter 和正文。"""
    content = file_path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)

    if not match:
        return {}, content

    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            fm[key.strip()] = value.strip().strip('"\'')

    return fm, match.group(2)


def check_terminology(file_path: Path) -> List[Issue]:
    """检查术语一致性。"""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(file_path)

    # 检查禁用词
    forbidden_patterns = [
        (r'本节将介绍|综上所述|众所周知', '避免学术腔，直接陈述'),
        (r'一言以蔽之|毋庸置疑|显而易见', '避免陈词滥调'),
        (r'显然|易得|简单', '不要居高临下，假设读者懂'),
        (r'foo|bar|baz', '用真实示例，避免占位符'),
    ]

    for pattern, suggestion in forbidden_patterns:
        matches = re.finditer(pattern, body)
        for match in matches:
            issues.append(Issue(
                level='WARN',
                message=f'发现禁用词: "{match.group()}"',
                suggestion=suggestion
            ))

    # 检查大小写
    case_patterns = [
        (r'\bclaude\b(?!\s+(?:Code|4|3))', 'Claude', '产品名首字母大写'),
        (r'\bgithub\b', 'GitHub', 'H 大写'),
        (r'\banthropic\b', 'Anthropic', '公司名首字母大写'),
    ]

    for pattern, correct, desc in case_patterns:
        matches = re.finditer(pattern, body, re.IGNORECASE)
        for match in matches:
            if match.group() != correct:
                issues.append(Issue(
                    level='INFO',
                    message=f'大小写建议: "{match.group()}" -> "{correct}"',
                    suggestion=desc
                ))

    # 检查术语首次出现是否有解释
    explained_terms = set()
    for term in TERMS_NEED_EXPLANATION:
        # 查找首次出现
        match = re.search(rf'\b{re.escape(term)}\b', body, re.IGNORECASE)
        if match:
            # 检查前后是否有中文解释
            start = max(0, match.start() - 50)
            end = min(len(body), match.end() + 50)
            context = body[start:end]

            # 简单判断是否有中文括号或"简称"等词
            has_chinese = bool(re.search(r'[\u4e00-\u9fff]', context))
            has_parens = '(' in context and ')' in context

            if not (has_chinese and has_parens):
                issues.append(Issue(
                    level='WARN',
                    message=f'术语首次出现建议解释: "{term}"',
                    suggestion='添加中文解释，如: Agent Skill (智能体技能)'
                ))

    return issues


def check_formatting(file_path: Path) -> List[Issue]:
    """检查格式问题。"""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(file_path)

    # 检查代码块
    code_blocks = re.findall(r'```(\w+)?', body)
    for i, lang in enumerate(code_blocks):
        if not lang:
            issues.append(Issue(
                level='INFO',
                message=f'代码块 #{i+1} 未指定语言',
                suggestion='添加语言标记如 ```python ```bash'
            ))

    # 检查段落长度
    paragraphs = body.split('\n\n')
    for i, para in enumerate(paragraphs):
        lines = para.strip().split('\n')
        if len(lines) > 8 and not para.startswith('```'):
            issues.append(Issue(
                level='INFO',
                message=f'第 {i+1} 段落较长 ({len(lines)} 行)',
                suggestion='建议拆分为短段落，便于阅读'
            ))

    # 检查标题层级
    headings = re.findall(r'^(#{1,6})\s+', body, re.MULTILINE)
    prev_level = 0
    for heading in headings:
        level = len(heading)
        if level > prev_level + 1 and prev_level > 0:
            issues.append(Issue(
                level='WARN',
                message=f'标题层级跳跃: {prev_level} -> {level}',
                suggestion='标题层级应逐级递进'
            ))
        prev_level = level

    return issues


def check_content_quality(file_path: Path) -> List[Issue]:
    """检查内容质量。"""
    issues = []
    fm, body = parse_frontmatter(file_path)

    # 统计字数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', body))
    english_words = len(re.findall(r'[a-zA-Z]+', body))
    total_words = chinese_chars + english_words

    target = int(fm.get('target_words', 0))
    if target > 0:
        ratio = total_words / target
        if ratio < 0.5:
            issues.append(Issue(
                level='ERROR',
                message=f'字数严重不足: {total_words}/{target} ({ratio:.0%})',
                suggestion='内容需要大幅扩充'
            ))
        elif ratio < 0.8:
            issues.append(Issue(
                level='WARN',
                message=f'字数偏少: {total_words}/{target} ({ratio:.0%})',
                suggestion='可以适当增加内容深度或案例'
            ))

    # 检查代码示例
    code_blocks = len(re.findall(r'```', body)) // 2
    if code_blocks == 0 and chinese_chars > 500:
        issues.append(Issue(
            level='INFO',
            message='未检测到代码示例',
            suggestion='技术书籍建议添加可运行的代码示例'
        ))

    # 检查图表
    has_table = '|' in body and '---' in body
    has_diagram = 'mermaid' in body or '![' in body
    if not has_table and not has_diagram and chinese_chars > 1000:
        issues.append(Issue(
            level='INFO',
            message='建议添加图表辅助说明',
            suggestion='长段落可用表格或图表增强可读性'
        ))

    return issues


def cmd_proofread(book_dir: Path, section_id: str):
    """校对指定小节。"""
    # 查找小节文件
    chapter_dirs = [
        '引言',
        '第一章_认识Agent_Skill',
        '第二章_Skill的分类与生态',
        '第三章_Agent_Skill开发实战',
    ]

    target_file = None
    for chapter_dir in chapter_dirs:
        chapter_path = book_dir / chapter_dir
        if not chapter_path.exists():
            continue

        for md_file in chapter_path.glob('*.md'):
            if md_file.name.endswith('_完整.md'):
                continue

            fm, _ = parse_frontmatter(md_file)
            if fm.get('section_id') == section_id:
                target_file = md_file
                break

        if target_file:
            break

    if not target_file:
        print(f'❌ 未找到小节: {section_id}')
        return

    print(f'🔍 正在校对: {target_file.name}')
    print('=' * 60)

    all_issues = []
    all_issues.extend(check_terminology(target_file))
    all_issues.extend(check_formatting(target_file))
    all_issues.extend(check_content_quality(target_file))

    if not all_issues:
        print('✅ 校对通过，未发现问题')
        return

    # 分级显示
    errors = [i for i in all_issues if i.level == 'ERROR']
    warns = [i for i in all_issues if i.level == 'WARN']
    infos = [i for i in all_issues if i.level == 'INFO']

    if errors:
        print(f'\n❌ 错误 ({len(errors)}):')
        for issue in errors:
            print(f'  - {issue.message}')
            if issue.suggestion:
                print(f'    建议: {issue.suggestion}')

    if warns:
        print(f'\n⚠️ 警告 ({len(warns)}):')
        for issue in warns:
            print(f'  - {issue.message}')
            if issue.suggestion:
                print(f'    建议: {issue.suggestion}')

    if infos:
        print(f'\nℹ️ 提示 ({len(infos)}):')
        for issue in infos:
            print(f'  - {issue.message}')
            if issue.suggestion:
                print(f'    建议: {issue.suggestion}')

    print(f'\n{"=" * 60}')
    print(f'总计: {len(errors)} 错误 | {len(warns)} 警告 | {len(infos)} 提示')


def cmd_terminology(book_dir: Path):
    """全书术语检查。"""
    print('📚 术语一致性检查')
    print('=' * 60)

    glossary_path = book_dir / '.claude' / 'skills' / 'book-writer' / 'references' / 'glossary.md'
    if glossary_path.exists():
        print('✅ 术语表已存在')
        print(f'   路径: {glossary_path}')
    else:
        print('⚠️ 术语表不存在')
        print('   建议创建: references/glossary.md')

    print('\n需要全文统一的术语:')
    for term in TERMS_NEED_EXPLANATION:
        print(f'  - {term}')


def cmd_checklist(book_dir: Path):
    """生成出版检查清单。"""
    checklist_path = book_dir / '.claude' / 'skills' / 'book-writer' / 'references' / 'editor-checklist.md'

    if checklist_path.exists():
        print('📋 出版检查清单')
        print('=' * 60)
        print(f'已存在: {checklist_path}')
        print('\n包含检查项:')
        print('  - 政治导向与合规')
        print('  - 版权审查')
        print('  - 事实核查')
        print('  - 编校质量')
        print('  - 体例格式')
        print('  - 装帧设计')
        print('  - 印刷前检查')
    else:
        print('⚠️ 检查清单不存在')


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    command = sys.argv[2]

    if not book_dir.exists():
        print(f'错误: 目录不存在: {book_dir}')
        sys.exit(1)

    if command == 'proofread':
        if len(sys.argv) < 4:
            print('用法: editor.py <目录> proofread <节号>')
            sys.exit(1)
        cmd_proofread(book_dir, sys.argv[3])
    elif command == 'terminology':
        cmd_terminology(book_dir)
    elif command == 'checklist':
        cmd_checklist(book_dir)
    else:
        print(f'未知命令: {command}')
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
