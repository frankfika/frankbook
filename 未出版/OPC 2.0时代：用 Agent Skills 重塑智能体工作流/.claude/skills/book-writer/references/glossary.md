# 术语表

> 本书专用术语统一规范，确保全文用词一致性。

---

## 核心术语

| 术语 | 英文/缩写 | 首次出现章节 | 定义 |
|------|-----------|--------------|------|
| Agent Skill | Skill | 引言 | Claude 的可复用能力封装单元，由 YAML Frontmatter 和 Markdown 指令组成 |
| 渐进式披露 | Progressive Disclosure | 1.2.3 | Skill 的核心技术架构，三级按需加载机制 |
| 一人公司 | One Person Company (OPC) | 引言 | 单人运营的商业模式，一人完成产品、开发、市场等全流程 |
| 模型上下文协议 | Model Context Protocol (MCP) | 1.2.4 | 连接 AI 与外部工具的协议标准 |
| 子代理 | Subagent | 1.2.4 | 在独立会话中运行的执行实体，通过 context: fork 隔离 |
| 数字员工 | Digital Worker | 1.1.2 | 通过 Skill 固化的标准化工作流程，可重复调用 |
| 游戏存档模式 | Save Game Pattern | 第三章 2.3 | 将 Skill 经验存放在 evolution.json 中，防止上游更新覆盖 |

---

## 技术术语规范

### 必须保留英文（直接使用）
- **SKILL.md** - Skill 的核心定义文件
- **YAML Frontmatter** - 文件头部的元数据配置
- **Claude Code** - 命令行工具名称
- **Token** - 文本处理单元
- **Context Window** - 上下文窗口
- **Fork** - 进程分叉/会话隔离
- **Hook** - 生命周期钩子

### 首次出现附中文解释（后续用英文）
- Agent Skill（智能体技能）
- Progressive Disclosure（渐进式披露）
- One Person Company（一人公司，简称 OPC）
- Model Context Protocol（模型上下文协议，简称 MCP）
- Subagent（子代理）

---

## 禁用/替换词

| 禁用词 | 替换为 | 说明 |
|--------|--------|------|
| 插件 | Skill / 技能 | 避免与浏览器插件混淆 |
| 宏 | Skill / 技能 | 避免与 Office 宏混淆 |
| 脚本 | Skill / 脚本 | 视上下文区分，Skill 更强调智能 |
| 模板 | Skill / 模板 | Skill 不仅是模板，还包含逻辑 |
| 智能体 | Agent | 技术语境用英文 |
| 大模型 | LLM / 大语言模型 | 全文统一 |

---

## 大小写规范

- **Claude** - 首字母大写（产品名）
- **Anthropic** - 首字母大写（公司名）
- **GitHub** - H 大写（官方写法）
- **SKILL.md** - 全大写（文件名规范）
- **Skill** - 句中首字母大写（指代能力单元）
- **skill** - 全小写（指代具体 skill 名称，如 my-skill）

---

## 版本号写法

- Claude Code 2.1（数字间用点）
- Claude 4 Opus（版本号后空格）
- v2.1.0（带 v 前缀用于技术语境）
- 2025 年 10 月（日期写法）

---

## 易混淆词辨析

### Skill vs Command
- **Skill**：封装完整工作流，可自动触发
- **Command**：快捷指令，需用户手动输入

### MCP vs Skill
- **MCP**：提供能力（API 接口）
- **Skill**：定义如何使用能力（业务逻辑）

### Fork vs 子进程
- **Fork**：在 Claude 中指独立的 Subagent 会话
- **子进程**：操作系统概念，避免混用

---

## 索引词条（供印刷版使用）

### A
- Anthropic
- Agent Skill
- allowed-tools

### C
- Claude Code
- Command
- config.yaml
- context: fork

### D
- description
- disable-model-invocation
- Digital Worker

### H
- Hook（生命周期钩子）

### M
- MCP（Model Context Protocol）

### O
- OPC（One Person Company）

### P
- Progressive Disclosure

### R
- references/

### S
- Save Game Pattern（游戏存档模式）
- SKILL.md
- scripts/
- Subagent

### U
- user-invocable

### Y
- YAML Frontmatter
