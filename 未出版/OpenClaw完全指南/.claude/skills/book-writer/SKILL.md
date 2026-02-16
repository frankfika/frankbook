---
name: book-writer
description: |
  书籍写作助手，管理《OpenClaw：自进化AI完全指南》的研究、撰写、审查和组装全流程。
  使用多Agent架构支持并行写作，提高创作效率。
  使用场景：写书、写章节、研究章节、书本进度查询、组装章节、审查内容、导出PDF。
---

# Book Writer - OpenClaw：自进化AI完全指南

## 项目路径

```
书籍项目根目录: /Users/fangchen/Baidu/个人空间/4、书籍和重要文章/未出版/opencrawl完全指南/
Skill 目录: .claude/skills/book-writer/
```

## 知识库配置

**NotebookLM 知识库**: https://notebooklm.google.com/notebook/83bf6e20-507c-41df-ae77-9eca55e615e0

研究时使用 `/notebooklm` skill 查询此知识库获取OpenClaw相关资料。

---

## 多Agent架构设计

本书籍写作系统采用**多Agent并行架构**，将写作流程拆解为可独立运行的子任务：

```
┌─────────────────────────────────────────────────────────────┐
│                    Book Writer Master                        │
│                     (主协调Agent)                            │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
    ┌──────────▼──────────┐      ┌───────────▼────────────┐
    │   Research Agent    │      │    Writing Agent       │
    │    (研究专用)        │      │     (写作专用)          │
    │  context: fork      │      │   context: fork        │
    └──────────┬──────────┘      └───────────┬────────────┘
               │                              │
    ┌──────────▼──────────┐      ┌───────────▼────────────┐
    │   Review Agent      │      │   Editor Agent         │
    │    (审查专用)        │      │     (校对专用)          │
    │  context: fork      │      │   context: fork        │
    └─────────────────────┘      └────────────────────────┘
```

### Agent 分工

| Agent | 职责 | 可并行数 | 输出 |
|-------|------|---------|------|
| **Master** | 任务分配、进度追踪、质量控制 | 1 | 整体进度 |
| **Research** | NotebookLM查询、资料收集 | 3-5 | research.md |
| **Writing** | 章节撰写、风格统一 | 2-3 | chapter.md |
| **Review** | 内容审查、事实核查 | 3-5 | review_report.md |
| **Editor** | 格式校对、术语统一 | 2-3 | 修订建议 |

---

## 快速开始

### 并行研究多个章节（推荐）

```bash
# 同时启动3个Research Agent研究不同章节
/book-writer research 1.1,1.2,1.3 --parallel=3

# 或研究同一部分的所有章节
/book-writer research part1 --parallel
```

### 并行撰写独立章节

```bash
# 同时撰写已研究完成的章节
/book-writer write 1.1,1.2,1.3 --parallel=3
```

### 审查与校对

```bash
# 并行审查多个章节
/book-writer review 1.1,1.2,1.3 --parallel=3

# 并行校对
/book-writer proofread 1.1,1.2,1.3 --parallel=3
```

### 查看全书进度

```bash
/book-writer progress
```

### 组装章节

```bash
/book-writer assemble 1
```

---

## 命令速查

| 命令 | 功能 | Agent类型 | 可并行 |
|------|------|-----------|--------|
| `research <节号>` | NotebookLM研究 | Research Agent | ✅ |
| `write <节号>` | 撰写该节正文 | Writing Agent | ✅ |
| `review <节号>` | 6维度审查 | Review Agent | ✅ |
| `proofread <节号>` | 责任编辑校对 | Editor Agent | ✅ |
| `progress` | 显示全书进度表 | Master Agent | - |
| `assemble <章号>` | 合并小节为完整章节 | Master Agent | - |
| `export` | 导出完整书籍为PDF | Master Agent | - |
| `batch <操作> <范围>` | 批量处理多个章节 | Multi-Agent | ✅ |

**完整命令文档**: 见 [references/COMMANDS.md](references/COMMANDS.md)

---

## 并行写作最佳实践

### 阶段1：并行研究（Phase 1-2）

第一部分各小节无依赖，可全部并行：

```bash
# 研究第一部分所有章节
/book-writer batch research part1 --parallel=5

# 或指定具体章节
/book-writer research 1.1,1.2,1.3,2.1,2.2,2.3,3.1,3.2,3.3,3.4 --parallel=5
```

### 阶段2：并行撰写（Phase 3-4）

```bash
# 撰写第一部分（各章节独立）
/book-writer batch write part1 --parallel=3

# 撰写第二部分实战章节
/book-writer batch write part2 --parallel=3
```

### 阶段3：并行审查（Phase 5）

```bash
# 同时审查多个章节
/book-writer batch review all --parallel=5
```

---

## 书籍结构

基于纲要：`OpenClaw-自进化AI完全指南-大纲.md`

