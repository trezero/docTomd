#!/usr/bin/env python3
"""Convert exported .doc files containing HTML into Markdown."""
from __future__ import annotations

import argparse
import dataclasses
import email
from email import policy
from email.message import Message
import html
from html.parser import HTMLParser
import pathlib
import re
from typing import Iterable, List, Optional, Union


class Node:
    """Simple representation of an HTML element."""

    __slots__ = ("name", "attrs", "children")

    def __init__(self, name: str, attrs: Optional[dict[str, str]] = None) -> None:
        self.name = name
        self.attrs = attrs or {}
        self.children: List[Union["Node", str]] = []

    def append(self, child: Union["Node", str]) -> None:
        self.children.append(child)


class HTMLTreeBuilder(HTMLParser):
    """Parse HTML into a simple Node tree."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = Node("document")
        self.stack: List[Node] = [self.root]

    # type: ignore[override]
    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() in self.VOID_TAGS:
            self.handle_startendtag(tag, attrs)
            return
        attr_dict = {name: value or "" for name, value in attrs}
        node = Node(tag, attr_dict)
        self.stack[-1].append(node)
        self.stack.append(node)

    # type: ignore[override]
    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attr_dict = {name: value or "" for name, value in attrs}
        node = Node(tag, attr_dict)
        self.stack[-1].append(node)

    # type: ignore[override]
    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].name == tag:
                del self.stack[index:]
                break

    # type: ignore[override]
    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].append(data)

    # type: ignore[override]
    def handle_comment(self, data: str) -> None:  # noqa: D401 - intentionally no-op
        """Ignore HTML comments."""
        # Intentionally ignored


@dataclasses.dataclass
class RenderContext:
    list_stack: List[dict[str, Union[str, int]]]
    pre: bool = False

    def child(self, **updates: Union[bool, list]) -> "RenderContext":
        data = dataclasses.replace(self)
        for key, value in updates.items():
            setattr(data, key, value)
        return data


class MarkdownRenderer:
    def __init__(self) -> None:
        self.block_tags = {
            "address",
            "article",
            "aside",
            "blockquote",
            "div",
            "dl",
            "fieldset",
            "figcaption",
            "figure",
            "footer",
            "form",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "header",
            "hr",
            "li",
            "main",
            "nav",
            "ol",
            "p",
            "pre",
            "section",
            "table",
            "ul",
        }

    def render(self, node: Node) -> str:
        ctx = RenderContext(list_stack=[])
        text = self._render_children(node, ctx)
        text = "\n".join(line.rstrip() for line in text.splitlines())
        text = re.sub(r"\n{3,}", "\n\n", text)
        clean = text.strip()
        if not clean:
            return ""
        return clean + "\n"

    def _render_children(self, node: Node, ctx: RenderContext) -> str:
        parts = []
        for child in node.children:
            parts.append(self._render(child, ctx))
        return "".join(parts)

    def _render(self, node: Union[Node, str], ctx: RenderContext) -> str:
        if isinstance(node, str):
            return self._render_text(node, ctx)

        name = node.name.lower()
        if name in {"html", "body"}:
            return self._render_children(node, ctx)

        if name in {"head", "style", "script"}:
            return ""

        if name.startswith("h") and len(name) == 2 and name[1].isdigit():
            level = int(name[1])
            content = self._render_children(node, ctx).strip()
            if not content:
                return ""
            return f"\n\n{'#' * level} {content}\n\n"

        if name == "p":
            content = self._render_children(node, ctx).strip()
            if not content:
                return ""
            return f"\n\n{content}\n\n"

        if name in {"strong", "b"}:
            content = self._render_children(node, ctx).strip()
            if not content:
                return ""
            return f"**{content}**"

        if name in {"em", "i"}:
            content = self._render_children(node, ctx).strip()
            if not content:
                return ""
            return f"*{content}*"

        if name == "br":
            return "\n"

        if name == "hr":
            return "\n\n---\n\n"

        if name == "a":
            href = node.attrs.get("href", "").strip()
            content = self._render_children(node, ctx).strip()
            if not content:
                content = href
            if not content:
                return ""
            if href:
                return f"[{content}]({href})"
            return content

        if name == "code":
            content = self._render_children(node, ctx.child(pre=True))
            return f"`{content}`"

        if name == "pre":
            content = self._render_children(node, ctx.child(pre=True))
            content = content.strip("\n")
            return f"\n\n```\n{content}\n```\n\n"

        if name == "ul":
            ctx.list_stack.append({"type": "ul"})
            items = [self._render(child, ctx) for child in node.children]
            ctx.list_stack.pop()
            content = "".join(item for item in items if item.strip())
            if not content:
                return ""
            return f"\n{content}\n"

        if name == "ol":
            ctx.list_stack.append({"type": "ol", "index": 0})
            items = [self._render(child, ctx) for child in node.children]
            ctx.list_stack.pop()
            content = "".join(item for item in items if item.strip())
            if not content:
                return ""
            return f"\n{content}\n"

        if name == "li":
            if not ctx.list_stack:
                bullet = "- "
            else:
                current = ctx.list_stack[-1]
                if current["type"] == "ol":
                    current["index"] = int(current.get("index", 0)) + 1
                    bullet = f"{current['index']}. "
                else:
                    bullet = "- "
            indent = "  " * (len(ctx.list_stack) - 1)
            content = self._render_children(node, ctx).strip()
            if not content:
                content = ""
            lines = content.splitlines()
            if not lines:
                return f"{indent}{bullet}\n"
            first = lines[0]
            rest = lines[1:]
            rendered = f"{indent}{bullet}{first}"
            for line in rest:
                rendered += f"\n{indent}  {line}"
            return rendered + "\n"

        if name == "img":
            alt = node.attrs.get("alt", "").strip()
            src = node.attrs.get("src", "").strip()
            if not src:
                return ""
            title = node.attrs.get("title", "").strip()
            title_part = f' "{title}"' if title else ""
            return f"![{alt}]({src}{title_part})"

        if name == "table":
            rows = self._extract_table_rows(node, ctx)
            if not rows:
                return ""
            header = rows[0]
            body = rows[1:] if len(rows) > 1 else []
            column_count = max(len(row) for row in rows)
            widths = [0] * column_count
            for row in rows:
                for index, cell in enumerate(row):
                    widths[index] = max(widths[index], len(cell))
            lines = []
            if header:
                padded_header = [header[i] if i < len(header) else "" for i in range(column_count)]
                header_line = " | ".join(padded_header[i].ljust(widths[i]) for i in range(column_count))
                separator = " | ".join("-" * max(3, widths[i]) for i in range(column_count))
                lines.append(header_line)
                lines.append(separator)
            for row in body:
                padded_row = [row[i] if i < len(row) else "" for i in range(column_count)]
                line = " | ".join(padded_row[i].ljust(widths[i]) for i in range(column_count))
                lines.append(line)
            table_text = "\n".join(lines)
            return f"\n\n{table_text}\n\n"

        if name in {"span", "font", "div", "section", "article", "body"}:
            return self._render_children(node, ctx)

        return self._render_children(node, ctx)

    def _render_text(self, text: str, ctx: RenderContext) -> str:
        if ctx.pre:
            return text
        if not text:
            return ""
        original = text
        text = html.unescape(text)
        text = text.replace("\xa0", " ")
        stripped = text.strip()
        if not stripped:
            return " "
        collapsed = re.sub(r"\s+", " ", stripped)
        if original and original[0].isspace():
            collapsed = " " + collapsed
        if original and original[-1].isspace():
            collapsed = collapsed + " "
        return collapsed

    def _extract_table_rows(self, node: Node, ctx: RenderContext) -> List[List[str]]:
        rows: List[List[str]] = []
        for child in node.children:
            if isinstance(child, Node) and child.name.lower() in {"thead", "tbody", "tfoot"}:
                rows.extend(self._extract_table_rows(child, ctx))
            elif isinstance(child, Node) and child.name.lower() == "tr":
                row = []
                for cell in child.children:
                    if isinstance(cell, Node) and cell.name.lower() in {"td", "th"}:
                        content = self._render_children(cell, ctx).strip()
                        row.append(content)
                if row:
                    rows.append(row)
        return rows


def extract_html(message: Message) -> Optional[str]:
    if message.get_content_type() == "text/html":
        payload = message.get_payload(decode=True)
        if payload is None:
            return None
        charset = message.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, errors="replace")
        except LookupError:
            return payload.decode("utf-8", errors="replace")

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="replace")
                except LookupError:
                    return payload.decode("utf-8", errors="replace")
    return None


def convert_html_to_markdown(html_text: str) -> str:
    parser = HTMLTreeBuilder()
    parser.feed(html_text)
    renderer = MarkdownRenderer()
    return renderer.render(parser.root)


def convert_file(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    data = input_path.read_bytes()
    message = email.message_from_bytes(data, policy=policy.default)
    html_text = extract_html(message)
    if html_text is None:
        try:
            html_text = data.decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - extremely unlikely
            html_text = ""
    markdown = convert_html_to_markdown(html_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def iter_doc_files(path: pathlib.Path) -> Iterable[pathlib.Path]:
    if path.is_file() and path.suffix.lower() == ".doc":
        yield path
    elif path.is_dir():
        for child in sorted(path.iterdir()):
            if child.is_file() and child.suffix.lower() == ".doc":
                yield child


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert .doc files containing HTML to Markdown")
    parser.add_argument("input", nargs="?", default="docIn", help="Path to a .doc file or directory (default: docIn)")
    parser.add_argument("--output", "-o", default="docOut", help="Directory to store Markdown files (default: docOut)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = pathlib.Path(args.input)
    output_dir = pathlib.Path(args.output)
    if not input_path.exists():
        raise SystemExit(f"Input path '{input_path}' does not exist")

    files = list(iter_doc_files(input_path))
    if not files:
        raise SystemExit("No .doc files found to convert")

    for file_path in files:
        relative = file_path.stem + ".md"
        output_path = output_dir / relative
        convert_file(file_path, output_path)
        print(f"Converted {file_path} -> {output_path}")


if __name__ == "__main__":
    main()
