# 命令详解

本文档包含 book-writer skill 所有命令的详细说明。

---

## 多Agent架构概述

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

| Agent | 职责 | 可并行数 | 输出 |
|-------|------|---------|------|
| **Master** | 任务分配、进度追踪、质量控制 | 1 | 整体进度 |
| **Research** | NotebookLM查询、资料收集 | 3-5 | research.md |
| **Writing** | 章节撰写、风格统一 | 2-3 | chapter.md |
| **Review** | 内容审查、事实核查 | 3-5 | review_report.md |
| **Editor** | 格式校对、术语统一 | 2-3 | 修订建议 |

---

## 1. 并行批量处理命令

### `/book-writer batch research <节号> [--parallel=N]`

使用多个Research Agent并行研究多个章节。

**参数：**
- `节号`：支持逗号分隔、部分名称或 `all`
- `--parallel=N`：并行Agent数量（默认3，最大5）

**示例：**

```bash
# 同时研究5个章节
python .claude/skills/book-writer/scripts/batch.py . research 1.1,1.2,1.3,1.4,1.5 --parallel=5

# 研究第一部分所有章节
python .claude/skills/book-writer/scripts/batch.py . research part1 --parallel=5

# 研究全书
python .claude/skills/book-writer/scripts/batch.py . research all --parallel=5
```

**执行逻辑：**
1. Master Agent创建任务队列
2. 启动N个Research Agent并行处理
3. 每个Agent独立完成NotebookLM查询
4. 自动保存研究笔记到 `assets/research/`
5. 实时更新任务状态和进度

---

### `/book-writer batch write <节号> [--parallel=N]`

使用多个Writing Agent并行撰写多个章节。

**示例：**

```bash
# 同时撰写3个章节
python .claude/skills/book-writer/scripts/batch.py . write 1.1,1.2,1.3 --parallel=3

# 撰写第一部分所有章节
python .claude/skills/book-writer/scripts/batch.py . write part1 --parallel=3
```

**注意事项：**
- 撰写前需确保已完成研究（有research.md）
- 每个Agent独立读取纲要、研究笔记和风格指南
- 输出文件实时写入磁盘

---

### `/book-writer batch review <节号> [--parallel=N]`

使用多个Review Agent并行审查多个章节。

**示例：**

```bash
# 同时审查5个章节
python .claude/skills/book-writer/scripts/batch.py . review 1.1,1.2,1.3,1.4,1.5 --parallel=5

# 审查所有章节
python .claude/skills/book-writer/scripts/batch.py . review all --parallel=5
```

---

### `/book-writer batch proofread <节号> [--parallel=N]`

使用多个Editor Agent并行校对多个章节。

**示例：**

```bash
# 同时校对3个章节
python .claude/skills/book-writer/scripts/batch.py . proofread 1.1,1.2,1.3 --parallel=3

# 校对所有章节
python .claude/skills/book-writer/scripts/batch.py . proofread all --parallel=3
```

---

## 2. 单Agent命令

### `/book-writer research <节号>`

针对某节做 NotebookLM 研究，产出研究笔记。

**执行步骤：**

1. 读取 `references/research-topics.md` 获取该节的研究主题清单
2. 读取 `references/outline.md` 获取该节的纲要描述
3. 使用 `/notebooklm` skill 查询 NotebookLM 知识库获取资料
4. 将研究结果写入 `assets/research/<节号>_research.md`
5. 更新该节文件的 frontmatter status 为 `researched`

**NotebookLM 查询示例：**

```
/notebooklm 查询 OpenClaw 的安装方法
/notebooklm 查询 GEPA 框架的详细解释
/notebooklm 查询 Moltbook 的AI社交行为案例
```

**底层调用：**
```bash
python .claude/skills/book-writer/scripts/research_agent.py . <节号>
```

---

### `/book-writer write <节号>`

加载纲要 + 研究笔记，撰写该节正文。

**执行步骤：**

