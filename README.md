# ChatPaper Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)

> **将学术论文（单篇或整个文件夹）转化为可持久化、可搜索、多主题的本地 HTML 论文精读库，并自动生成高质量离线矢量思维导图。**

`chatpaper-library` 是一个为 AI 智能体（如 Google Antigravity、Claude Desktop、Cursor、ChatGPT 等）量身打造的开源 Skill。它拒绝走马观花式的浅层摘要，通过严格的 8 节学术分析框架、中英双语规范、本地确定性渲染与增量维护机制，帮科研工作者轻松构建个人学术文献知识库。

---

## 🌟 核心特性

- 📖 **结构化深度精读（非简单摘要）**：
  - 严格遵循八大模块分析：基本信息（双语题目/作者/DOI等）、一句话总结、核心概念对比表、方法体系深度梳理、作者提出的关键难题、未来方向、分析师客观评价（优点与局限）、针对性阅读建议。
  - 自动保留作者声明、实证数据、图表公式引用，严禁凭空捏造。
- 🌐 **双语规范（Bilingual Title Support）**：
  - 针对英文论文，全流程严格保留英文原题，并自动翻译提炼精准中文译名；
  - 精读库目录（卡片/表格）与论文详情页顶部均采用“原文主标题 + 中文副标题”双语对照排版。
- 🧠 **本地离线零依赖思维导图生成**：
  - 自带轻量级纯 Python 矢量渲染器（`scripts/render_mindmap.py`），无需连接任何第三方云服务；
  - 将分层 Markdown 大纲一键转为现代化高对比度、双向平衡分支的 SVG 矢量图。
- 💻 **现代化自包含 HTML 知识库**：
  - 生成单文件便携式 `paper-library.html`，无需搭建后台服务器，双击即开即用；
  - 支持 **卡片（Card）** 与 **表格（Table）** 两种视图，内置实时模糊搜索与标签过滤；
  - 提供 **玫瑰（Rose）**、**森林（Green）**、**海洋（Blue）** 3 种现代主题自由切换；
  - 经典三栏式论文详情布局：左侧交互式目录导航（Sticky ToC）、中间全文精读内容、右侧元数据与本地笔记（支持 `localStorage` 离线保存）；
  - 内置 SVG 导图查看器，支持平移、滚轮缩放与独立打开。
- 🔄 **增量更新与智能去重**：
  - 维护集中式 `library.json` 索引库，优先通过 DOI 匹配，其次通过标题匹配，重复处理自动更新而非产生冗余条目。

---

## 📂 项目结构

```text
chatpaper-library/
├── SKILL.md                  # Skill 核心定义与工作流程规范
├── README.md                 # 项目介绍与使用指南
├── LICENSE                   # MIT 开源协议
├── .gitignore                # Git 忽略配置
├── agents/
│   └── openai.yaml           # Agent 元数据与调用策略配置
├── assets/
│   └── library-template.html # 现代化单文件 HTML 论文库模板
├── references/
│   ├── analysis-format.md    # 论文精读 8 节标准结构规范
│   └── library-schema.md     # library.json 元数据模式规范
└── scripts/
    ├── build_library.py      # 构建单文件 HTML 知识库脚本（纯 Python 标准库）
    └── render_mindmap.py     # 离线渲染 SVG 思维导图脚本（纯 Python 标准库）
```

---

## 🚀 安装与配置

### 方式一：在 Google Antigravity 中使用
将本项目放置到全局或项目 Skills 目录下：
- 全局路径：`~/.gemini/config/skills/chatpaper-library`
- 项目路径：`<your-workspace>/.agent/skills/chatpaper-library`

在对话中直接输入：
```text
请帮我把这个文件夹里的论文添加到精读库中：D:/MyPapers/
# 或
Use $chatpaper-library to analyze paper.pdf
```

### 方式二：在 Claude Desktop / Cursor / 其他 Agent 中使用
作为自定义 Skill 或 Prompt 注入到您的 Agent 工作流中，并允许 Agent 调用 `scripts/` 中的 Python 脚本。

---

## 🛠️ 独立脚本使用指南

本项目脚本全部使用 **Python 3.8+ 标准库** 编写，**无需 `pip install` 任何三方包**！

### 1. 生成思维导图 SVG
编写一个层级清晰的 `mindmap.md`（一级 `#` 为核心，二级 `##` 为主分支，三级 `###` 为子分支，下接列表），运行：
```bash
python scripts/render_mindmap.py input_mindmap.md output_mindmap.svg
```

### 2. 编译生成 HTML 论文库
根据 `references/library-schema.md` 准备好 `library.json` 后，运行：
```bash
python scripts/build_library.py library.json paper-library.html
```

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。欢迎 Star、Fork 与 PR！
