---
name: book-writer
description: |
  书籍写作助手，管理 OPC 2.0 书籍的研究、撰写、审查和组装全流程。
  使用场景：写书、写章节、研究章节、书本进度查询、组装章节、审查内容、导出PDF、生成大纲。
---

# Book Writer - OPC 2.0 书籍写作助手

## 项目路径

```
书籍项目根目录（即当前工作目录）: /Users/fangchen/Baidu/个人空间/4、书籍和重要文章/未出版/OPC 2.0时代：用 Agent Skills 重塑智能体工作流/
Skill 目录（项目级）: .claude/skills/book-writer/
```

## 快速开始

```bash
# 查看全书进度
/book-writer progress

# 研究某节（收集资料）
/book-writer research <节号>

# 撰写某节
/book-writer write <节号>

# 审查某节
/book-writer review <节号>

# 校对某节（三审三校）
/book-writer proofread <节号>

# 组装章节
/book-writer assemble <章号>

# 导出PDF
/book-writer export
```

## 命令速查

| 命令 | 功能 | 示例 |
|------|------|------|
| `research <节号>` | 网络研究，产出研究笔记 | `research 1.1.1` |
| `write <节号>` | 撰写该节正文 | `write 1.1.1` |
| `review <节号>` | 6维度审查内容质量 | `review 1.1.1` |
| `proofread <节号>` | 责任编辑校对检查 | `proofread 1.1.1` |
| `progress` | 显示全书进度表 | `progress` |
| `assemble <章号>` | 合并小节为完整章节 | `assemble 1` |
| `export` | 导出完整书籍为PDF | `export` |
| `init <节号> <标题>` | 初始化新小节 | `init 1.1.5 "新小节标题"` |
| `restructure` | 重组目录结构 | `restructure` |
| `diagram <类型> <路径>` | 生成架构图 | `diagram skill-arch 第一章/images/arch` |

**完整命令文档**: 见 [references/COMMANDS.md](references/COMMANDS.md)

## 文件状态流转

```
outline（仅 frontmatter）
    ↓
researched（已研究，有研究笔记）
    ↓
draft（已撰写初稿）
    ↓
reviewed（已审查通过）
    ↓
final（定稿）
```

## 写作顺序建议

| 阶段 | 章节 | 说明 |
|------|------|------|
| Phase 1 | 引言, 1.1.1, 1.1.2, 1.1.3 | 基础铺垫，研究量小 |
| Phase 2 | 1.2.1, 1.2.2, 1.2.3, 1.2.4 | 核心概念，需大量研究 |
| Phase 3 | 2.1, 2.2.1~2.2.7, 2.3.1~2.3.3 | 解剖 Skill |
| Phase 4 | 3.1~3.7, 4.1~4.8 | Skills 目录 |
| Phase 5 | 第三章 1.1~2.5 | 高阶实战 |

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
│   ├── progress.py             # 进度追踪
│   ├── assemble.py             # 章节组装
│   ├── validate.py             # 内容验证
│   ├── init.py                 # 初始化新小节
│   ├── restructure.py          # 目录重组
│   ├── diagram.py              # 生成架构图
│   ├── editor.py               # 责任编辑校对
│   └── batch.py                # 批量处理
└── assets/
    └── research/               # 研究笔记存放处
```

## 版权合规

- 案例引用改写为原创叙述，标注来源
- 技术文档消化重述，不大段照搬
- 代码示例原创编写
- 关键数据在正文中标注来源

## 容错与并发机制

### 断点续传

所有操作都会实时保存状态到文件，网络中断后可无缝恢复：

- **研究阶段**: `assets/research/<节号>_research.md` 自动保存
- **写作阶段**: 章节文件实时写入磁盘
- **状态追踪**: `progress.json` 记录所有小节状态
- **恢复方式**: 重新运行相同命令，自动检测已完成的步骤

### 并发处理

支持同时处理多个独立章节（研究阶段尤其有效）：

```bash
# 并发研究多个小节（推荐，无依赖关系）
/book-writer research 1.1.1
/book-writer research 1.1.2
/book-writer research 1.1.3
```

**注意**: 同一小节的 write 操作会覆盖，不要并发写同一文件。

## 灵活调整说明

本书的目录结构并非固定不变。在写作过程中，你可以：

1. **调整章节顺序**: 如果某些内容逻辑上更适合前置或后置
2. **合并或拆分小节**: 根据实际内容量调整颗粒度
3. **新增或删除章节**: 根据研究进展和读者需求
4. **调整字数目标**: 根据内容重要性和深度需求

任何结构调整都通过 `/book-writer restructure` 命令处理，确保所有映射文件保持一致。
