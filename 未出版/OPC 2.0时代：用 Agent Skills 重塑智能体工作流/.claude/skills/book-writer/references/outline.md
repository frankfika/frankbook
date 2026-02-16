# OPC 2.0时代：用 Agent Skills 重塑AI智能体工作流

> **纲要说明**：本大纲是初始框架，在写作过程中可根据研究进展和内容需要灵活调整。如果发现某些章节需要合并、拆分、新增或调整顺序，随时提出修改建议。

## 引言

OPC (One Person Company，一人公司) 的创业者都有这种经历：产品要自己设计，代码要自己写，市场要自己跑，周报要自己写，推文要自己发。每天在十几个角色之间切换，每个角色都要重新进入状态，重复着同样的工作——写代码时要回忆架构规范，写文案时要回忆品牌语气，做数据分析时要回忆查询模式。**这就是 OPC 的核心困境：一个人要完成一个团队的事，而且每次都要从零开始。**

AI 工具的出现本该解决这个问题，但现实是：ChatGPT、Claude 这些对话式 AI 虽然强大，但每次打开新对话都要从头输入背景信息，知识无法沉淀，经验不能复用。你教过 AI 如何写周报、如何审查代码、如何生成营销文案，但下周又得重新教一遍。**AI 没有记忆，就像一个每周一失忆的员工，你再优秀也带不动。**

Agent Skills 就是为了解决这个问题而生的——**它让 AI 学会你的"独门绝技"，把这些重复的工作模式固化成可复用的"数字员工"。** 你写一次周报模板，AI 以后每次都按这个格式生成；你定义一次代码审查标准，AI 以后每次都按这个流程检查。这不是什么高大上的概念，就是一个很实用的工具模式：你把经常做的事写成一个文件，AI 就按你的方法干活，省时省力，还不容易出错。

对 OPC 来说，这意味着你可以从"单兵作战"升级为"指挥官"——通过调用不同的 Skills，指挥一支由 PM、程序员、设计师、运营专员组成的"AI 团队"协同工作，而不再是一个人做所有事。这就是 Agent Skills 给 OPC 带来的质变。

---

# 第一章 认识 Agent Skill

## 1 Agent Skill 是什么

### 1.1 现实中遇到的问题

#### 1.1.1 重复性工作的痛点

每周写周报、每天回复类似邮件、每次会议都要整理纪要——这些重复性工作占据了大量时间。即使有了 AI 助手，你仍然需要一遍遍重复同样的指令（如表结构、过滤规则、特殊术语），不仅效率低下，还容易遗漏关键信息。Rakuten 财务部门的案例显示，手动处理财务报告需要一整天，而通过 Skill 自动化仅需一小时，效率提升 87.5%。本节将深入分析这些重复性场景的根源和解决方案。

#### 1.1.2 知识和经验的碎片化

你的宝贵经验散落在各个聊天记录中，想要复用却找不到；团队里的最佳实践在老员工脑子里，新员工只能重新摸索；项目知识没有沉淀，同样的错误反复出现。Agent Skill 被定义为"行为规范 + 专业知识 + 使用时机"的组合，相当于给 AI 发放的"数字化标准作业程序（SOP）"或"岗位操作手册"。本节探讨 Skill 如何将隐性知识转化为可传承的显性资产。

#### 1.1.3 提示词管理的困境

精心设计的提示词保存在哪里？如何分类整理？团队之间如何共享？随着提示词越来越多，管理变得越来越困难。更严重的是，每次调用都要重新加载完整上下文，导致 Token 爆炸和成本飙升。本节分析传统提示词工程的局限性，引出 Skill 的"渐进式披露"架构如何从根本上解决这个问题。

### 1.2 Agent Skill 的技术本质

#### 1.2.1 从Prompt到Skill：范式转变与核心价值

