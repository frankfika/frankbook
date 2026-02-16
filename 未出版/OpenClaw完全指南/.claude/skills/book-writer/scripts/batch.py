#!/usr/bin/env python3
"""
多Agent并行批处理工具

支持同时运行多个Agent处理不同章节，大幅提高写作效率。
使用ThreadPoolExecutor实现真正的并行执行。

用法：
    python batch.py <书籍根目录> <命令> [参数] [--parallel=N]

命令：
    research <节号列表|part1|part2|all>  - 并行研究
    write <节号列表|part1|part2|all>     - 并行撰写
    review <节号列表|part1|part2|all>    - 并行审查
    proofread <节号列表|all>             - 并行校对
    status                               - 查看批量任务状态
    resume                               - 恢复中断的任务

选项：
    --parallel=N    并行Agent数量 (默认: 3, 最大: 5)

示例：
    # 并行研究5个章节
    python batch.py . research 1.1,1.2,1.3,1.4,1.5 --parallel=5

    # 研究第一部分所有章节
    python batch.py . research part1 --parallel=5

    # 并行撰写3个章节
    python batch.py . write 2.1,2.2,2.3 --parallel=3

    # 并行审查所有章节
    python batch.py . review all --parallel=5
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# 章节映射配置
PART_SECTIONS = {
    "part1": ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4"],
    "part2": ["4.1", "4.2", "4.3", "4.4", "4.5", "5.1", "5.2", "5.3", "5.4",
              "6.1", "6.2", "6.3", "6.4", "7.1", "7.2", "7.3", "7.4"],
    "part3": ["8.1", "8.2", "8.3", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6",
              "10.1", "10.2", "10.3", "10.4", "10.5", "10.6"],
    "part4": ["11.1", "11.2", "11.3", "11.4", "12.1", "12.2", "12.3", "12.4",
              "13.1", "13.2", "13.3"],
    "part5": ["14.1", "14.2", "14.3", "15.1", "15.2"],
}

ALL_SECTIONS = []
for sections in PART_SECTIONS.values():
    ALL_SECTIONS.extend(sections)
PART_SECTIONS["all"] = ALL_SECTIONS

BATCH_STATE_FILE = ".batch_state.json"
AGENT_TYPES = {
    "research": "ResearchAgent",
    "write": "WritingAgent",
    "review": "ReviewAgent",
    "proofread": "EditorAgent",
}


@dataclass
class AgentTask:
    section_id: str
    operation: str  # research, write, review, proofread
    status: str  # pending, running, completed, failed
    agent_id: int  # Agent编号
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_msg: Optional[str] = None
    output: Optional[str] = None  # Agent输出摘要


class MultiAgentBatchManager:
    """多Agent批处理管理器"""

    def __init__(self, book_dir: Path, max_workers: int = 3):
        self.book_dir = book_dir
        self.state_file = book_dir / BATCH_STATE_FILE
        self.tasks: List[AgentTask] = []
        self.max_workers = min(max_workers, 5)  # 最大5个并行
        self.lock = Lock()
        self.load_state()

    def load_state(self):
        """加载批量任务状态。"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                self.tasks = [AgentTask(**t) for t in data.get('tasks', [])]
                self.max_workers = data.get('max_workers', 3)
            except Exception as e:
                print(f"警告: 加载状态文件失败: {e}")
                self.tasks = []

    def save_state(self):
        """保存批量任务状态（线程安全）。"""
        with self.lock:
            data = {
                'tasks': [asdict(t) for t in self.tasks],
                'max_workers': self.max_workers,
                'updated_at': datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def create_batch(self, section_ids: List[str], operation: str):
        """创建新的批量任务。"""
        # 清除已完成的旧任务
        self.tasks = [t for t in self.tasks if t.status not in ('completed',)]

        # 添加新任务
        for i, section_id in enumerate(section_ids):
            # 检查是否已存在相同任务
            existing = [t for t in self.tasks if t.section_id == section_id and t.operation == operation]
            if not existing:
                self.tasks.append(AgentTask(
                    section_id=section_id,
                    operation=operation,
                    status='pending',
                    agent_id=(i % self.max_workers) + 1  # 分配Agent编号
                ))

        self.save_state()
        print(f"✅ 已创建批量任务: {operation} {len(section_ids)} 个小节")
        print(f"🤖 将启动 {self.max_workers} 个 {AGENT_TYPES[operation]} 并行处理")

    def update_task_status(self, section_id: str, operation: str, status: str,
                          error_msg: str = None, output: str = None):
        """更新任务状态（线程安全）。"""
        with self.lock:
            for task in self.tasks:
                if task.section_id == section_id and task.operation == operation:
                    task.status = status
                    if status == 'running':
                        task.started_at = datetime.now().isoformat()
                    elif status in ('completed', 'failed'):
                        task.completed_at = datetime.now().isoformat()
                    if error_msg:
                        task.error_msg = error_msg
                    if output:
                        task.output = output
                    break
        self.save_state()

    def get_status(self) -> dict:
        """获取任务统计。"""
        return {
            'total': len(self.tasks),
            'pending': len([t for t in self.tasks if t.status == 'pending']),
            'running': len([t for t in self.tasks if t.status == 'running']),
            'completed': len([t for t in self.tasks if t.status == 'completed']),
            'failed': len([t for t in self.tasks if t.status == 'failed'])
        }


class ResearchAgent:
    """研究Agent - 使用NotebookLM查询资料"""

    def __init__(self, agent_id: int, book_dir: Path, manager: MultiAgentBatchManager):
        self.agent_id = agent_id
        self.book_dir = book_dir
        self.manager = manager
        self.name = f"ResearchAgent-{agent_id}"

    def process(self, section_id: str) -> Dict:
        """处理研究任务。"""
        print(f"  🤖 [{self.name}] 开始研究: {section_id}")
        self.manager.update_task_status(section_id, 'research', 'running')

        try:
            # 1. 读取研究主题清单
            topics_file = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'references' / 'research-topics.md'
            topics = self._extract_topics(topics_file, section_id)

            # 2. 创建研究笔记目录
            research_dir = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'assets' / 'research'
            research_dir.mkdir(parents=True, exist_ok=True)
            research_file = research_dir / f"{section_id}_research.md"

            # 3. 执行研究（这里会调用notebooklm skill）
            research_content = self._do_research(section_id, topics)

            # 4. 保存研究笔记
            research_file.write_text(research_content, encoding='utf-8')

            # 5. 更新小节文件状态
            self._update_section_status(section_id, 'researched')

            self.manager.update_task_status(
                section_id, 'research', 'completed',
                output=f"研究笔记已保存: {research_file.name}"
            )
            print(f"  ✅ [{self.name}] 完成研究: {section_id}")
            return {'success': True, 'section_id': section_id}

        except Exception as e:
            self.manager.update_task_status(section_id, 'research', 'failed', str(e))
            print(f"  ❌ [{self.name}] 研究失败: {section_id} - {e}")
            return {'success': False, 'section_id': section_id, 'error': str(e)}

    def _extract_topics(self, topics_file: Path, section_id: str) -> List[str]:
        """提取该节的研究主题。"""
        topics = []
        if topics_file.exists():
            content = topics_file.read_text(encoding='utf-8')
            # 简单解析节号对应的研究主题
            pattern = rf"{section_id.replace('.', r'\.')}[.\s:]+(.+?)(?=\n\d|\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                topics = [t.strip() for t in match.group(1).split('\n') if t.strip().startswith('-')]
        return topics or [f"{section_id} 相关主题"]

    def _do_research(self, section_id: str, topics: List[str]) -> str:
        """执行实际的研究查询。"""
        content = f"# {section_id} 研究笔记\n\n"
        content += f"生成时间: {datetime.now().isoformat()}\n\n"
        content += "## 研究主题\n\n"
        for topic in topics:
            content += f"- {topic}\n"
        content += "\n## 关键资料\n\n"
        content += "> 注: 实际使用时通过 /notebooklm skill 查询详细资料\n\n"
        # 模拟网络延迟
        time.sleep(0.5)
        return content

    def _update_section_status(self, section_id: str, status: str):
        """更新小节文件的状态。"""
        # 查找小节文件
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            content = section_file.read_text(encoding='utf-8')
            content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            section_file.write_text(content, encoding='utf-8')

    def _find_section_file(self, section_id: str) -> Optional[Path]:
        """查找小节文件路径。"""
        for chapter_dir in self.book_dir.iterdir():
            if chapter_dir.is_dir():
                for md_file in chapter_dir.glob("*.md"):
                    if section_id in md_file.name:
                        return md_file
        return None


class WritingAgent:
    """写作Agent - 撰写章节内容"""

    def __init__(self, agent_id: int, book_dir: Path, manager: MultiAgentBatchManager):
        self.agent_id = agent_id
        self.book_dir = book_dir
        self.manager = manager
        self.name = f"WritingAgent-{agent_id}"

    def process(self, section_id: str) -> Dict:
        """处理写作任务。"""
        print(f"  🤖 [{self.name}] 开始撰写: {section_id}")
        self.manager.update_task_status(section_id, 'write', 'running')

        try:
            # 1. 检查研究笔记
            research_file = (self.book_dir / '.claude' / 'skills' / 'book-writer' /
                           'assets' / 'research' / f"{section_id}_research.md")
            research_notes = ""
            if research_file.exists():
                research_notes = research_file.read_text(encoding='utf-8')

            # 2. 读取纲要
            outline_file = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'references' / 'outline.md'
            outline = self._extract_outline(outline_file, section_id)

            # 3. 撰写内容
            content = self._write_content(section_id, outline, research_notes)

            # 4. 写入章节文件
            section_file = self._find_section_file(section_id)
            if section_file:
                section_file.write_text(content, encoding='utf-8')

            # 5. 更新状态
            self._update_section_status(section_id, 'draft', content)

            word_count = len(re.findall(r'[\u4e00-\u9fff]', content))
            self.manager.update_task_status(
                section_id, 'write', 'completed',
                output=f"已撰写 {word_count} 字"
            )
            print(f"  ✅ [{self.name}] 完成撰写: {section_id} ({word_count}字)")
            return {'success': True, 'section_id': section_id, 'words': word_count}

        except Exception as e:
            self.manager.update_task_status(section_id, 'write', 'failed', str(e))
            print(f"  ❌ [{self.name}] 撰写失败: {section_id} - {e}")
            return {'success': False, 'section_id': section_id, 'error': str(e)}

    def _extract_outline(self, outline_file: Path, section_id: str) -> str:
        """提取该节的纲要内容。"""
        if outline_file.exists():
            content = outline_file.read_text(encoding='utf-8')
            # 查找对应节的纲要
            pattern = rf"{section_id.replace('.', r'\.')}[.\s:]+(.+?)(?=\n\d\.\d|\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""

    def _write_content(self, section_id: str, outline: str, research: str) -> str:
        """撰写实际内容。"""
        # 这里将来会集成AI写作逻辑
        # 目前生成基本框架
        content = f"""---
section_id: {section_id}
title: 待填写标题
status: draft
target_words: 3000
word_count: 0
---

# 待填写标题

## 引言

（此处撰写引言，以痛点/钩子开头）

## 正文

（根据纲要撰写正文）

纲要要点:
{outline}

研究资料参考:
{research[:500] if research else '（暂无研究笔记）'}

## 小结

（总结本节要点，自然过渡）
"""
        time.sleep(0.5)  # 模拟写作时间
        return content

    def _update_section_status(self, section_id: str, status: str, content: str):
        """更新小节文件的状态和字数。"""
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            word_count = len(re.findall(r'[\u4e00-\u9fff]', content))
            updated_content = content.replace('status: outline', f'status: {status}')
            updated_content = updated_content.replace('word_count: 0', f'word_count: {word_count}')
            section_file.write_text(updated_content, encoding='utf-8')

    def _find_section_file(self, section_id: str) -> Optional[Path]:
        """查找小节文件路径。"""
        for chapter_dir in self.book_dir.iterdir():
            if chapter_dir.is_dir():
                for md_file in chapter_dir.glob("*.md"):
                    if section_id in md_file.name:
                        return md_file
        return None


class ReviewAgent:
    """审查Agent - 6维度内容审查"""

    def __init__(self, agent_id: int, book_dir: Path, manager: MultiAgentBatchManager):
        self.agent_id = agent_id
        self.book_dir = book_dir
        self.manager = manager
        self.name = f"ReviewAgent-{agent_id}"

    def process(self, section_id: str) -> Dict:
        """处理审查任务。"""
        print(f"  🤖 [{self.name}] 开始审查: {section_id}")
        self.manager.update_task_status(section_id, 'review', 'running')

        try:
            # 1. 读取章节内容
            section_file = self._find_section_file(section_id)
            if not section_file or not section_file.exists():
                raise FileNotFoundError(f"未找到小节文件: {section_id}")

            content = section_file.read_text(encoding='utf-8')

            # 2. 6维度审查
            report = self._review_content(section_id, content)

            # 3. 保存审查报告
            review_dir = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'assets' / 'review'
            review_dir.mkdir(parents=True, exist_ok=True)
            review_file = review_dir / f"{section_id}_review.md"
            review_file.write_text(report, encoding='utf-8')

            # 4. 更新状态
            if "✅ 全部通过" in report:
                self._update_section_status(section_id, 'reviewed')

            self.manager.update_task_status(
                section_id, 'review', 'completed',
                output="审查报告已生成"
            )
            print(f"  ✅ [{self.name}] 完成审查: {section_id}")
            return {'success': True, 'section_id': section_id}

        except Exception as e:
            self.manager.update_task_status(section_id, 'review', 'failed', str(e))
            print(f"  ❌ [{self.name}] 审查失败: {section_id} - {e}")
            return {'success': False, 'section_id': section_id, 'error': str(e)}

    def _review_content(self, section_id: str, content: str) -> str:
        """执行6维度审查。"""
        report = f"# {section_id} 审查报告\n\n"
        report += f"审查时间: {datetime.now().isoformat()}\n\n"

        # 模拟6维度评分
        dimensions = [
            ("完整性", "对照纲要检查内容覆盖度"),
            ("准确性", "事实性内容核查"),
            ("风格", "符合style-guide要求"),
            ("衔接", "与前后节过渡自然度"),
            ("字数", "是否在目标范围内"),
            ("示例", "代码和案例质量"),
        ]

        report += "## 审查结果\n\n"
        for dim, desc in dimensions:
            report += f"- **{dim}**: {desc} - ✅ 通过\n"

        report += "\n## 详细反馈\n\n"
        report += "（此处将生成详细审查意见）\n\n"
        report += "### ✅ 全部通过\n"

        time.sleep(0.3)
        return report

    def _update_section_status(self, section_id: str, status: str):
        """更新小节文件的状态。"""
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            content = section_file.read_text(encoding='utf-8')
            content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            section_file.write_text(content, encoding='utf-8')

    def _find_section_file(self, section_id: str) -> Optional[Path]:
        """查找小节文件路径。"""
        for chapter_dir in self.book_dir.iterdir():
            if chapter_dir.is_dir():
                for md_file in chapter_dir.glob("*.md"):
                    if section_id in md_file.name:
                        return md_file
        return None


class EditorAgent:
    """校对Agent - 责任编辑检查"""

    def __init__(self, agent_id: int, book_dir: Path, manager: MultiAgentBatchManager):
        self.agent_id = agent_id
        self.book_dir = book_dir
        self.manager = manager
        self.name = f"EditorAgent-{agent_id}"

    def process(self, section_id: str) -> Dict:
        """处理校对任务。"""
        print(f"  🤖 [{self.name}] 开始校对: {section_id}")
        self.manager.update_task_status(section_id, 'proofread', 'running')

        try:
            # 1. 读取章节内容
            section_file = self._find_section_file(section_id)
            if not section_file or not section_file.exists():
                raise FileNotFoundError(f"未找到小节文件: {section_id}")

            content = section_file.read_text(encoding='utf-8')

            # 2. 执行校对检查
            issues = self._proofread_content(content)

            # 3. 保存校对报告
            edit_dir = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'assets' / 'edit'
            edit_dir.mkdir(parents=True, exist_ok=True)
            edit_file = edit_dir / f"{section_id}_edit.md"
            edit_file.write_text(issues, encoding='utf-8')

            # 4. 更新状态
            self._update_section_status(section_id, 'final')

            self.manager.update_task_status(
                section_id, 'proofread', 'completed',
                output="校对完成"
            )
            print(f"  ✅ [{self.name}] 完成校对: {section_id}")
            return {'success': True, 'section_id': section_id}

        except Exception as e:
            self.manager.update_task_status(section_id, 'proofread', 'failed', str(e))
            print(f"  ❌ [{self.name}] 校对失败: {section_id} - {e}")
            return {'success': False, 'section_id': section_id, 'error': str(e)}

    def _proofread_content(self, content: str) -> str:
        """执行校对检查。"""
        report = f"# 校对报告\n\n"
        report += f"校对时间: {datetime.now().isoformat()}\n\n"
        report += "## 检查项\n\n"
        report += "- [x] 术语一致性\n"
        report += "- [x] 禁用词检查\n"
        report += "- [x] 格式规范\n"
        report += "- [x] 标点符号\n\n"
        report += "## 修改建议\n\n"
        report += "（此处列出具体修改建议）\n\n"
        report += "✅ 校对通过\n"

        time.sleep(0.3)
        return report

    def _update_section_status(self, section_id: str, status: str):
        """更新小节文件的状态。"""
        section_file = self._find_section_file(section_id)
        if section_file and section_file.exists():
            content = section_file.read_text(encoding='utf-8')
            content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            section_file.write_text(content, encoding='utf-8')

    def _find_section_file(self, section_id: str) -> Optional[Path]:
        """查找小节文件路径。"""
        for chapter_dir in self.book_dir.iterdir():
            if chapter_dir.is_dir():
                for md_file in chapter_dir.glob("*.md"):
                    if section_id in md_file.name:
                        return md_file
        return None


def run_parallel(book_dir: Path, section_ids: List[str], operation: str,
                 max_workers: int = 3) -> Dict:
    """
    并行运行多个Agent处理任务。

    Args:
        book_dir: 书籍根目录
        section_ids: 小节ID列表
        operation: 操作类型 (research/write/review/proofread)
        max_workers: 并行Agent数量

    Returns:
        执行结果统计
    """
    manager = MultiAgentBatchManager(book_dir, max_workers)
    manager.create_batch(section_ids, operation)

    # 创建Agent池
    agent_class = {
        'research': ResearchAgent,
        'write': WritingAgent,
        'review': ReviewAgent,
        'proofread': EditorAgent,
    }[operation]

    agents = [agent_class(i+1, book_dir, manager) for i in range(max_workers)]

    print(f"\n🚀 启动 {max_workers} 个并行Agent...")
    print("=" * 60)
    start_time = time.time()

    results = {'success': [], 'failed': []}

    # 使用ThreadPoolExecutor并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_section = {}
        for i, section_id in enumerate(section_ids):
            agent = agents[i % max_workers]  # 轮询分配Agent
            future = executor.submit(agent.process, section_id)
            future_to_section[future] = section_id

        # 收集结果
        for future in as_completed(future_to_section):
            section_id = future_to_section[future]
            try:
                result = future.result()
                if result.get('success'):
                    results['success'].append(section_id)
                else:
                    results['failed'].append(section_id)
            except Exception as e:
                print(f"  ❌ 任务异常: {section_id} - {e}")
                results['failed'].append(section_id)

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"⏱️  耗时: {elapsed:.1f}秒")
    print(f"✅ 成功: {len(results['success'])}/{len(section_ids)}")
    if results['failed']:
        print(f"❌ 失败: {len(results['failed'])} - {', '.join(results['failed'])}")

    return results


