# Preferred analysis format

Use this structure for every paper unless the user asks for another. Adapt method and experiment subsections to the paper type; do not force experimental fields onto a review paper.

> **标题规范（Bilingual Title Requirement）**：
> - 针对英文论文：正文一级标题 `#` 必须保留**英文原名**，并在其下方紧随一行小字或引用块给出**中文翻译名称**（例如：`> **中文译名**：高比例可再生能源电力系统频率安全域：理论、评估与应用`）。
> - 针对中文论文：正文一级标题采用中文原名。

Start with one scope sentence, for example: “以下分析基于论文全文 N 页，包括正文、主要公式、图表、结论和附录。” State any unreadable or missing portions.

## 1. 基本信息

- 论文原名（英文论文保留英文原题，中文论文保留中文原名）与 中文翻译名称（英文论文必填精准中文译名）
- Authors and affiliations
- Venue, publication status/date, DOI
- Funding when present
- Code and data availability; write “未找到” when unavailable
- Keywords

## 2. 一句话总结

Give one compact synthesis. For a review or systems paper, show the central technical chain as a bold arrow sequence when that aids understanding. Follow it with the authors’ central judgment.

## 3. 核心概念

Define the concepts needed to read the paper. Use a comparison table when several concepts are easy to confuse. Preserve equations only when they materially clarify the method and identify their source section or page.

## 4. 论文梳理的方法体系

Break the paper into numbered method subsections. For each approach, explain its basic idea, strengths, limitations, assumptions, and role in the larger workflow. Use four-column comparison tables where appropriate.

For an empirical paper, include tasks, datasets, baselines, metrics, and key numerical results here or in a clearly labeled experiments subsection. Do not invent missing values.

## 5. 作者提出的关键难题

Summarize the open problems or bottlenecks explicitly identified by the authors. Keep this separate from your own criticism.

## 6. 作者建议的未来方向

Use a numbered list. Preserve the authors’ scope and avoid presenting your own proposals as theirs.

## 7. 我的评价

Use `### 优点` and `### 局限`. This is analyst judgment, not an author claim. Evaluate evidence quality, methodological coverage, assumptions, reproducibility, generalization, and practical applicability.

## 8. 阅读建议

Say whether the paper deserves close reading, who benefits most, and what sections to prioritize. End with one promising research direction in a block quote when justified.

## Style requirements

- Write in clear Chinese while retaining useful English abbreviations.
- Prefer paragraphs, lists, and real Markdown tables over compressed prose.
- Avoid generic praise. Tie every judgment to paper content.
- Cite sections, pages, figures, tables, or appendices when extraction supports them.
- Keep the analysis Markdown complete; the HTML builder renders this file without restructuring it.