在 Skill 机制出现之前，用户每次执行特定任务都需要重复输入冗长的 Prompt，这些隐性知识散落在聊天记录中无法复用。Skill 的引入标志着从"手工作坊"到"工业化生产"的范式转变，实现了三大核心价值：**标准化**（固化经过验证的流程，确保输出质量一致）、**自动化**（结合脚本和 MCP 工具，实现智能自动化）、**可传承**（通过 Git 共享和插件市场，实现知识的跨时空传承）。更关键的是，通过"渐进式披露"架构，Claude 启动时只加载 Skill 的元数据（约 100 tokens），只有在需要时才加载详细指令。这使得 Claude 可以挂载成百上千个技能而不变笨或变慢，从根本上解决了"上下文窗口爆炸"问题。本节通过 Rakuten 财务自动化（效率提升 87.5%）和公众号数据抓取（30 分钟→5 分钟）等案例，说明 Skill 相对于 Prompt 的本质优势。

#### 1.2.2 Claude Code 与 Skill 的发展历程

**起源阶段（2024 年）**：Claude Code 最初是 Anthropic Labs 的内部研究项目，探索 AI 模型能力的边界。值得一提的是，Claude Code 自身的代码 100% 都是由 Claude Code 编写的，这被视为一种"自指性"的开发里程碑。**2025 年 2 月**：作为"代理式命令行工具"（Agentic CLI）首次发布研究预览版，与 Claude 3.7 Sonnet 一同推出。**2025 年 5 月**：全面上市（GA），随着 Claude 4 (Opus/Sonnet) 系列模型的发布，Claude Code 被誉为"AI 编码助手之王"。**2025 年 10 月 16 日**：这是一个历史性的时刻——Anthropic 正式推出 Claude Skills（Agent Skills）机制，同时支持 Claude.ai、Claude Code CLI 和 Claude API。**2025 年 11 月**：发布"Skills Explained"深度指南，确立了 Skill 的标准结构和渐进式加载机制。**2025 年 12 月**：Agent Skills 成为开放标准（agentskills.io），不再局限于 Anthropic，引导整个 AI Agent 生态。**2026 年 1 月**：Claude Code 2.1 重大更新，Skill 获得"热重载"、"上下文分叉"、"生命周期钩子"等增强功能，成为系统的一等公民。本节通过这个时间线，说明 Skill 机制是如何从"解决重复提示问题"演变为"AI 能力扩展标准"的。

#### 1.2.3 Progressive Disclosure架构原理

渐进式披露是 Skill 的核心技术，通过三级加载机制实现：**Level 1（元数据感知）**仅读取 name 和 description，让 Claude "知道自己会什么"；**Level 2（按需激活）**根据语义匹配自动加载 SKILL.md 正文；**Level 3（延迟加载）**仅在需要时读取参考文档或执行脚本。这种架构解决了传统 Prompt 工程的"上下文窗口爆炸"问题，同时配合 **context: fork**（独立会话运行）和 **hooks**（生命周期钩子）等高级特性，实现了灵活的上下文管理和自动化流程控制。本节详细解密这个架构的技术实现和性能优势。

#### 1.2.4 Skill、MCP、Subagents、Command 的对比与协同

**Skill**（决策层）：定义工作流和业务规则，提供"方法论"（如何使用能力）。例如 data-analysis Skill 定义"先查询 sales 表，然后运行脚本画图"的业务逻辑。**MCP**（执行层）：提供"能力"（API 接口、数据库连接）。例如 Postgres MCP 提供 query_db 工具，但不知道如何查询。**Subagents**（调度层）：独立的执行实体，通过 context: fork 在独立会话中运行，执行完毕后只返回结果，不污染主对话历史。主 Agent 负责协调，通过调用不同的"分身"并发处理复杂项目。**Command**（快捷层）：预定义的快捷指令集合（如 /commit、/deploy），提供一键执行的便捷入口，类似于命令行别名。这四者的关系是：Command 是用户触发的快捷方式，Skill 是封装的业务流程，MCP 是底层的工具能力，Subagents 是隔离的执行环境。本节通过对比表格和实例说明四者的职责边界、协作模式以及各自的最佳使用场景。

## 2 解剖 Agent Skill

### 2.1 核心组成架构

```
skill-name/
├── SKILL.md          # 核心：定义触发条件和执行逻辑
├── scripts/          # 脚本（Python、Bash等）
├── references/       # 参考文档（按需加载）
└── config.yaml       # 配置（可选）
```