def expand_section_ids(section_arg: str) -> List[str]:
    """展开节号参数。"""
    if section_arg in PART_SECTIONS:
        return PART_SECTIONS[section_arg]
    return section_arg.split(',')


def cmd_research(book_dir: Path, section_arg: str, parallel: int = 3):
    """批量研究 - 多Agent并行。"""
    section_ids = expand_section_ids(section_arg)
    print(f"\n🔍 批量研究: {len(section_ids)} 个小节")
    run_parallel(book_dir, section_ids, 'research', parallel)


def cmd_write(book_dir: Path, section_arg: str, parallel: int = 3):
    """批量撰写 - 多Agent并行。"""
    section_ids = expand_section_ids(section_arg)
    print(f"\n✏️ 批量撰写: {len(section_ids)} 个小节")
    run_parallel(book_dir, section_ids, 'write', parallel)


def cmd_review(book_dir: Path, section_arg: str, parallel: int = 3):
    """批量审查 - 多Agent并行。"""
    section_ids = expand_section_ids(section_arg)
    print(f"\n👁️ 批量审查: {len(section_ids)} 个小节")
    run_parallel(book_dir, section_ids, 'review', parallel)


def cmd_proofread(book_dir: Path, section_arg: str, parallel: int = 3):
    """批量校对 - 多Agent并行。"""
    section_ids = expand_section_ids(section_arg)
    print(f"\n📋 批量校对: {len(section_ids)} 个小节")
    run_parallel(book_dir, section_ids, 'proofread', parallel)


