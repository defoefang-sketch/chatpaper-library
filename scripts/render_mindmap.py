#!/usr/bin/env python3
"""Render heading/list Markdown into a portable SVG mind map."""

from __future__ import annotations

import argparse
import html
import math
import re
from dataclasses import dataclass, field
from pathlib import Path


COLORS = ["#ED7E7D", "#6BA6D4", "#6FBF92", "#D99A4E", "#9B7BC5", "#4FA9A6", "#C66B91", "#7D9C45"]


@dataclass
class Node:
    label: str
    children: list["Node"] = field(default_factory=list)
    x: float = 0
    y: float = 0
    side: int = 1
    color: str = COLORS[0]


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_~=`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_markdown(path: Path) -> Node:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    root: Node | None = None
    heading_stack: list[tuple[int, Node]] = []
    bullet_stack: list[tuple[int, Node]] = []
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    for index, raw in enumerate(lines):
        line = raw.rstrip()
        if in_frontmatter:
            if index and line.strip() == "---":
                in_frontmatter = False
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            node = Node(clean(heading.group(2)))
            if not node.label:
                continue
            if root is None:
                root = node
                heading_stack = [(level, node)]
            else:
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                parent = heading_stack[-1][1] if heading_stack else root
                parent.children.append(node)
                heading_stack.append((level, node))
            bullet_stack.clear()
            continue
        bullet = re.match(r"^(\s*)(?:[-+*]|\d+[.)])\s+(.+?)\s*$", line)
        if bullet and root is not None:
            indent = len(bullet.group(1).expandtabs(2))
            node = Node(clean(bullet.group(2)))
            if not node.label:
                continue
            while bullet_stack and bullet_stack[-1][0] >= indent:
                bullet_stack.pop()
            parent = bullet_stack[-1][1] if bullet_stack else heading_stack[-1][1]
            parent.children.append(node)
            bullet_stack.append((indent, node))
    if root is None:
        root = Node(path.stem)
    return root


def leaf_weight(node: Node) -> int:
    return max(1, sum(leaf_weight(child) for child in node.children))


def max_depth(node: Node, depth: int = 0) -> int:
    return max([depth] + [max_depth(child, depth + 1) for child in node.children])


def wrap_label(label: str, limit: int = 18) -> list[str]:
    words = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_.+/%—–-]+|[^\s]", label)
    rows: list[str] = []
    row = ""
    width = 0.0
    for token in words:
        token_width = sum(1.0 if "\u4e00" <= c <= "\u9fff" else 0.55 for c in token)
        gap = "" if not row or len(token) == 1 and "\u4e00" <= token <= "\u9fff" else " "
        if row and width + token_width > limit:
            rows.append(row)
            row, width = token, token_width
        else:
            row += gap + token
            width += token_width
    if row:
        rows.append(row)
    return rows or [""]


def node_size(node: Node) -> tuple[float, float, list[str]]:
    rows = wrap_label(node.label)
    max_units = max(sum(1.0 if "\u4e00" <= c <= "\u9fff" else 0.58 for c in row) for row in rows)
    width = min(250, max(92, 28 + max_units * 13))
    height = 24 + len(rows) * 17
    return width, height, rows


def assign_branch_colors(root: Node) -> None:
    def paint(node: Node, color: str) -> None:
        node.color = color
        for child in node.children:
            paint(child, color)
    for i, child in enumerate(root.children):
        paint(child, COLORS[i % len(COLORS)])


def layout(root: Node) -> tuple[float, float]:
    assign_branch_colors(root)
    left: list[Node] = []
    right: list[Node] = []
    left_weight = right_weight = 0
    for child in sorted(root.children, key=leaf_weight, reverse=True):
        weight = leaf_weight(child)
        if right_weight <= left_weight:
            right.append(child); right_weight += weight; child.side = 1
        else:
            left.append(child); left_weight += weight; child.side = -1

    depth = max_depth(root)
    h_step = 300
    margin = 170
    width = max(1200, 2 * (depth * h_step + margin))
    root.x = width / 2
    gap = 62

    def place_side(nodes: list[Node], side: int) -> tuple[float, list[Node]]:
        cursor = 80.0
        ordered: list[Node] = []
        def place(node: Node, d: int) -> None:
            nonlocal cursor
            node.side = side
            node.x = root.x + side * d * h_step
            if node.children:
                child_ys = []
                for child in node.children:
                    child.side = side
                    place(child, d + 1)
                    child_ys.append(child.y)
                node.y = (child_ys[0] + child_ys[-1]) / 2
            else:
                node.y = cursor
                cursor += gap
            ordered.append(node)
        for item in nodes:
            place(item, 1)
            cursor += gap * 0.45
        return max(160.0, cursor), ordered

    left_h, left_nodes = place_side(left, -1)
    right_h, right_nodes = place_side(right, 1)
    height = max(720.0, left_h, right_h) + 80
    root.y = height / 2
    for nodes, side_h in ((left_nodes, left_h), (right_nodes, right_h)):
        offset = (height - side_h) / 2
        for node in nodes:
            node.y += offset
    return width, height


def flatten(root: Node) -> list[tuple[Node | None, Node]]:
    result: list[tuple[Node | None, Node]] = []
    def walk(parent: Node | None, node: Node) -> None:
        result.append((parent, node))
        for child in node.children:
            walk(node, child)
    walk(None, root)
    return result


def render(root: Node, output: Path) -> None:
    width, height = layout(root)
    pairs = flatten(root)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{math.ceil(width)}" height="{math.ceil(height)}" viewBox="0 0 {math.ceil(width)} {math.ceil(height)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<g fill="none" stroke-linecap="round">'
    ]
    for parent, node in pairs:
        if parent is None:
            continue
        pw, _, _ = node_size(parent); nw, _, _ = node_size(node)
        sx = parent.x + node.side * pw / 2
        ex = node.x - node.side * nw / 2
        bend = (sx + ex) / 2
        parts.append(f'<path d="M {sx:.1f} {parent.y:.1f} C {bend:.1f} {parent.y:.1f}, {bend:.1f} {node.y:.1f}, {ex:.1f} {node.y:.1f}" stroke="{node.color}" stroke-width="2.2" opacity=".72"/>')
    parts.append('</g><g font-family="Segoe UI, PingFang SC, Microsoft YaHei, sans-serif">')
    for parent, node in pairs:
        nw, nh, rows = node_size(node)
        x = node.x - nw / 2; y = node.y - nh / 2
        is_root = parent is None
        fill = "#423F3D" if is_root else "#FFFFFF"
        stroke = "#423F3D" if is_root else node.color
        text_fill = "#FFFFFF" if is_root else "#423F3D"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{nw:.1f}" height="{nh:.1f}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{2.4 if is_root else 1.6}"/>')
        start_y = node.y - (len(rows) - 1) * 8.5 + 5
        parts.append(f'<text x="{node.x:.1f}" y="{start_y:.1f}" text-anchor="middle" fill="{text_fill}" font-size="{16 if is_root else 14}" font-weight="{700 if is_root or node.children else 500}">')
        for i, row in enumerate(rows):
            dy = 0 if i == 0 else 17
            parts.append(f'<tspan x="{node.x:.1f}" dy="{dy}">{html.escape(row)}</tspan>')
        parts.append('</text>')
    parts.append('</g></svg>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Heading/list Markdown file")
    parser.add_argument("output", type=Path, help="Output SVG file")
    args = parser.parse_args()
    root = parse_markdown(args.input)
    render(root, args.output)
    print(f"rendered {len(flatten(root))} nodes -> {args.output}")


if __name__ == "__main__":
    main()