1. 读取 `references/section-map.md` 确认该节的文件路径和目标字数
2. 读取 `references/outline.md` 获取该节纲要内容
3. 读取 `references/style-guide.md` 获取写作风格要求
4. 读取 `assets/research/<节号>_research.md`（如存在）获取研究笔记
5. 读取前一节的正文（如存在）确保衔接连贯
6. 撰写正文，遵循以下结构：
   - 以痛点/钩子开头，抓住读者注意力
   - 解释核心概念，用类比和场景化表达
   - 给出具体例子和代码示例
   - 实用总结，自然过渡到下一节
7. 写入对应的章节文件
8. 更新 frontmatter：status → `draft`，word_count → 实际字数

**写作模式：**
- **全自动模式**：序章、实战案例等 → 直接完成写作
- **分步确认模式**：核心技术概念节 → 写完后请用户审阅确认

**底层调用：**
```bash
python .claude/skills/book-writer/scripts/writing_agent.py . <节号>
```

---

### `/book-writer review <节号>`

从 6 个维度审查已撰写的内容。

**审查维度：**

1. **完整性**：对照纲要，检查是否覆盖了所有要求的内容点
2. **准确性**：事实性内容（数据、日期、仓库地址）是否正确
3. **风格**：是否符合 style-guide 要求（对话式、场景化、有节奏感）
4. **衔接**：与前后节的过渡是否自然
5. **字数**：是否在目标范围内（±20%）
6. **示例**：代码和案例是否充实、原创、可运行

**执行步骤：**

1. 读取该节正文
2. 读取 `references/style-guide.md` 和 `references/outline.md`
3. 逐维度评分（通过/需改进）并给出具体修改建议
4. 如全部通过，更新 frontmatter status → `reviewed`
5. 如需修改，列出修改清单，等待用户决定

**底层调用：**
```bash
python .claude/skills/book-writer/scripts/review_agent.py . <节号>
```

---

### `/book-writer proofread <节号>`

责任编辑校对检查（三审三校流程）。

**检查内容：**
- 术语一致性（OpenClaw、Gateway、Agent 等大小写）
- 禁用词（"本节将介绍""综上所述"等学术腔）
- 格式规范（代码块语言标记、段落长度）
- 内容质量（字数、代码示例、图表）

**底层调用：**
```bash
python .claude/skills/book-writer/scripts/editor_agent.py . <节号>
```

---

## 3. Master Agent 命令

### `/book-writer progress`

显示全书进度表。

```bash
python .claude/skills/book-writer/scripts/master.py . status
```

**输出示例：**
```
======================================================================
📚 《OpenClaw：自进化AI完全指南》写作进度报告
======================================================================

总体进度: [████████████████░░░░░░░░░░░░░░] 50% (30/60 节完成)
总字数: 45,000 / 90,000 目标字数

          状态分布
----------------------------------------
  📋 纲要        10 节
  🔍 已研究      20 节
  ✏️ 初稿        15 节
  ✅ 已审查      12 节
  🎉 定稿         3 节
```

---

### `/book-writer plan`

生成写作计划，显示当前阶段和下一步建议。

```bash
python .claude/skills/book-writer/scripts/master.py . plan
```

---

### `/book-writer assemble <章号>`

将各小节合并为完整章节。

```bash
python .claude/skills/book-writer/scripts/master.py . assemble <章号>
```

章号对应：
- `0` = 序章
- `1` = 第一部分（第1-3章）
- `2` = 第二部分（第4-8章）
- `3` = 第三部分（第9-11章）
- `4` = 第四部分（第12-13章）
- `5` = 终章
- `6` = 附录

组装后通读检查：小节间过渡是否自然，术语是否统一。

---

### `/book-writer export`

将完整章节导出为 PDF。

```bash
# 先组装所有章节
python .claude/skills/book-writer/scripts/master.py . assemble 0
python .claude/skills/book-writer/scripts/master.py . assemble 1
python .claude/skills/book-writer/scripts/master.py . assemble 2

# 然后使用 md2pdf skill 导出
/md2pdf 第一章.md
```

---

## 4. 批量任务管理

