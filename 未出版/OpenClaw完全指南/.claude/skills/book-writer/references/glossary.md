# 术语表

> 本书专用术语统一规范，确保全文用词一致性。

---

## 核心术语

| 术语 | 英文/缩写 | 首次出现章节 | 定义 |
|------|-----------|--------------|------|
| 自进化智能体 | Self-Evolving Agent | 第1章 | 通过执行-评估-反思-进化循环，越用越强的AI系统 |
| GEPA框架 | Generation-Evaluation-Planning-Advancement | 第1章 | 自进化的四大支柱框架 |
| OpenClaw | - | 序章 | 开源的自进化AI助手平台 |
| Gateway | - | 第3章 | OpenClaw的控制平面，消息路由中心 |
| Agent | - | 第3章 | OpenClaw的AI推理层，执行具体任务 |
| Lobster引擎 | Lobster Engine | 第3章 | OpenClaw的确定性工作流引擎 |
| ClawdHub | - | 第6章 | OpenClaw的技能市场 |
| Moltbook | - | 第9章 | AI-only的社交网络 |
| OPC | One-Person Company | 第11章 | 一人公司，一人+AI团队=一家公司 |
| Agent OS | Agent Operating System | 第12章 | AI的个人操作系统 |

---

## 技术术语规范

### 必须保留英文（直接使用）
- **OpenClaw** - 项目名称
- **Gateway** - 系统控制平面
- **Agent** - AI推理实体
- **Lobster Engine** - 工作流引擎
- **ClawdHub** - 技能市场
- **Moltbook** - AI社交网络
- **Skill** - 技能
- **MCP** - Model Context Protocol
- **Cron** - 定时任务
- **WebSocket** - 通信协议
- **Docker** - 容器技术
- **YAML/JSON** - 数据格式

### 首次出现附中文解释（后续用英文）
- Self-Evolving Agent（自进化智能体）
- GEPA Framework（自进化四大支柱框架）
- Gateway-Centric（以网关为中心的架构）
- One-Person Company（一人公司，简称OPC）
- Agent OS（智能体操作系统）

---

## 禁用/替换词

| 禁用词 | 替换为 | 说明 |
|--------|--------|------|
| 插件 | Skill/技能 | 避免与浏览器插件混淆 |
| 机器人 | Agent/智能体 | 更专业的术语 |
| 脚本 | Skill/脚本 | 视上下文区分 |
| 智能助手 | AI助手/智能体 | 统一用词 |
| 大模型 | LLM/大语言模型 | 全文统一 |
| 聊天机器人 | 对话AI/AI助手 | 更准确的描述 |

---

## 大小写规范

- **OpenClaw** - 首字母大写（产品名）
- **Gateway** - 首字母大写（核心组件）
- **Agent** - 首字母大写（核心组件）
- **ClawdHub** - C和H大写（产品名）
- **Moltbook** - M大写（产品名）
- **Claude** - 首字母大写（AI模型）
- **Anthropic** - 首字母大写（公司名）
- **GitHub** - H大写（官方写法）
- **Skill** - 句中首字母大写（指代技能单元）
- **OPC** - 全大写（缩写）
- **MCP** - 全大写（缩写）

---

## 版本号写法

- OpenClaw v1.0（数字间用点）
- Claude 3.5 Sonnet（版本号后空格）
- Node.js ≥ 22（版本要求）
- 2025年11月（日期写法）

---

## 易混淆词辨析

### Gateway vs Agent
- **Gateway**：控制平面，负责消息路由和连接管理
- **Agent**：执行平面，负责AI推理和任务执行

### Skill vs 工作流
- **Skill**：可复用的能力单元
- **工作流**：特定任务的执行流程

### OpenClaw vs ClawdHub
- **OpenClaw**：AI助手平台本身
- **ClawdHub**：技能市场/应用商店

### Moltbook vs OpenClaw
- **Moltbook**：AI社交网络（AI-only）
- **OpenClaw**：个人AI助手平台

---

## 索引词条（供印刷版使用）

### A
- Agent
- Agent OS
- Anthropic

### C
- ClawdHub
- Claude
- Cron

### D
- Docker
- DM Pairing

### G
- Gateway
- GEPA框架
- Generation
- Evaluation
- Planning
- Advancement

### L
- Lobster Engine
- Loopback-First

### M
- MCP（Model Context Protocol）
- Moltbook

### O
- One-Person Company（OPC）
- OpenClaw

### S
- Self-Evolving Agent
- Skill

### W
- WebSocket