这是一个典型的 Skill 目录结构。SKILL.md 是核心，通过 YAML Frontmatter 定义元数据，通过 Markdown 正文描述具体操作步骤；scripts 存放辅助脚本（如可视化工具 codebase-visualizer 的 scripts/visualize.py）；references 存放参考文档（如 pdf-processing 的 FORMS.md）；config.yaml 存放配置信息。本节详细说明每个部分的设计原则和使用场景。

### 2.2 SKILL.md 完整编写指南

#### 2.2.1 文件结构：YAML Frontmatter + Markdown 正文

SKILL.md 是 Skill 的核心文件，由两部分组成：**YAML Frontmatter**（文件顶部，用 `---` 包围）定义元数据配置（name、description、disable-model-invocation 等）；**Markdown 正文**描述具体的指令流程（触发条件、执行步骤、输出规范）。这种设计将"元数据"与"指令内容"分离，既便于系统解析，又便于人类编写和维护。本节通过示例文件完整展示 SKILL.md 的结构。

#### 2.2.2 核心字段：name 和 description

**name**：唯一标识符，仅限小写字母、数字和连字符，最大 64 字符，成为斜杠命令（如 /deploy-app）的入口。**description**：触发条件的核心，Claude 依靠此字段判断何时自动调用该 Skill，最大 1024 字符。最佳实践是使用第三人称描述能力和具体触发场景（如"当用户要求分析财报时使用"）。这两个字段决定了 Skill 的"身份"和"触发时机"。本节通过正反案例说明如何编写精准的 description。

#### 2.2.3 触发与权限控制

**disable-model-invocation**：设为 true 时禁止 Claude 自动调用，必须由用户手动输入 /name 触发，适用场景：高风险操作（如 commit, deploy）。**user-invocable**：设为 false 时不显示在 / 菜单中，适用场景：仅作为后台辅助知识库。**allowed-tools**：指定该 Skill 运行时无需用户确认即可调用的工具（如 Bash, Read, Grep 或特定的 MCP 工具）。**hooks**：定义生命周期钩子（如 PreToolUse），在特定事件触发自动化脚本，用于安全检查或日志记录。本节讲解不同触发模式和权限边界的设计原则。

#### 2.2.4 高级配置：model、context、agent

**model**：强制该 Skill 使用特定模型运行（如复杂推理任务用 claude-4.5-opus，简单格式化用 claude-4.5-haiku）。**context**：设为 fork 时在独立会话中运行，避免污染主对话历史。**agent**：配合 context: fork 使用，指定由哪个 Subagent 执行该 Skill。本节说明这些高级配置的性能优化和隔离机制。

#### 2.2.5 Markdown 正文：三个层次

SKILL.md 的 Markdown 正文包含三个层次：**触发条件**（何时使用）、**执行步骤**（如何做）、**输出规范**（结果应该长什么样）。编写时要遵循"清晰的指令、明确的边界、灵活的参数"三大原则。例如 python-naming-standard Skill 通过简洁的规则定义确保代码符合团队规范。本节通过示例说明高质量正文的编写方法。

#### 2.2.6 确定性与创造性的分离原则

对于数据清洗、格式转换等严谨任务，不要依赖 LLM 的输出，而是让 Skill 调用 Python/Bash 脚本来处理。例如：PDF 提取数据不要让 AI 逐字阅读，而是让 Skill 运行 scripts/extract_pdf.py。脚本代码本身不进入上下文，Claude 只是通过 Bash exec 运行脚本并获取输出结果，这极大节省了 Token，实现了逻辑与执行的分离。本节讲解如何根据任务特性选择合适的实现方式。

#### 2.2.7 验证闭环设计

不要只让 Skill 生成代码，要包含验证步骤。例如："生成代码后，必须运行 npm test，如果失败，读取错误日志并尝试修复，最多重试 3 次"。这种"生成-验证-修复"的闭环能显著提升 Skill 的可靠性。本节说明如何设计验证机制和错误处理策略。

### 2.3 辅助文件的组织与使用

#### 2.3.1 scripts/：脚本文件的组织与调用

