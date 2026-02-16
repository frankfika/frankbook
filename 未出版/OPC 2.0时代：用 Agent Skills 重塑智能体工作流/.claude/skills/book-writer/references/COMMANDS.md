# 命令详解

本文档包含 book-writer skill 所有命令的详细说明。

---

## 1. `/book-writer research <节号>`

针对某节做网络研究，产出研究笔记。

**执行步骤：**

1. 读取 `references/research-topics.md` 获取该节的研究主题清单
2. 读取 `references/outline.md` 获取该节的纲要描述
3. 使用 WebSearch 搜索关键事实（时间线、数据、案例）
4. 将研究结果写入 `assets/research/<节号>_research.md`
5. 更新该节文件的 frontmatter status 为 `researched`

**研究策略（按内容类型）：**

| 内容类型 | 方法 |
|----------|------|
| Claude Code 发展时间线、版本号 | WebSearch 多源验证 |
| GitHub 仓库信息（star、功能） | WebSearch + WebFetch GitHub |
| 技术概念、架构原理 | WebSearch 官方文档 |
| 案例数据 | WebSearch 多源交叉验证 |

---

## 2. `/book-writer write <节号>`

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
- **全自动模式**：引言、1.1.x 系列、第二章各 Skill 介绍节 → 直接完成写作
- **分步确认模式**：1.2.x 核心技术概念节 → 写完后请用户审阅确认

---

## 3. `/book-writer review <节号>`

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

---

## 4. `/book-writer progress`

显示全书进度表。

```bash
python .claude/skills/book-writer/scripts/progress.py .
```

---

## 5. `/book-writer assemble <章号>`

将各小节合并为完整章节。

```bash
python .claude/skills/book-writer/scripts/assemble.py . <章号>
```

章号对应：0=引言, 1=第一章, 2=第二章, 3=第三章

组装后通读检查：小节间过渡是否自然，术语是否统一。

---

## 6. `/book-writer export`

将完整章节导出为 PDF。

```bash
# 先组装所有章节
python .claude/skills/book-writer/scripts/assemble.py . 0
python .claude/skills/book-writer/scripts/assemble.py . 1
python .claude/skills/book-writer/scripts/assemble.py . 2
python .claude/skills/book-writer/scripts/assemble.py . 3

# 然后使用 md2pdf skill 导出
```

---

## 7. `/book-writer init <节号> <标题>`

初始化新的小节文件（当需要新增章节时使用）。

**执行步骤：**

1. 根据节号确定章节目录
2. 创建新的 markdown 文件，包含标准 frontmatter
3. 更新 `references/section-map.md` 添加新节信息

---

## 8. `/book-writer restructure`

重组书籍目录结构（当大纲调整时使用）。

**使用场景：**
- 新增章节
- 调整章节顺序
- 合并或拆分小节

**执行步骤：**

1. 读取当前 `references/outline.md` 和 `references/section-map.md`
2. 分析用户的新需求
3. 提出重组方案
4. 执行文件重命名/移动
5. 更新 section-map

**可用命令：**

```bash
# 列出所有小节
python .claude/skills/book-writer/scripts/restructure.py . list

# 移动/重命名小节
python .claude/skills/book-writer/scripts/restructure.py . move 1.2.5 1.3.1

# 交换两个小节
python .claude/skills/book-writer/scripts/restructure.py . swap 2.1 2.2

# 删除小节（会确认）
python .claude/skills/book-writer/scripts/restructure.py . delete 1.1.4
```

---

## 9. `/book-writer diagram <图表类型> <输出路径>`

生成技术架构图、流程图（使用 Mermaid 语法）。

**支持的图表类型：**

| 类型 | 说明 |
|------|------|
| `skill-arch` | Skill 核心架构图 |
| `progressive` | Progressive Disclosure 三级加载示意图 |
| `skill-mcp-compare` | Skill vs MCP vs Subagent 对比图 |
| `workflow` | OPC 工作流图 |
| `directory` | Skill 目录结构图 |

**示例：**

```bash
# 生成 Skill 架构图
python .claude/skills/book-writer/scripts/diagram.py . skill-arch 第一章/images/skill_arch

# 生成 Progressive Disclosure 示意图
python .claude/skills/book-writer/scripts/diagram.py . progressive 第一章/images/progressive

# 列出所有可用图表
python .claude/skills/book-writer/scripts/diagram.py --list
```

**使用方法：**

1. 生成的图表保存为 Markdown 文件（包含 Mermaid 代码）
2. 使用以下方式查看/导出：
   - **在线编辑器**: https://mermaid.live（推荐，可导出 PNG/SVG/PDF）
   - **Typora**: 直接渲染
   - **VS Code**: 安装 Mermaid 插件
   - **GitHub/GitLab**: 自动渲染

---

## 10. `/book-writer proofread <节号>`

责任编辑校对检查（三审三校流程）。

**检查内容：**
- 术语一致性（Skill、Claude、GitHub 等大小写）
- 禁用词（"本节将介绍""综上所述"等学术腔）
- 格式规范（代码块语言标记、段落长度）
- 内容质量（字数、代码示例、图表）

**示例：**

```bash
# 校对指定小节
python .claude/skills/book-writer/scripts/editor.py . proofread 1.2.1

# 查看术语表
python .claude/skills/book-writer/scripts/editor.py . terminology

# 查看出版检查清单
python .claude/skills/book-writer/scripts/editor.py . checklist
```