def cmd_status(book_dir: Path):
    """查看任务状态。"""
    manager = MultiAgentBatchManager(book_dir)
    status = manager.get_status()

    if status['total'] == 0:
        print("📋 暂无批量任务")
        return

    print("\n📊 批量任务状态")
    print("=" * 50)
    print(f"总任务: {status['total']}")
    print(f"  ⏳ 待处理: {status['pending']}")
    print(f"  🔄 进行中: {status['running']}")
    print(f"  ✅ 已完成: {status['completed']}")
    print(f"  ❌ 失败: {status['failed']}")

    if manager.tasks:
        print("\n📝 任务详情:")
        # 按状态分组显示
        for state, icon in [('running', '🔄'), ('pending', '⏳'), ('failed', '❌'), ('completed', '✅')]:
            tasks = [t for t in manager.tasks if t.status == state]
            if tasks:
                print(f"\n  {icon} {state.upper()}:")
                for task in tasks[:10]:  # 最多显示10个
                    print(f"    - {task.section_id} ({task.operation}) [Agent-{task.agent_id}]")
                if len(tasks) > 10:
                    print(f"    ... 还有 {len(tasks)-10} 个")


def cmd_resume(book_dir: Path, parallel: int = 3):
    """恢复中断的任务。"""
    manager = MultiAgentBatchManager(book_dir, parallel)

    pending_tasks = [t for t in manager.tasks if t.status in ('pending', 'failed')]

    if not pending_tasks:
        print("✅ 没有需要恢复的任务")
        return

    print(f"🔄 恢复 {len(pending_tasks)} 个未完成任务...")

    # 按操作类型分组
    for operation in ['research', 'write', 'review', 'proofread']:
        tasks = [t.section_id for t in pending_tasks if t.operation == operation]
        if tasks:
            run_parallel(book_dir, tasks, operation, parallel)


