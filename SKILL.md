---
name: chatpaper-library
description: Analyze one academic paper PDF or a folder of papers, generate structured Chinese reading notes and local SVG mind maps, and create or incrementally update a searchable HTML paper library. Use when the user asks to add papers to a 精读库、论文库、文献库, batch-process a paper folder, or invokes $chatpaper-library. Do not use for non-academic document collections.
---

# ChatPaper Library

Turn one paper or a folder of papers into a durable local reading library. Preserve analytical depth while making deterministic artifact generation fast and offline.

## Inputs and output location

- Accept a PDF, multiple paper files, or a folder. For a folder, discover supported academic documents recursively and ignore previously generated library folders.
- If the user points to an existing `library.json`, update that library in place.
- Otherwise create `chatpaper-library/` in the current writable workspace. Do not write beside a read-only source PDF unless the user asks.
- Use a stable paper slug. Match an existing entry by DOI first, then normalized title, so reruns update rather than duplicate.

## Analyze each paper

Extract full-text, equations, figures, tables, appendices, or page verification directly using Antigravity's native document and PDF viewing tools (`view_file`), or combine with `nature-reader`. Read the complete paper, not only its abstract.

Before drafting, read [references/analysis-format.md](references/analysis-format.md). Follow its eight-section structure unless the user explicitly requests another structure. Clearly distinguish author claims, reported evidence, and your own evaluation. Never invent metadata, datasets, code links, numerical results, page citations, or limitations.

Create these files for every paper:

```text
papers/<slug>/analysis.md
papers/<slug>/mindmap.md
papers/<slug>/mindmap.svg
```

The analysis Markdown is the source of truth for the HTML detail page. Keep headings, lists, block quotes, and comparison tables valid Markdown.

## Generate the mind map locally

Write `mindmap.md` as a clean heading-and-list hierarchy: one `#` root, `##` main branches, `###` sub-branches, then concise bullets. Do not put a Mermaid code block in this file.

Run the bundled renderer (locate within the skill's `scripts/` directory):

```powershell
python "<skill-directory>/scripts/render_mindmap.py" <mindmap.md> <mindmap.svg>
```

Use the environment's Python executable. This renderer is dependency-free, deterministic, and keeps paper content local. Do not upload files to third-party services unless the user explicitly requests web export.

## Update the library

Read [references/library-schema.md](references/library-schema.md) before creating or changing `library.json`. Preserve existing papers, notes-compatible slugs, manual tags, statuses, and unrelated metadata.

**论文标题展示与双语规范**：
- 在 `library.json` 中，`title` 必须保留论文标题原名（英文论文存英文原名，中文论文存中文原名），并新增 `title_zh` 字段存储精准的中文翻译名称；
- 在精读库目录页（卡片视图与表格视图），必须保留论文标题原名（如果是英文论文，主标题显示英文原题），并在其下方用一行小字给出标题中文翻译名称；
- 点击进入论文详情页后，顶部大标题同样采用原名展示，大标题下方紧随一行小字呈现中文翻译名称。

After updating the manifest, build a self-contained HTML page:

```powershell
python "<skill-directory>/scripts/build_library.py" <library.json> <paper-library.html>
```

The HTML must retain:

- searchable card and table views (with bilingual title display: original title on top, Chinese translation below);
- rose, green, and blue themes;
- a three-column paper detail layout with sticky table of contents and bilingual title header;
- the full Markdown analysis rendered in the center column;
- per-paper notes saved in browser `localStorage`;
- a mind-map action on every paper card and detail page;
- an in-page SVG viewer with zoom, scroll, and a direct-open link;
- relative artifact links so the library folder remains portable.

## Verify and report

- Confirm that every manifest paper has readable analysis and mind-map files.
- Open the generated page through a temporary localhost server and verify the dashboard, one detail page, one table, and every mind-map path. Check browser console errors. Stop the server afterward.
- For a batch, report totals for discovered, added, updated, skipped, and failed papers. Never silently omit a failed paper.
- Return clickable links to `paper-library.html`, `library.json`, and the newly generated artifacts.

If a paper cannot be parsed reliably, keep any existing library entry unchanged and report the specific failure.
