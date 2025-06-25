---
title: 记一次MCP辅助开发经历
date: '2025-04-06T13:48:30+08:00'
tags:
- 编程
- Python
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---

# 记一次MCP使用经历

>本次开发的结果和完整对话记录都将整理并备份在[Github](https://github.com/Jinvic/minesweeper)上。

最开始只是玩扫雷时，感觉鼠标声音有点响，想改成键盘。另外有时扫雷会出现纯看运气的情况，希望加个直接显示雷的作弊功能。就这两个需求，简单让AI写了下，过程略。

因为感觉一个庞大的单文件不够美观，就想试着拆分成多文件系统。正好最近经常被MCP刷屏，想试试能不能接入一个MCP让cursor自己完成文件的创建之类步骤，实现完全的自动化。找了下选择了这个[Filesystem MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)。

## MCP接入和验证

cursor接入MCP也有两种方式，分别时全局和当前目录。前者在`C:/Users/用户名/.cursor/mcp.json`下，后者在当前目录创建`./.cursor/mcp.json`。我使用的后者，写入如下内容：

```json
{
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-filesystem",
          "./"
        ]
      }
    }
  }
```

由于使用的npx命令，所以需要nodejs环境。之后再cursor的设置的MCP页面能看到该MCP且带绿点就行了。要验证该mcp能否正常操作文件系统，可以使用如下提示词验证：

```txt
请在当前工作目录下创建一个名为 'test.txt' 的新文件，并向其中写入以下内容：'这是一个测试文件。'
```

## 拆分多文件

最开始我让AI拆分多文件时它虽然拆了但没有创建对应文件，似乎是我表述不清晰。之后明确说明让它创建对应文件就会去使用MCP创建了。

```markdown

_**User**_

请阅读main.py的代码，并将其拆分为更工程化的多文件结构。

---

_**Assistant**_



---

我将把这个扫雷游戏拆分为更工程化的多文件结构。下面是建议的文件结构和代码：

## 文件结构


minesweeper/
│
├── game/
│   ├── __init__.py
│   ├── core.py          # 游戏核心逻辑
│   └── ui.py            # 用户界面组件
│
├── handlers/
│   ├── __init__.py
│   └── events.py        # 事件处理器
│
└── main.py              # 入口点文件


## 代码实现

(略)

```

```markdown


_**User**_

请你按照如上内容完成项目文件的创建和编辑。

---

_**Assistant**_



---

<details>
            <summary>Listed current directory • **4** results</summary>
        
| Name |
|-------|
| 📄 `main.py` |
| 📄 `main.py.backup` |
| 📁 `__pycache__` |
| 📁 `.cursor` |

</details>

---

现在我将创建项目目录结构。首先创建主要目录：

---

我需要在当前工作目录中创建项目目录：

---

让我们使用终端命令创建目录：

---

mkdir -p minesweeper/game minesweeper/handlers

PS D:\Workspace\Python\Arbiter> mkdir -p minesweeper/game minesweeper/handlers

mkdir: A positional parameter cannot be found that accepts argument 'minesweeper
/handlers'.

---

让我尝试使用PowerShell语法：

---

mkdir minesweeper/game, minesweeper/handlers -Force

    Directory: D:\Workspace\Python\Arbiter\minesweeper

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----            2025/4/5    16:30                game
d----            2025/4/5    16:30                handlers
PS D:\Workspace\Python\Arbiter>

---

现在让我们创建所需的所有文件：

---

(略)

```

可以看到，现在它会去获取当前文件目录结构并使用命令创建目录。再Linux命令出错时也会主动更换目录。

## 添加日志功能

之后添加readme，功能修改和测试等都正常。直到我尝试添加日志功能后，发现它会自动查询生成的日志去DEBUG。

最开始它只是通过 `-Tail` 选项查询最新的日志：

```markdown


游戏现在没有显示错误，这是个好迹象。让我们检查一下日志文件，看看窗口大小调整功能是否正常工作：

---

Get-Content -Path "./logs/minesweeper_2025-04-05.log" -Tail 30

```

在发现信息不足时马上更该更准确的筛选和查询方式：

```txt
让我们看更多的日志记录：

---

Get-Content -Path "./logs/minesweeper_2025-04-05.log" | Select-String -Pattern "游戏板|窗口|设置"

```

## 自动化测试流程

在学会查询日志后，后续的开发和测试它甚至会在功能完成后自己创建测试脚本并运行：

```markdown

让我们测试日志级别的变更是否真正影响了日志输出。首先，我们创建一个临时的测试脚本：

---

（内容略）

---

现在运行测试脚本：

---

python test_log_settings.py

（日志略）

---

我们可以看到，日志级别设置已经修改，但有两个问题需要解决：

1. 控制台只显示了警告和错误级别的日志，这是因为控制台处理器的级别被硬编码为WARNING
2. 日志保留天数意外地显示为3天而不是7天，这可能是之前的测试修改了配置

让我们修复第一个问题，并再次运行测试：

---

（过程略）

现在我们可以看到，DEBUG 和 INFO 级别的消息也显示出来了，说明日志级别设置已经正确应用。

```

如上内容都是在一次对话中完成的。很明显，AI主动建立了一个创建测试脚本->运行->查看日志输出->修改测试脚本->运行...的工作流，反复测试并修改直到问题解决，大大提升了效率和自动化程度。

## 总结

本来只是一次简单的开发，但加入MCP后的成果令我十分惊讶，尤其是AI借助MCP在没有任何指示的情况主动建立起了一套可行的测试流程。这还只是导入了一个最基础的文件系统操作的MCP。难以想象在更专业的领域，加入MCP后的AI辅助开发会对开发流程带来何种颠覆性的改变。