| 部分 | 章节 | 内容概要 | 目标字数 | 依赖 |
|------|------|---------|---------|------|
| 序章 | - | 当AI有了"手"和"脚" | 3,000 | 无 |
| 第一部分 | 第1-3章 | 认识OpenClaw（历史、概念、架构） | 25,000 | 无 |
| 第二部分 | 第4-10章 | 实战指南（4招+案例） | 40,000 | 第一部分 |
| 第三部分 | 第11-13章 | 进阶主题（Moltbook、安全、OPC） | 25,000 | 第二部分 |
| 第四部分 | 第14-15章 | 未来与展望 | 15,000 | 第三部分 |
| 终章 | - | 现在就开始 | 2,000 | 无 |
| 附录 | A-D | 命令速查、配置示例等 | 5,000 | 无 |

**全书总计**: 约12万字

---

## 文件状态流转

```
outline（仅 frontmatter）
    ↓
[并行研究] → researched（已研究，有研究笔记）
    ↓
[并行撰写] → draft（已撰写初稿）
    ↓
[并行审查] → reviewed（已审查通过）
    ↓
[并行校对] → proofread（已校对）
    ↓
final（定稿）
```

---

## 多Agent任务分配策略

### 策略1：按章节并行（推荐）

独立章节可同时处理：
- 第1章各小节可并行研究/撰写
- 第4-10章实战部分可并行
- 案例集锦章节可并行

### 策略2：按阶段流水线

```
Research Agent 1 → Writing Agent 1 → Review Agent 1
Research Agent 2 → Writing Agent 2 → Review Agent 2
Research Agent 3 → Writing Agent 3 → Review Agent 3
```

### 策略3：混合模式

- 先并行完成所有研究
- 再并行撰写所有章节
- 最后并行审查

---

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/outline.md` | 书本纲要（内容要求权威来源，可调整） |
| `references/style-guide.md` | 写作风格指南（通俗易懂、深入浅出、实践为主） |
| `references/research-topics.md` | 各节研究主题清单 |
| `references/section-map.md` | 小节→文件路径→组装顺序映射（可调整） |
| `references/editor-checklist.md` | 责任编辑出版检查清单（三审三校） |
| `references/glossary.md` | 术语表（确保全文用词一致） |
| `references/COMMANDS.md` | 完整命令文档 |

---

## 目录结构

```
.claude/skills/book-writer/
├── SKILL.md                    # 本文件
├── references/
│   ├── outline.md              # 书籍纲要
│   ├── style-guide.md          # 写作风格指南
│   ├── research-topics.md      # 研究主题清单
│   ├── section-map.md          # 章节映射表
│   ├── editor-checklist.md     # 出版检查清单
│   ├── glossary.md             # 术语表
│   └── COMMANDS.md             # 完整命令文档
├── scripts/
│   ├── master.py               # 主协调Agent
│   ├── research_agent.py       # 研究Agent
│   ├── writing_agent.py        # 写作Agent
│   ├── review_agent.py         # 审查Agent
│   ├── editor_agent.py         # 校对Agent
│   ├── progress.py             # 进度追踪
│   ├── assemble.py             # 章节组装
│   ├── batch.py                # 批量处理（多Agent调度）
│   └── utils.py                # 共用工具
└── assets/
    └── research/               # 研究笔记存放处
```

---

## 版权合规

- 案例引用改写为原创叙述，标注来源
- 技术文档消化重述，不大段照搬
- 代码示例原创编写
- 关键数据在正文中标注来源

---

## 容错与并发机制

### 断点续传

所有操作都会实时保存状态到文件，网络中断后可无缝恢复：

- **研究阶段**: `assets/research/<节号>_research.md` 自动保存
- **写作阶段**: 章节文件实时写入磁盘
- **状态追踪**: `progress.json` 记录所有小节状态
- **恢复方式**: 重新运行相同命令，自动检测已完成的步骤

### 并发冲突处理

- **同一章节**: 同一时间只能有一个Agent写入
- **不同章节**: 可完全并行，无冲突
- **资源锁定**: 使用文件锁防止同时写入

---

## 研究流程

本书研究主要依赖 **Google NotebookLM** 知识库：

1. 使用 `/notebooklm` skill 查询资料
2. 将关键信息整理到 `assets/research/<节号>_research.md`
3. 标注信息来源（NotebookLM中的哪个文档）
4. 撰写时引用研究笔记

### NotebookLM 查询示例

```
/notebooklm 查询 OpenClaw 的安装方法
/notebooklm 查询 GEPA 框架的详细解释
/notebooklm 查询 Moltbook 的AI社交行为案例
```

---

## 多Agent命令示例

### 批量研究

```bash
# 研究第一部分所有章节（5个Agent并行）
python .claude/skills/book-writer/scripts/batch.py research part1 --parallel=5

# 研究指定章节（3个Agent并行）
python .claude/skills/book-writer/scripts/batch.py research 1.1,1.2,1.3 --parallel=3
```

### 批量撰写

```bash
# 撰写所有已研究的章节（3个Agent并行）
python .claude/skills/book-writer/scripts/batch.py write part1 --parallel=3
```

### 批量审查

```bash
# 审查所有章节（5个Agent并行）
python .claude/skills/book-writer/scripts/batch.py review all --parallel=5
```
