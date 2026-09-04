# Library manifest schema

`library.json` is UTF-8 JSON. Paths are relative to the manifest directory and use forward slashes.

```json
{
  "title": "论文精读库",
  "generated_at": "2026-09-04",
  "papers": [
    {
      "slug": "stable-kebab-case-id",
      "title": "论文原名（若是英文论文则填英文原名，中文论文填中文原名）",
      "title_zh": "中文翻译名称（针对英文论文，用于目录页与详情页以小字展示译名）",
      "title_en": "English title (英文原题，保持字段兼容)",
      "authors": ["作者一", "作者二"],
      "affiliations": ["单位一"],
      "venue": "期刊或会议",
      "year": "2025",
      "date": "2025-08-14",
      "doi": "10.xxxx/xxxxx",
      "status": "done",
      "tags": ["关键词一", "关键词二"],
      "references_count": 0,
      "source_path": "D:/papers/example.pdf",
      "analysis_md": "papers/stable-id/analysis.md",
      "mindmap_md": "papers/stable-id/mindmap.md",
      "mindmap_svg": "papers/stable-id/mindmap.svg"
    }
  ]
}
```

Required paper fields: `slug`, `title`, `authors`, `year`, `status`, `tags`, `analysis_md`, and `mindmap_svg`.
Recommended bilingual fields: `title_zh` (英文论文必填中文翻译，供目录及详情页小字显示), `title_en` (保留英文原名).

Allowed status values: `reading`, `done`, `archived`. Default a completed new analysis to `done`.

## 标题展示与双语规范

1. **目录页（卡片视图与表格视图）**：
   - 保留论文标题原名（如果是英文论文，主标题采用英文原名）；
   - 在主标题下方，用一行小字给出标题中文翻译名称（`title_zh`）；
   - 若本身为中文论文，则直接展示中文原名，不重复展示小字。
2. **论文详情页（Detail Page）**：
   - 顶部大标题（`h1.paper-title`）同样保留论文标题原名（英文论文采用英文原名）；
   - 在大标题下方紧随一行小字（或副标题样式）给出中文翻译名称（`title_zh`）。

## Update rules

1. Match by normalized DOI when both sides have one.
2. Otherwise match by a case-folded title with whitespace and punctuation removed.
3. Preserve an existing `slug`, `status`, and user-added tags unless the user requests changes.
4. Update bibliographic facts only when verified from the paper.
5. Set `generated_at` to the build date.
6. Never store the full PDF or analysis body inside the manifest.

## Batch accounting

Track and report discovered source files, new entries, updated entries, skipped files, and failures with source path and reason.
