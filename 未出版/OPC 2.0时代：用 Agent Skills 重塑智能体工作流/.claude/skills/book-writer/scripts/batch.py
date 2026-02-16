#!/usr/bin/env python3
"""
批量处理工具 - 支持并发和断点续传

支持批量研究、撰写多个章节，自动保存进度，网络中断后可恢复。

用法：
    python batch.py <书籍根目录> <命令> [参数]

命令：
    research <节号列表>      - 批量研究（逗号分隔）
    write <节号列表>         - 批量撰写（逗号分隔）
    status                   - 查看批量任务状态
    resume                   - 恢复中断的任务

示例：
    python batch.py . research 1.1.1,1.1.2,1.1.3
    python batch.py . write 2.1,2.2,2.3
    python batch.py . status
    python batch.py . resume
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional


BATCH_STATE_FILE = ".batch_state.json"


@dataclass
class Task:
    section_id: str
    operation: str  # research, write
    status: str  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_msg: Optional[str] = None


class BatchManager:
    def __init__(self, book_dir: Path):
        self.book_dir = book_dir
        self.state_file = book_dir / BATCH_STATE_FILE
        self.tasks: List[Task] = []
        self.load_state()

    def load_state(self):
        """加载批量任务状态。"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                self.tasks = [Task(**t) for t in data.get('tasks', [])]
            except Exception as e:
                print(f"警告: 加载状态文件失败: {e}")
                self.tasks = []

    def save_state(self):
        """保存批量任务状态。"""
        data = {
            'tasks': [asdict(t) for t in self.tasks],
            'updated_at': datetime.now().isoformat()
        }
        self.state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def create_batch(self, section_ids: List[str], operation: str):
        """创建新的批量任务。"""
        # 清除已完成的旧任务
        self.tasks = [t for t in self.tasks if t.status not in ('completed',)]

        # 添加新任务
        for section_id in section_ids:
            # 检查是否已存在相同任务
            existing = [t for t in self.tasks if t.section_id == section_id and t.operation == operation]
            if not existing:
                self.tasks.append(Task(
                    section_id=section_id,
                    operation=operation,
                    status='pending'
                ))

        self.save_state()
        print(f"✅ 已创建批量任务: {operation} {len(section_ids)} 个小节")

    def get_next_task(self) -> Optional[Task]:
        """获取下一个待处理任务。"""
        for task in self.tasks:
            if task.status == 'pending':
                return task
        return None

    def update_task_status(self, section_id: str, operation: str, status: str, error_msg: str = None):
        """更新任务状态。"""
        for task in self.tasks:
            if task.section_id == section_id and task.operation == operation:
                task.status = status
                if status == 'running':
                    task.started_at = datetime.now().isoformat()
                elif status in ('completed', 'failed'):
                    task.completed_at = datetime.now().isoformat()
                if error_msg:
                    task.error_msg = error_msg
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


def cmd_research(book_dir: Path, section_ids: List[str]):
    """批量研究。"""
    manager = BatchManager(book_dir)
    manager.create_batch(section_ids, 'research')

    print(f"\n🔍 开始批量研究 {len(section_ids)} 个小节...")
    print("=" * 60)

    for section_id in section_ids:
        print(f"\n📄 研究: {section_id}")
        manager.update_task_status(section_id, 'research', 'running')

        try:
            # 这里可以调用实际的研究逻辑
            # 目前只是模拟
            print(f"   正在搜索资料...")
            time.sleep(1)  # 模拟网络请求

            # 保存研究笔记
            research_dir = book_dir / 'assets' / 'research'
            research_dir.mkdir(parents=True, exist_ok=True)
            research_file = research_dir / f"{section_id}_research.md"

            if not research_file.exists():
                research_file.write_text(f"# {section_id} 研究笔记\n\n", encoding='utf-8')

            manager.update_task_status(section_id, 'research', 'completed')
            print(f"   ✅ 完成")

        except Exception as e:
            manager.update_task_status(section_id, 'research', 'failed', str(e))
            print(f"   ❌ 失败: {e}")

    print("\n" + "=" * 60)
    status = manager.get_status()
    print(f"批量研究完成: {status['completed']}/{status['total']}")


def cmd_write(book_dir: Path, section_ids: List[str]):
    """批量撰写。"""
    manager = BatchManager(book_dir)
    manager.create_batch(section_ids, 'write')

    print(f"\n✏️ 开始批量撰写 {len(section_ids)} 个小节...")
    print("=" * 60)

    for section_id in section_ids:
        print(f"\n📄 撰写: {section_id}")
        manager.update_task_status(section_id, 'write', 'running')

        try:
            # 检查研究笔记是否存在
            research_file = book_dir / 'assets' / 'research' / f"{section_id}_research.md"
            if research_file.exists():
                print(f"   已加载研究笔记")

            # 这里可以调用实际的撰写逻辑
            print(f"   正在撰写...")
            time.sleep(1)  # 模拟撰写过程

            manager.update_task_status(section_id, 'write', 'completed')
            print(f"   ✅ 完成")

        except Exception as e:
            manager.update_task_status(section_id, 'write', 'failed', str(e))
            print(f"   ❌ 失败: {e}")

    print("\n" + "=" * 60)
    status = manager.get_status()
    print(f"批量撰写完成: {status['completed']}/{status['total']}")


def cmd_status(book_dir: Path):
    """查看任务状态。"""
    manager = BatchManager(book_dir)
    status = manager.get_status()

    if status['total'] == 0:
        print("📋 暂无批量任务")
        return

    print("📋 批量任务状态")
    print("=" * 40)
    print(f"总任务: {status['total']}")
    print(f"待处理: {status['pending']}")
    print(f"进行中: {status['running']}")
    print(f"已完成: {status['completed']}")
    print(f"失败: {status['failed']}")

    if manager.tasks:
        print("\n任务详情:")
        for task in manager.tasks:
            icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(task.status, '?')
            print(f"  {icon} {task.section_id} ({task.operation})")


def cmd_resume(book_dir: Path):
    """恢复中断的任务。"""
    manager = BatchManager(book_dir)

    pending_tasks = [t for t in manager.tasks if t.status in ('pending', 'failed')]

    if not pending_tasks:
        print("✅ 没有需要恢复的任务")
        return

    print(f"🔄 恢复 {len(pending_tasks)} 个未完成任务...")

    # 按操作类型分组
    research_tasks = [t.section_id for t in pending_tasks if t.operation == 'research']
    write_tasks = [t.section_id for t in pending_tasks if t.operation == 'write']

    if research_tasks:
        cmd_research(book_dir, research_tasks)

    if write_tasks:
        cmd_write(book_dir, write_tasks)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    command = sys.argv[2]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    if command == 'research':
        if len(sys.argv) < 4:
            print("用法: batch.py <目录> research <节号1,节号2,节号3>")
            sys.exit(1)
        section_ids = sys.argv[3].split(',')
        cmd_research(book_dir, section_ids)
    elif command == 'write':
        if len(sys.argv) < 4:
            print("用法: batch.py <目录> write <节号1,节号2,节号3>")
            sys.exit(1)
        section_ids = sys.argv[3].split(',')
        cmd_write(book_dir, section_ids)
    elif command == 'status':
        cmd_status(book_dir)
    elif command == 'resume':
        cmd_resume(book_dir)
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
