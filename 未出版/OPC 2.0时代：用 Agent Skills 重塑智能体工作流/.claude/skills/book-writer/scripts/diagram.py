#!/usr/bin/env python3
"""
图表生成工具

为书籍生成各种技术架构图、流程图、对比图。
支持 Mermaid 语法和文本描述生成。

用法：
    python diagram.py <书籍根目录> <图表类型> <输出文件名>

图表类型：
    skill-arch      - Skill 核心架构图
    progressive     - Progressive Disclosure 三级加载示意图
    skill-mcp-compare - Skill vs MCP vs Subagent 对比图
    workflow        - OPC 工作流图
    directory       - Skill 目录结构图

示例：
    python diagram.py . skill-arch 第一章/images/skill_arch
    python diagram.py . progressive 第一章/images/progressive_disclosure
"""

import sys
from pathlib import Path

# Mermaid 图表模板
DIAGRAMS = {
    "skill-arch": """
flowchart TB
    subgraph Skill[Skill 核心架构]
        direction TB
        skill_md[SKILL.md<br/>YAML Frontmatter + Markdown]
        scripts[scripts/ 目录<br/>Python/Bash 脚本]
        references[references/ 目录<br/>参考文档]
        config[config.yaml<br/>可选配置]
    end

    subgraph Execution[执行流程]
        direction TB
        trigger[语义匹配触发] --> load[按需加载内容]
        load --> execute[执行指令]
        execute --> script[调用脚本]
        script --> output[返回结果]
    end

    Skill --> Execution
""",

    "progressive": """
graph TB
    subgraph L1[Level 1: 元数据感知]
        A[读取 name + description<br/>~100 tokens]
    end

    subgraph L2[Level 2: 按需激活]
        B[匹配触发条件<br/>加载 SKILL.md 正文]
    end

    subgraph L3[Level 3: 延迟加载]
        C[需要时读取<br/>references/ 和 scripts/]
    end

    L1 -->|触发匹配| L2
    L2 -->|执行需要| L3

    style L1 fill:#e1f5fe
    style L2 fill:#fff3e0
    style L3 fill:#e8f5e9
""",

    "skill-mcp-compare": """
graph LR
    subgraph Layers[四层架构]
        direction TB
        C[Command<br/>快捷层<br/>用户触发]
        S[Skill<br/>决策层<br/>定义工作流]
        M[MCP<br/>执行层<br/>提供能力]
        SA[Subagent<br/>调度层<br/>隔离执行]
    end

    User([用户]) --> C
    C --> S
    S --> M
    S -.->|context: fork| SA
    M --> Tools[外部工具/API]
""",

    "workflow": """
flowchart LR
    subgraph Morning[早晨启动]
        A[加载 CLAUDE.md<br/>项目记忆]
    end

    subgraph Plan[规划]
        B[PM-Skill] --> PRD[生成 PRD<br/>任务列表]
    end

    subgraph Execute[执行]
        C[Coding-Skill] --> D[TDD-Skill]
        D --> E[Review-Skill]
        F[Marketing-Skill] --> G[X-Article-Skill]
    end

    subgraph Archive[归档]
        H[更新知识库<br/>CLAUDE.md]
    end

    Morning --> Plan
    Plan --> Execute
    Execute --> Archive
""",

    "directory": """
tree
    root[my-skill/]
    ├── skill_md[SKILL.md]
    ├── scripts[scripts/]
    │   ├── tool1[tool.py]
    │   └── tool2[helper.sh]
    ├── references[references/]
    │   ├── ref1[FORMAT.md]
    │   └── ref2[EXAMPLES.md]
    └── config[config.yaml]
""",
}


def generate_mermaid(diagram_type: str) -> str:
    """获取 Mermaid 图表代码。"""
    return DIAGRAMS.get(diagram_type, "")


def list_diagrams():
    """列出所有可用的图表类型。"""
    print("可用的图表类型:")
    for key, value in DIAGRAMS.items():
        title = value.strip().split('\n')[0] if value else key
        print(f"  {key:<15} - {title}")


def save_diagram(book_dir: Path, diagram_type: str, output_path: str):
    """保存图表到文件。"""
    mermaid_code = generate_mermaid(diagram_type)

    if not mermaid_code:
        print(f"❌ 未知图表类型: {diagram_type}")
        list_diagrams()
        return False

    # 处理输出路径
    if output_path.endswith('.md'):
        output_file = book_dir / output_path
    else:
        output_file = book_dir / f"{output_path}.md"

    # 确保目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 生成带说明的 Markdown
    content = f"""# {diagram_type} 图表

## Mermaid 代码

```mermaid
{mermaid_code}
```

## 说明

此图表使用 Mermaid 语法，可以在以下平台渲染：
- GitHub / GitLab
- Notion
- Typora
- VS Code + Mermaid 插件
- 在线编辑器: https://mermaid.live

## 使用建议

1. 复制上面的 Mermaid 代码
2. 粘贴到支持 Mermaid 的编辑器中
3. 或使用在线编辑器查看和修改
"""

    output_file.write_text(content, encoding="utf-8")
    print(f"✅ 图表已保存: {output_file}")
    print(f"\n使用提示:")
    print(f"  - 使用 Typora、VS Code 或在线编辑器查看")
    print(f"  - 在线编辑器: https://mermaid.live")
    print(f"  - 导出图片: 在在线编辑器中导出 PNG/SVG")

    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        list_diagrams()
        sys.exit(1)

    if sys.argv[1] in ("--list", "-l"):
        list_diagrams()
        sys.exit(0)

    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    book_dir = Path(sys.argv[1])
    diagram_type = sys.argv[2]
    output_path = sys.argv[3]

    if not book_dir.exists():
        print(f"错误: 目录不存在: {book_dir}")
        sys.exit(1)

    save_diagram(book_dir, diagram_type, output_path)


if __name__ == "__main__":
    main()
