#!/usr/bin/env python3
"""Build a portable single-file HTML paper library from library.json."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def inline(text: str) -> str:
    value = html.escape(text.strip())
    code: list[str] = []
    def keep_code(match: re.Match[str]) -> str:
        code.append(f"<code>{match.group(1)}</code>")
        return f"@@CODE{len(code)-1}@@"
    value = re.sub(r"`([^`]+)`", keep_code, value)
    value = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    for i, snippet in enumerate(code):
        value = value.replace(f"@@CODE{i}@@", snippet)
    return value


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_rule(line: str) -> bool:
    cells = split_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def render_list(block: list[tuple[int, bool, str]]) -> str:
    def level(index: int, indent: int) -> tuple[str, int]:
        ordered = block[index][1]
        tag = "ol" if ordered else "ul"
        out = [f"<{tag}>"]
        while index < len(block):
            current_indent, current_ordered, text = block[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                nested, index = level(index, current_indent)
                out[-1] += nested
                continue
            if current_ordered != ordered:
                break
            out.append(f"<li>{inline(text)}")
            index += 1
            if index < len(block) and block[index][0] > indent:
                nested, index = level(index, block[index][0])
                out[-1] += nested
            out[-1] += "</li>"
        out.append(f"</{tag}>")
        return "".join(out), index
    chunks: list[str] = []
    i = 0
    while i < len(block):
        rendered, i = level(i, block[i][0])
        chunks.append(rendered)
    return "".join(chunks)


def markdown_to_html(markdown: str) -> tuple[str, list[dict[str, str]]]:
    lines = markdown.replace("\r\n", "\n").splitlines()
    output: list[str] = []
    toc: list[dict[str, str]] = []
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    heading_index = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1; continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1)); title = heading.group(2).strip()
            if level == 1:
                i += 1; continue
            if level == 2:
                heading_index += 1
                anchor = f"sec-{heading_index}"
                toc.append({"id": anchor, "title": re.sub(r"^\d+(?:\.\d+)*[.、]?\s*", "", title)})
                output.append(f'<section id="{anchor}"><span class="section-num">{heading_index:02d}</span><h2>{inline(title)}</h2>')
                if heading_index > 1:
                    output.insert(-1, "</section>")
            else:
                output.append(f"<h{level}>{inline(title)}</h{level}>")
            i += 1; continue
        if line.lstrip().startswith(">"):
            block: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                block.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            output.append(f'<blockquote>{inline(" ".join(block))}</blockquote>')
            continue
        if "|" in line and i + 1 < len(lines) and is_table_rule(lines[i + 1]):
            headers = split_cells(line); i += 2; rows: list[list[str]] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_cells(lines[i])); i += 1
            table = ['<div class="table-wrap"><table class="analysis-table"><thead><tr>']
            table += [f"<th>{inline(cell)}</th>" for cell in headers]
            table.append("</tr></thead><tbody>")
            for row in rows:
                table.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
            table.append("</tbody></table></div>")
            output.append("".join(table)); continue
        list_match = re.match(r"^(\s*)([-+*]|\d+[.)])\s+(.+)$", line)
        if list_match:
            block: list[tuple[int, bool, str]] = []
            while i < len(lines):
                match = re.match(r"^(\s*)([-+*]|\d+[.)])\s+(.+)$", lines[i])
                if not match: break
                block.append((len(match.group(1).expandtabs(2)), bool(re.match(r"\d", match.group(2))), match.group(3)))
                i += 1
            output.append(render_list(block)); continue
        para = [line.strip()]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6})\s+|^\s*(?:[-+*]|\d+[.)])\s+|^\s*>", lines[i]):
            if "|" in lines[i] and i + 1 < len(lines) and is_table_rule(lines[i + 1]): break
            para.append(lines[i].strip()); i += 1
        output.append(f"<p>{inline(' '.join(para))}</p>")
    if heading_index:
        output.append("</section>")
    return "\n".join(output), toc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--template", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    root = manifest_path.parent
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    papers = data.get("papers")
    if not isinstance(papers, list):
        raise SystemExit("library.json must contain a papers array")
    problems: list[str] = []
    enriched: list[dict] = []
    for paper in papers:
        item = dict(paper)
        missing = [key for key in ("slug", "title", "authors", "year", "status", "tags", "analysis_md", "mindmap_svg") if key not in item]
        if missing:
            problems.append(f"{item.get('title','<untitled>')}: missing {', '.join(missing)}"); continue
        analysis_path = root / Path(item["analysis_md"])
        map_path = root / Path(item["mindmap_svg"])
        if not analysis_path.is_file():
            problems.append(f"{item['title']}: analysis missing: {analysis_path}"); continue
        if not map_path.is_file():
            problems.append(f"{item['title']}: mind map missing: {map_path}"); continue
        item["analysis_html"], item["toc"] = markdown_to_html(analysis_path.read_text(encoding="utf-8-sig"))
        item["authors_text"] = "、".join(item["authors"]) if isinstance(item["authors"], list) else str(item["authors"])
        enriched.append(item)
    if problems:
        raise SystemExit("\n".join(problems))
    data["papers"] = enriched
    template_path = args.template or Path(__file__).resolve().parent.parent / "assets" / "library-template.html"
    template = template_path.read_text(encoding="utf-8")
    template = template.replace("border:1px solid var(--rule71);", "")
    template = template.replace("导 wrap SVG9050</a${''}</a>", "导图 SVG →</a>")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    if "__LIBRARY_JSON__" not in template:
        raise SystemExit("template is missing __LIBRARY_JSON__")
    result = template.replace("__LIBRARY_JSON__", payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"built {len(enriched)} papers -> {args.output}")


if __name__ == "__main__":
    main()