当 Skill 需要执行复杂逻辑时，纯提示词可能不够用，这时就需要脚本文件。脚本代码本身不进入上下文，Claude 只是通过 Bash exec 运行脚本并获取输出结果，这极大节省了 Token，实现了逻辑与执行的分离。本节讲解如何组织和管理 scripts 目录，以及在 SKILL.md 中调用脚本的方法。

#### 2.3.2 references/：参考文档的按需加载机制

有些 Skill 需要参考大量文档，但全部加载会消耗太多 token。references 目录提供按需加载机制：只有当 Claude 在执行过程中发现需要查阅具体参数时，才会再次调用读取工具去加载 reference.md。本节说明如何设计高效的参考文档结构，避免"SKILL.md -> doc A -> doc B"的链式引用。

#### 2.3.3 扁平化引用结构最佳实践

资源文件引用最好保持在一级深度，即 SKILL.md 直接引用 reference.md。避免深层嵌套的链式引用，这会导致 AI 迷失方向。本节通过实际案例说明扁平化结构的设计方法。

	---

# 第二章 Skill 的分类与生态

## 3 官方必备 Skills

### 3.1 Skill Creator - "能生娃的 Skill"

**这是什么**：一个能自动创建其他 Skill 的 Skill，堪称"元技能"。

**能帮你做什么**：
- 不需要懂技术，说出需求自动生成完整 Skill 结构
- 自动编写 SKILL.md 的触发词和描述
- 自动生成脚本模板
- 省去手动创建的麻烦

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/skill-creator`

**如何使用**：
- 安装后，直接对 Claude 说"使用 skill-creator 帮我做一个分析 Excel 的 skill"
- Claude 会引导你回答问题：触发条件、需要哪些库、输出格式
- 自动生成完整的 Skill 文件结构
- 你只需要手动调整细节即可

**适用场景**：想创建自己的 Skill 但不知道从何下手时。

### 3.2 Document Skills - "文档处理工具集"

**这是什么**：官方提供的文档处理 Skills 集合，包含 PDF、Markdown、Word 等格式的转换、提取、分析功能。

**能帮你做什么**：
- 从 PDF 提取表格数据
- 批量转换文档格式
- 自动生成文档摘要
- 处理扫描版 PDF（OCR）

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/document-skills`

**如何使用**：
- 直接把 PDF 文件路径告诉 Claude：`帮我分析这个文件 sales_report.pdf 中的销售数据`
- Claude 会自动调用 PDF extraction Skill，提取表格并生成分析报告
- 对于批量转换：`把 docs/ 文件夹下所有 Markdown 转成 PDF`

**适用场景**：处理大量办公文档、提取报告数据、批量格式转换。

### 3.3 Image Skills - "图像处理工具集"

**这是什么**：官方提供的图像处理 Skills，支持图片编辑、格式转换、OCR 识别等功能。

**能帮你做什么**：
- 批量调整图片尺寸
- 图片格式转换（WebP、PNG、JPEG）
- OCR 文字识别
- 生成缩略图

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/image-skills`

**如何使用**：
- 批量处理：`把 images/ 文件夹下所有图片转成 WebP 格式，质量 80%`
- OCR 识别：`识别 screenshot.png 中的文字内容`
- 生成缩略图：`为所有产品图生成 200x200 的缩略图`

**适用场景**：网站图片优化、文档数字化、内容创作者处理素材。

### 3.4 Git Skills - "版本控制助手"

**这是什么**：封装了 Git 最佳实践的 Skill，自动处理版本控制操作。

**能帮你做什么**：
- 自动生成规范的 Commit Message
- 智能合并分支
- 生成 Release Notes
- 清理无用分支

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/git`

**如何使用**：
- 提交代码：直接说`提交当前修改`，Claude 会自动生成符合规范的 Commit Message
- 查看历史：`帮我看看最近 5 次提交改了什么`
- 生成日志：`为本次发布生成 Release Notes`

**适用场景**：开发者日常版本管理、团队协作规范 Git 操作。

### 3.5 PPTX Generator - "一键生成演示文稿"

从 HTML 直接生成专业 PowerPoint 演示文稿。

