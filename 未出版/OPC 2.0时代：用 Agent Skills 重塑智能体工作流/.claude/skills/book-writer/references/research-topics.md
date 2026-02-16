# 各节研究主题清单

> **使用说明**：本清单是研究起点，而非终点。在写作过程中，如果发现新的值得研究的方向，随时添加。研究完成后在方括号中打勾并记录关键发现。

---

## 引言
- [ ] OPC (One Person Company) 概念和趋势数据
- [ ] AI 工具在个人创业中的应用现状
- [ ] Agent Skills 的基本概念验证

---

## Phase 1: 基础铺垫

### 1.1.1 重复性工作的痛点
- [ ] Rakuten 财务自动化案例：效率提升 87.5% 的具体数据和来源
- [ ] 常见重复性工作场景的统计数据
- [ ] AI 助手在处理重复任务中的局限性

### 1.1.2 知识和经验的碎片化
- [ ] 企业知识管理的痛点数据
- [ ] 隐性知识向显性知识转化的方法论
- [ ] Agent Skill 作为"数字化 SOP"的定义来源

### 1.1.3 提示词管理的困境
- [ ] 提示词工程的发展和局限性
- [ ] Token 成本和上下文窗口限制的具体数据
- [ ] Progressive Disclosure 概念的首次引入背景

---

## Phase 2: 核心概念（需大量研究）

### 1.2.1 从 Prompt 到 Skill：范式转变
- [ ] Prompt Engineering 的发展历程
- [ ] Skill 三大核心价值（标准化、自动化、可传承）的案例支撑
- [ ] Rakuten 财务自动化完整案例细节
- [ ] 公众号数据抓取案例（30分钟→5分钟）
- [ ] Progressive Disclosure 架构的技术细节（元数据约 100 tokens）

### 1.2.2 Claude Code 与 Skill 的发展历程
- [ ] Claude Code 起源：Anthropic Labs 内部研究项目（2024年）
- [ ] Claude Code 100% 自编写的出处和报道
- [ ] 2025年2月：研究预览版发布，Claude 3.7 Sonnet
- [ ] 2025年5月：GA 全面上市，Claude 4 系列
- [ ] 2025年10月16日：Agent Skills 正式推出
- [ ] 2025年11月："Skills Explained" 深度指南发布
- [ ] 2025年12月：agentskills.io 开放标准
- [ ] 2026年1月：Claude Code 2.1 重大更新（热重载、上下文分叉、生命周期钩子）
- [ ] 每个时间点需要多源验证

### 1.2.3 Progressive Disclosure 架构原理
- [ ] 三级加载机制的技术实现细节（Level 1/2/3）
- [ ] context: fork 的工作机制
- [ ] hooks（生命周期钩子）的技术实现
- [ ] 与传统 Prompt 工程的性能对比数据
- [ ] 实际加载性能测试数据

### 1.2.4 Skill、MCP、Subagents、Command 的对比
- [ ] MCP (Model Context Protocol) 协议详情
- [ ] Subagents 架构和 context: fork 机制
- [ ] Command 快捷指令系统
- [ ] 四者协作的实际工作流示例
- [ ] 各自的最佳使用场景

---

## Phase 3: 解剖 Skill

### 2.1 核心组成架构
- [ ] 典型 Skill 目录结构的官方规范
- [ ] SKILL.md、scripts/、references/、config.yaml 的设计原则
- [ ] codebase-visualizer 的 scripts/visualize.py 示例
- [ ] pdf-processing 的 FORMS.md 示例

### 2.2.1 YAML Frontmatter + Markdown 正文
- [ ] YAML Frontmatter 的完整字段列表
- [ ] 元数据与指令内容分离的设计理由

### 2.2.2 name 和 description 字段
- [ ] name 字段的命名规范（小写、连字符、64字符限制）
- [ ] description 字段的最佳实践和反例
- [ ] 1024 字符限制的来源

### 2.2.3 触发与权限控制
- [ ] disable-model-invocation 的使用场景
- [ ] user-invocable 的使用场景
- [ ] allowed-tools 的配置方法
- [ ] hooks（PreToolUse 等）的具体用法

### 2.2.4 高级配置 model、context、agent
- [ ] 可用的模型选项（claude-4.5-opus, claude-4.5-haiku 等）
- [ ] context: fork 的隔离机制
- [ ] agent 字段与 Subagent 的关系