### 查看批量任务状态

```bash
python .claude/skills/book-writer/scripts/batch.py . status
```

**输出：**
```
📊 批量任务状态
==================================================
总任务: 15
  ⏳ 待处理: 5
  🔄 进行中: 3
  ✅ 已完成: 7
  ❌ 失败: 0

📝 任务详情:

  🔄 RUNNING:
    - 1.3 (research) [Agent-2]
    - 1.5 (research) [Agent-3]

  ⏳ PENDING:
    - 1.4 (research) [Agent-1]
    ...
```

---

### 恢复中断的任务

如果批量任务因网络中断或其他原因停止，可以恢复：

```bash
python .claude/skills/book-writer/scripts/batch.py . resume --parallel=3
```

系统会自动检测未完成的任务并继续执行。

---

## 5. 辅助工具命令

### 术语表查询

```bash
python .claude/skills/book-writer/scripts/editor_agent.py . terminology
```

### 出版检查清单

```bash
python .claude/skills/book-writer/scripts/editor_agent.py . checklist
```

---

## 6. 并行写作最佳实践

### 阶段1：并行研究

第一部分各小节无依赖，可全部并行：

```bash
# 研究第一部分所有章节
python .claude/skills/book-writer/scripts/batch.py . research part1 --parallel=5

# 研究第二部分所有章节
python .claude/skills/book-writer/scripts/batch.py . research part2 --parallel=5
```

### 阶段2：并行撰写

```bash
# 撰写第一部分（各章节独立）
python .claude/skills/book-writer/scripts/batch.py . write part1 --parallel=3

# 撰写第二部分实战章节
python .claude/skills/book-writer/scripts/batch.py . write part2 --parallel=3
```

### 阶段3：并行审查

```bash
# 同时审查多个章节
python .claude/skills/book-writer/scripts/batch.py . review all --parallel=5
```

### 阶段4：并行校对

```bash
# 同时校对多个章节
python .claude/skills/book-writer/scripts/batch.py . proofread all --parallel=3
```

---

## 7. 断点续传与容错

### 断点续传

所有操作都会实时保存状态到 `.batch_state.json`，网络中断后可无缝恢复：

```bash
# 查看当前任务状态
python .claude/skills/book-writer/scripts/batch.py . status

# 恢复未完成的任务
python .claude/skills/book-writer/scripts/batch.py . resume --parallel=3
```

### 并发冲突处理

- **同一章节**：同一时间只能有一个Agent写入（通过文件锁）
- **不同章节**：可完全并行，无冲突
- **状态同步**：使用线程锁保证状态文件一致性

---

## 8. 工作流程示例

### 完整写作流程

```bash
# 1. 查看当前进度
python .claude/skills/book-writer/scripts/master.py . status

# 2. 并行研究第一部分
python .claude/skills/book-writer/scripts/batch.py . research part1 --parallel=5

# 3. 并行撰写第一部分
python .claude/skills/book-writer/scripts/batch.py . write part1 --parallel=3

# 4. 并行审查第一部分
python .claude/skills/book-writer/scripts/batch.py . review part1 --parallel=5

# 5. 查看进度
python .claude/skills/book-writer/scripts/master.py . status

# 6. 组装第一部分
python .claude/skills/book-writer/scripts/master.py . assemble 1

# 7. 继续下一部分...
```

---

## 附录：Agent 脚本直接调用

| Agent | 脚本路径 | 用法 |
|-------|---------|------|
| Master | `scripts/master.py` | `python master.py . status` |
| Research | `scripts/research_agent.py` | `python research_agent.py . 1.1` |
| Writing | `scripts/writing_agent.py` | `python writing_agent.py . 1.1` |
| Review | `scripts/review_agent.py` | `python review_agent.py . 1.1` |
| Editor | `scripts/editor_agent.py` | `python editor_agent.py . 1.1` |
| Batch | `scripts/batch.py` | `python batch.py . research 1.1,1.2 --parallel=2` |
| Progress | `scripts/progress.py` | `python progress.py .` |