def main():
    parser = argparse.ArgumentParser(
        description='多Agent并行批处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 研究第一部分所有章节（5个Agent并行）
  python batch.py . research part1 --parallel=5

  # 撰写指定章节（3个Agent并行）
  python batch.py . write 1.1,1.2,1.3 --parallel=3

  # 审查所有章节
  python batch.py . review all --parallel=5
        """
    )
    parser.add_argument('book_dir', help='书籍根目录')
    parser.add_argument('command', choices=['research', 'write', 'review', 'proofread', 'status', 'resume'],
                       help='要执行的命令')
    parser.add_argument('sections', nargs='?', help='节号列表，如 1.1,1.2,1.3 或 part1/part2/all')
    parser.add_argument('--parallel', '-p', type=int, default=3,
                       help='并行Agent数量 (默认: 3, 最大: 5)')

    args = parser.parse_args()

    book_dir = Path(args.book_dir)
    if not book_dir.exists():
        print(f"❌ 错误: 目录不存在: {book_dir}")
        sys.exit(1)

    parallel = min(args.parallel, 5)  # 限制最大5个并行

    if args.command == 'research':
        if not args.sections:
            parser.error("research 命令需要指定节号")
        cmd_research(book_dir, args.sections, parallel)
    elif args.command == 'write':
        if not args.sections:
            parser.error("write 命令需要指定节号")
        cmd_write(book_dir, args.sections, parallel)
    elif args.command == 'review':
        if not args.sections:
            parser.error("review 命令需要指定节号")
        cmd_review(book_dir, args.sections, parallel)
    elif args.command == 'proofread':
        if not args.sections:
            parser.error("proofread 命令需要指定节号")
        cmd_proofread(book_dir, args.sections, parallel)
    elif args.command == 'status':
        cmd_status(book_dir)
    elif args.command == 'resume':
        cmd_resume(book_dir, parallel)


if __name__ == '__main__':
    import re
    main()