**能帮你做什么**：Markdown/HTML 转 PPTX；自动套用预设模板；批量生成幻灯片；支持中文字体和排版。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/pptx`

**如何使用**：把 Markdown 文件转成 PPTX：`把 report.md 转成 PowerPoint，使用蓝色主题`

**适用场景**：需要频繁制作演示文稿、报告汇报时。

### 3.6 PDF Toolkit - "PDF 处理瑞士军刀"

由 Anthropic 官方出品的 PDF 处理工具。

**能帮你做什么**：合并多个 PDF 文件；拆分 PDF 为多个文件；转换 PDF 格式；提取 PDF 中的文本和图片；压缩 PDF 文件大小。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/pdf`

**如何使用**：合并文件：`把 chapter1.pdf, chapter2.pdf, chapter3.pdf 合并成一个文件`；提取内容：`提取这个 PDF 中的所有表格数据`

**适用场景**：办公人员、文档管理者、研究人员日常处理 PDF。

### 3.7 WebApp Testing - "代码审查专家"

由 Anthropic 官方出品的代码质量检查工具。

**能帮你做什么**：自动检测安全漏洞（XSS、SQL 注入等）；性能问题分析；代码规范合规检查；最佳实践建议；自动生成测试报告。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/webapp-testing`

**如何使用**：安全检查：`检查我的代码有没有 SQL 注入漏洞`；性能分析：`分析这段代码的性能瓶颈`

**适用场景**：开发者、QA 工程师、技术负责人进行代码审查。

## 4 社区爆款 Skills

### 4.1 Codebase Visualizer - "代码库可视化"

**这是什么**：将整个代码库结构可视化，帮助快速理解项目架构。

**能帮你做什么**：
- 生成代码库依赖关系图
- 显示文件和模块的调用关系
- 识别代码热点（修改频繁的文件）
- 评估代码复杂度

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/anthropics/skills/tree/main/skills/codebase-visualizer`

**如何使用**：
- 生成全览：`帮我生成整个项目的结构图`
- 分析模块：`显示 auth 模块的依赖关系`
- 对比版本：`看看 v1.0 和 v2.0 的代码结构有什么变化`

**适用场景**：接手老项目、代码重构前分析、技术文档生成。

### 4.2 Database Query - "数据库查询助手"

**这是什么**：结合数据库 MCP（如 Postgres MCP），提供智能查询能力的 Skill。

**能帮你做什么**：
- 用自然语言查询数据库
- 自动生成优化过的 SQL
- 解释查询结果
- 生成数据可视化

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/community/database-query-skill`

**如何使用**：
- 自然语言查询：`上个月销售额超过 10 万的产品有哪些`
- 数据分析：`对比今年和去年的用户增长趋势`
- 生成报告：`生成一份本周活跃用户统计报告`

**适用场景**：数据分析、业务报表生成、非技术人员查询数据库。

### 4.3 Content Generator - "内容生成神器"

**这是什么**：帮助创作者快速生成各类内容的 Skill，支持文章、文案、脚本等。

**能帮你做什么**：
- 根据大纲生成完整文章
- 自动调整语气和风格
- SEO 优化内容
- 多语言翻译

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/community/content-generator-skill`

**如何使用**：
- 生成文章：`根据这个大纲生成一篇 2000 字的技术博客`
- 改写内容：`把这段文字改写成更轻松的语气`
- SEO 优化：`优化这篇文章的关键词，提高搜索排名`

**适用场景**：内容创作者、SEO 专员、营销人员。

### 4.4 Testing Helper - "测试用例生成器"

**这是什么**：根据代码自动生成单元测试的 Skill，内置测试框架最佳实践。

**能帮你做什么**：
- 自动生成单元测试
- 生成边界条件测试
- 生成 Mock 数据
- 验证测试覆盖率

**如何安装**：
对 Claude 说：`帮我安装 skill，地址是 https://github.com/community/testing-helper-skill`

**如何使用**：
- 生成测试：`为 utils.py 中的所有函数生成单元测试`
- 补充边界测试：`为这个函数添加异常情况测试`
- 运行验证：`生成测试后自动运行，失败则尝试修复`

**适用场景**：开发者编写测试、提高代码质量、TDD 实践。

### 4.5 Superpowers - "全栈开发工作流"

