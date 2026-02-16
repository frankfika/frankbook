#!/usr/bin/env python3
"""
共用工具函数

提供所有Agent共享的工具函数。
"""

import re
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime


# 标准章节目录映射
CHAPTER_DIRS = {
    "序章": ["0.1"],
    "第一部分": ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4"],
    "第二部分": ["4.1", "4.2", "4.3", "4.4", "4.5", "5.1", "5.2", "5.3", "5.4",
                 "6.1", "6.2", "6.3", "6.4", "7.1", "7.2", "7.3", "7.4"],
    "第三部分": ["8.1", "8.2", "8.3", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6",
                 "10.1", "10.2", "10.3", "10.4", "10.5", "10.6"],
    "第四部分": ["11.1", "11.2", "11.3", "11.4", "12.1", "12.2", "12.3", "12.4",
                 "13.1", "13.2", "13.3"],
    "终章": ["14.1", "14.2", "14.3", "15.1", "15.2"],
    "附录": ["A.1", "A.2", "A.3", "A.4"],
}

# 节号到章节的反向映射
SECTION_TO_CHAPTER = {}
for chapter, sections in CHAPTER_DIRS.items():
    for section in sections:
        SECTION_TO_CHAPTER[section] = chapter


def parse_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """
    解析Markdown文件的YAML frontmatter。

    Args:
        content: Markdown文件内容

    Returns:
        frontmatter字典，如果没有则返回None
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None

    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            fm[key] = value
    return fm


def update_frontmatter(file_path: Path, updates: Dict[str, Any]) -> bool:
    """
    更新Markdown文件的frontmatter。

    Args:
        file_path: 文件路径
        updates: 要更新的键值对

    Returns:
        是否成功更新
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        for key, value in updates.items():
            pattern = rf'^{re.escape(key)}:\s*.+$'
            replacement = f'{key}: {value}'

            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                # 在frontmatter末尾添加
                content = re.sub(
                    r'^(---\s*\n.*?)\n---\s*\n',
                    rf'\1\n{replacement}\n---\n',
                    content,
                    flags=re.DOTALL
                )

        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"更新frontmatter失败: {e}")
        return False


def count_words(content: str) -> int:
    """
    统计Markdown文件的字数（排除frontmatter）。

    Args:
        content: Markdown内容

    Returns:
        字数统计
    """
    # 移除frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # 移除Markdown标记
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)  # 图片
    content = re.sub(r'\[.*?\]\(.*?\)', ' ', content)  # 链接
    content = re.sub(r'[#*`]', '', content)  # 标记符号

    # 中文字符 + 英文单词
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))

    return chinese_chars + english_words


def find_section_file(book_dir: Path, section_id: str) -> Optional[Path]:
    """
    根据节号查找小节文件。

    Args:
        book_dir: 书籍根目录
        section_id: 节号，如 "1.1"

    Returns:
        文件路径，如果未找到则返回None
    """
    chapter_name = SECTION_TO_CHAPTER.get(section_id)
    if chapter_name:
        chapter_path = book_dir / chapter_name
        if chapter_path.exists():
            for md_file in chapter_path.glob("*.md"):
                if section_id in md_file.name:
                    return md_file

    # 如果没找到，遍历所有目录
    for chapter_name in CHAPTER_DIRS.keys():
        chapter_path = book_dir / chapter_name
        if chapter_path.exists():
            for md_file in chapter_path.glob("*.md"):
                if section_id in md_file.name:
                    return md_file

    return None


def get_section_info(book_dir: Path, section_id: str) -> Optional[Dict[str, Any]]:
    """
    获取小节的详细信息。

    Args:
        book_dir: 书籍根目录
        section_id: 节号

    Returns:
        小节信息字典
    """
    file_path = find_section_file(book_dir, section_id)
    if not file_path or not file_path.exists():
        return None

    content = file_path.read_text(encoding='utf-8')
    fm = parse_frontmatter(content)

    if not fm:
        return None

    return {
        'section_id': section_id,
        'file_path': file_path,
        'title': fm.get('title', file_path.stem),
        'status': fm.get('status', 'outline'),
        'word_count': int(fm.get('word_count', 0)),
        'target_words': int(fm.get('target_words', 0)),
        'chapter': file_path.parent.name,
    }