### 2.2.5 Markdown 正文三个层次
- [ ] 触发条件、执行步骤、输出规范的编写示例
- [ ] python-naming-standard Skill 的示例

### 2.2.6 确定性与创造性的分离
- [ ] 脚本调用 vs LLM 直接处理的决策框架
- [ ] Token 节省的具体数据

### 2.2.7 验证闭环设计
- [ ] "生成-验证-修复"闭环的实现模式
- [ ] 重试机制的最佳实践

### 2.3.1 scripts/ 目录
- [ ] 脚本组织和管理的最佳实践
- [ ] Bash exec 执行脚本的机制

### 2.3.2 references/ 按需加载
- [ ] 按需加载机制的工作原理
- [ ] 避免链式引用的设计方法

### 2.3.3 扁平化引用结构
- [ ] 一级深度引用的设计原则
- [ ] 深层嵌套导致问题的案例

---

## Phase 4: Skills 目录

### 3.1-3.7 官方 Skills
- [ ] 验证所有 GitHub 仓库地址是否真实存在
  - https://github.com/anthropics/skills/tree/main/skills/skill-creator
  - https://github.com/anthropics/skills/tree/main/skills/document-skills
  - https://github.com/anthropics/skills/tree/main/skills/image-skills
  - https://github.com/anthropics/skills/tree/main/skills/git
  - https://github.com/anthropics/skills/tree/main/skills/pptx
  - https://github.com/anthropics/skills/tree/main/skills/pdf
  - https://github.com/anthropics/skills/tree/main/skills/webapp-testing
- [ ] 每个 Skill 的实际功能描述（以 README 为准）
- [ ] 安装方式的准确描述

### 4.1-4.8 社区 Skills
- [ ] 验证所有 GitHub 仓库地址：
  - https://github.com/anthropics/skills/tree/main/skills/codebase-visualizer
  - https://github.com/community/database-query-skill（需验证）
  - https://github.com/community/content-generator-skill（需验证）
  - https://github.com/community/testing-helper-skill（需验证）
  - https://github.com/obra/superpowers
  - https://github.com/wshuyi/x-article-publisher-skill
  - https://github.com/PleasePrompto/notebooklm-skill
  - https://github.com/kepano/obsidian-skills
- [ ] 每个项目的 star 数、最近更新时间
- [ ] 实际功能验证（以 README 为准）
- [ ] 替换所有占位/无效仓库地址为真实地址

---

## Phase 5: 开发实战

### 第三章 1.1 为什么是 GitHub
- [ ] yt-dlp 项目数据（star 数：纲要说 143k，需验证当前）
- [ ] 开源项目 vs AI 临时编写代码的可靠性论据

### 第三章 1.2 完整工作流
- [ ] skill-creator 的实际使用流程
- [ ] GitHub 搜索到 Skill 固化的完整演示

### 第三章 1.3 视频下载 Skill 实战
- [ ] yt-dlp 的功能特性和支持的网站数量
- [ ] Cookie 配置等常见问题和解决方案

### 第三章 2.1-2.5 OPC 最佳实践
- [ ] OPC 工作流的实际案例
- [ ] evolution.json "游戏存档"模式的技术实现
- [ ] Skills 军团构建的实际步骤
- [ ] 常见陷阱的真实案例

---

## 研究方法论

### 信息来源优先级

1. **官方来源**（最高优先级）
   - Anthropic 官方文档和博客
   - Claude Code 官方仓库
   - Skills 官方仓库

2. **权威报道**（高优先级）
   - 知名技术媒体（TechCrunch、The Verge、Ars Technica 等）
   - 开发者社区（GitHub、Hacker News、Reddit r/ClaudeAI）

3. **社区实践**（中优先级）
   - 开源项目 README
   - 开发者博客和教程
   - 用户案例分享

4. **交叉验证**（必须步骤）
   - 关键数据和日期必须多源验证
   - 引用时标注来源

### 研究笔记格式

研究完成后，在 `assets/research/<节号>_research.md` 中记录：

```markdown
# <节号> 研究笔记

## 关键发现

### 发现1：[标题]
- **来源**：[链接]
- **内容**：[摘要]
- **可信度**：高/中/低

## 待验证信息
- [ ] [信息点1]
- [ ] [信息点2]

## 引用素材
- [链接1] - [简要说明]
- [链接2] - [简要说明]
```