由开发者 obra 创建的完整软件开发流程 Skill。

**能帮你做什么**：自动生成需求文档（PRD）；编写代码并自动测试；代码审查和优化建议；Git 提交信息生成；完整的 CI/CD 流程。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/obra/superpowers`

**如何使用**：开始新功能：`帮我开发一个用户登录功能`，会自动生成 PRD、编写代码、测试、提交

**适合人群**：独立开发者、小型团队、创业者。

### 4.6 X Article Publisher - "推特创作者神器"

帮你快速创作和发布 X（Twitter）文章的 Skill。

**能帮你做什么**：生成推文串（thread）；自动控制字数和语气；优化标题和钩子；生成相关话题标签。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/wshuyi/x-article-publisher-skill`

**如何使用**：创作推文：`帮我写一条关于 AI 工具的推文串`，会自动生成多个关联推文

**适合人群**：内容创作者、运营人员、KOL。

### 4.7 NotebookLM Bridge - "连接 Google NotebookLM"

在 Claude Code 中直接使用 NotebookLM 的知识库功能。

**能帮你做什么**：查询你的 NotebookLM 笔记；直接上传 PDF 到 NotebookLM；基于知识库回答问题；多源知识整合。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/PleasePrompto/notebooklm-skill`

**如何使用**：查询笔记：`在我的 NotebookLM 中搜索关于 Agent Skill 的内容`

**适合人群**：研究人员、学生、知识管理爱好者。

### 4.8 Obsidian Skills - "笔记软件增强"

由 Obsidian 创始人亲自编写的官方 Skill（包含多个 Skill）。

**能帮你做什么**：生成 Obsidian 兼容的 Markdown；自动添加标签和元数据；生成 Obsidian Canvas 白板；保持原有格式不被破坏。

**如何安装**：对 Claude 说 `帮我安装 skill，地址是 https://github.com/kepano/obsidian-skills`

**如何使用**：生成笔记：`帮我把这篇文章转成 Obsidian 笔记格式，添加标签`

**适合人群**：Obsidian 用户、知识管理爱好者。

---

# 第三章 Agent Skill 的开发实战（高阶）

## 1 核心理念：将GitHub变成你的超级技能库

### 1.1 为什么是GitHub而不是重复造轮子

**重复造轮子是一件特别呆逼的事情**。互联网三十年，开源世界的大神们已经为绝大多数需求铺好了路，做出了成熟、稳定、高效的开源产品。这些项目经历了无数时间、使用者的检验，在成功率、稳定性、效率上，都远超让AI临时写的代码。Skill 的出现，让我们第一次能够便捷地封装这些开源项目，把它们变成自己的"独门绝技"。本节探讨如何站在巨人的肩膀上，快速构建高质量 Skill。

### 1.2 完整工作流：从搜索GitHub到Skill固化

**步骤 1**：用 AI 搜索 GitHub。例如对 ChatGPT 说"有没有去各种视频网站下载视频的开源项目"，AI 会推荐 yt-dlp。**步骤 2**：用 skill-creator 打包。对 Claude Code 说"帮我把 https://github.com/yt-dlp/yt-dlp 打包成 Skill"。**步骤 3**：首次运行测试。把视频链接扔给 AI，让它用新 Skill 下载。**步骤 4**：迭代优化。把首次运行遇到的问题和经验告诉 AI："把这些经验更新到 Skill 里"。至此，Skill 固化，成为你的可靠技能。本节详细演示这个完整流程。

### 1.3 实战案例：视频下载 Skill

从需求出发：经常需要下载视频但工具分散、广告多、下载慢。用 AI 搜索发现 yt-dlp（143k star，支持上千网站），通过 skill-creator 打包成 Skill。首次运行会遇到依赖安装、Cookie 配置等问题，解决后让 AI 更新到 Skill 中。下次再使用时，直接一句话搞定。这个案例展示了完整的"发现 → 打包 → 测试 → 优化"流程。



## 2 OPC 与 Agent Skills的最佳实践：一人公司的超级杠杆

### 2.1 OPC、AI 与 Skill 的三角关系