def get_all_sections(book_dir: Path) -> List[Dict[str, Any]]:
    """
    获取所有小节的信息。

    Args:
        book_dir: 书籍根目录

    Returns:
        小节信息列表
    """
    sections = []

    for chapter_name in CHAPTER_DIRS.keys():
        chapter_path = book_dir / chapter_name
        if not chapter_path.exists():
            continue

        for md_file in sorted(chapter_path.glob("*.md")):
            # 跳过组装后的文件
            if "_完整" in md_file.name or "_第" in md_file.name:
                continue

            info = get_section_info(book_dir, md_file.stem.split('_')[0])
            if info:
                sections.append(info)

    return sections


def expand_section_range(section_arg: str) -> List[str]:
    """
    展开节号参数。

    支持:
    - 单个节号: "1.1"
    - 逗号分隔: "1.1,1.2,1.3"
    - 范围: "1.1-1.5"
    - 部分名称: "part1", "part2", "all"

    Args:
        section_arg: 节号参数

    Returns:
        展开的节号列表
    """
    # 部分映射
    part_sections = {
        "part1": CHAPTER_DIRS["第一部分"],
        "part2": CHAPTER_DIRS["第二部分"],
        "part3": CHAPTER_DIRS["第三部分"],
        "part4": CHAPTER_DIRS["第四部分"],
        "part5": CHAPTER_DIRS["终章"],
        "all": [],
    }

    # 构建all列表
    for sections in CHAPTER_DIRS.values():
        part_sections["all"].extend(sections)

    # 检查是否是部分名称
    if section_arg.lower() in part_sections:
        return part_sections[section_arg.lower()]

    # 检查是否是范围
    if '-' in section_arg:
        start, end = section_arg.split('-', 1)
        # 这里可以实现范围展开逻辑
        return [start.strip(), end.strip()]

    # 逗号分隔
    return [s.strip() for s in section_arg.split(',')]


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    格式化时间戳。

    Args:
        dt: datetime对象，默认为当前时间

    Returns:
        格式化后的字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本。

    Args:
        text: 原始文本
        max_length: 最大长度

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def ensure_dir(path: Path) -> Path:
    """
    确保目录存在。

    Args:
        path: 目录路径

    Returns:
        目录路径
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(file_path: Path) -> Optional[Dict]:
    """
    加载JSON文件。

    Args:
        file_path: 文件路径

    Returns:
        解析后的字典，失败返回None
    """
    try:
        if file_path.exists():
            return json.loads(file_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"加载JSON失败: {e}")
    return None


def save_json(file_path: Path, data: Dict, indent: int = 2) -> bool:
    """
    保存JSON文件。

    Args:
        file_path: 文件路径
        data: 要保存的数据
        indent: 缩进

    Returns:
        是否成功
    """
    try:
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=indent),
            encoding='utf-8'
        )
        return True
    except Exception as e:
        print(f"保存JSON失败: {e}")
        return False


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.progress_file = self.book_dir / '.claude' / 'skills' / 'book-writer' / 'assets' / 'progress.json'
        ensure_dir(self.progress_file.parent)
        self.data = self._load()

    def _load(self) -> Dict:
        """加载进度数据。"""
        data = load_json(self.progress_file)
        if data is None:
            data = {
                'created_at': format_timestamp(),
                'sections': {},
            }
        return data

    def save(self):
        """保存进度数据。"""
        self.data['updated_at'] = format_timestamp()
        save_json(self.progress_file, self.data)

    def update_section(self, section_id: str, **kwargs):
        """更新小节进度。"""
        if section_id not in self.data['sections']:
            self.data['sections'][section_id] = {}

        self.data['sections'][section_id].update(kwargs)
        self.data['sections'][section_id]['updated_at'] = format_timestamp()
        self.save()

    def get_section(self, section_id: str) -> Dict:
        """获取小节进度。"""
        return self.data['sections'].get(section_id, {})

    def get_all_sections(self) -> Dict[str, Dict]:
        """获取所有小节进度。"""
        return self.data['sections']