OPC (One Person Company，一人公司) 的核心挑战是：一个人要完成产品、市场、销售、运营、财务等多个角色的工作。传统方法是雇佣团队，但成本高、管理复杂。AI 的出现提供了新的可能，但单纯依赖对话式 AI 仍需反复输入指令、知识无法沉淀。

Agent Skills 是 OPC 的终极解决方案，它构建了"OPC + AI + Skill"的三角关系：**OPC 提供决策和方向**，**AI 提供执行能力**，**Skill 提供专业知识和标准流程**。每一个 Skill 相当于一个"数字员工"，PM-Skill 是产品经理，Review-Skill 是代码审查员，Marketing-Skill 是市场专员。OPC 不再需要事必躬亲，而是通过调用不同的 Skills，指挥一支"AI 团队"协同工作。这实现了从"单兵作战"到"指挥官"的质变。

### 2.2 OPC 的典型工作流

一个成熟的 OPC 工作流是这样的：

**早晨启动**：打开 Claude Code，自动加载项目的 CLAUDE.md（项目记忆），AI 知道项目背景、架构、当前进度。

**规划阶段**：调用 PM-Skill，输入一句话想法"我想加个用户推荐功能"，Skill 自动生成完整的 PRD（产品需求文档）和任务列表。

**执行阶段**：
- 开发任务：调用 Coding-Skill 编写代码，TDD-Skill 自动生成测试，Review-Skill 进行代码审查
- 内容任务：调用 Marketing-Skill 生成营销文案，X-Article-Skill 创作推文串
- 数据任务：调用 Database-Skill 查询用户数据，生成可视化报告

**审查阶段**：调用 Review-Skill（模拟合伙人角色）对成果进行找茬和优化，确保质量。

**归档阶段**：任务完成后，经验自动回写到知识库（CLAUDE.md 或 evolution.json），下次遇到类似问题直接调用经验。

通过这个工作流，OPC 实际上是在指挥一支由 Skills 定义的、不知疲倦的专家团队，而不是一个人在做所有事。

### 2.3 "游戏存档"模式：持续进化的关键

封装的 GitHub 项目会持续更新，但 OPC 使用过程中积累的优化经验会被覆盖。解决方案是"游戏存档"模式：将 SKILL.md 视为"主程序"（来自上游），将迭代经验存放在独立的 evolution.json 中（"游戏存档"）。当 GitHub 更新覆盖 SKILL.md 时，evolution.json 中的经验会自动重新注入到新版本。

这个机制对 OPC 尤其重要：你不仅是使用开源项目，而是在使用过程中不断优化、定制化。这些定制化的经验是你的核心竞争力，不应该因为上游更新而丢失。通过"游戏存档"模式，OPC 既能享受开源社区的持续更新，又能保留自己的独特优势。

### 2.4 如何构建你的 Skills 军团

**步骤 1：从痛点出发**。不要为了装 Skill 而装 Skill。列出你日常工作中重复最高、最耗时的环节，比如"每周写周报要花 2 小时""每次发推文都要想很久"。

**步骤 2：搜索现成方案**。用 AI 搜索（"GitHub 上有没有自动化生成周报的开源项目"），或浏览第二章介绍的 Skills 库。先看看有没有现成的，90% 的情况下都有。

**步骤 3：快速打包测试**。用 skill-creator 快速打包成 Skill，首次运行测试。把实际需求扔给 AI，让它用新 Skill 处理。

**步骤 4：迭代优化**。把首次运行遇到的问题和经验告诉 AI："把这些经验更新到 Skill 里"。至此，Skill 成为你的可靠"数字员工"。

**步骤 5：定期维护**。用 skill-manager 检查所有 Skills 的版本状态，几秒钟看到哪些需要更新。一条命令完成全量升级。

### 2.5 常见陷阱

**描述模糊**：避免"帮助处理文件"，改成"当用户需要将 Markdown 转换为 PDF 时使用"。**过度依赖 Prompt**：确定性的任务用脚本实现，不要让 AI 检查 1000 行数据，而是写 Python 脚本。**忽视安全**：移除 allowed-tools，强制用户确认危险操作。**上下文污染**：长流程任务设置 context: fork，避免污染主对话。

---
