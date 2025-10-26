#!/usr/bin/env python3
"""
build_book.py
Compile Markdown manuscript into:
  - EPUB  (ebooklib)
  - PDF   (WeasyPrint if available; fallback to ReportLab)
Also copies in cover + images where relevant.

Usage:
  python scripts/build_book.py \
      --input book/manuscript.md \
      --epub book/book.epub \
      --pdf  book/book.pdf \
      --cover book/kindle/cover/cover.jpg \
      --images-dir book/images
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Optional deps handled by uv --with
try:
    import markdown as md
except Exception:
    print("ERROR: Python package 'markdown' is required.", file=sys.stderr)
    raise

# EPUB deps
try:
    from ebooklib import epub
except Exception:
    epub = None  # handled later

# Optional PDF deps
try:
    from weasyprint import HTML, CSS  # type: ignore
except Exception:
    HTML = CSS = None  # handled at runtime

# Fallback PDF
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
except Exception:
    LETTER = None
    canvas = None


CSS_DEFAULT = """
/* Minimal eBook styles */
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; line-height: 1.45; }
h1, h2, h3, h4 { line-height: 1.25; margin: 1.2em 0 .4em; }
code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }
pre { background: #f6f8fa; padding: .8em; border-radius: .35em; overflow-x: auto; }
img { max-width: 100%; height: auto; }
"""


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def md_to_html(markdown_text: str) -> str:
    return md.markdown(
        markdown_text,
        extensions=["extra", "toc", "codehilite", "tables", "fenced_code"],
    )


def guess_title(markdown_text: str) -> str:
    # first ATX H1 line (# Title)
    for line in markdown_text.splitlines():
        m = re.match(r"^\s*#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return "MCP Gateway Masterclass"


def build_epub(
    html: str, out_path: Path, title: str, image_dir: Path | None, cover_img: Path | None
):
    if epub is None:
        raise RuntimeError("ebooklib not available. Run with uv --with ebooklib.")

    book = epub.EpubBook()
    book.set_identifier("mcp-gateway-masterclass")
    book.set_title(title)
    book.set_language("en")
    book.add_author("Ruslan Magaña")

    if cover_img and cover_img.exists():
        with cover_img.open("rb") as f:
            book.set_cover("cover.jpg", f.read())

    # Stylesheet
    style = epub.EpubItem(
        uid="style_css",
        file_name="style/style.css",
        media_type="text/css",
        content=CSS_DEFAULT.encode("utf-8"),
    )
    book.add_item(style)

    # Chapter from entire manuscript (simple, reliable)
    chap = epub.EpubHtml(title=title, file_name="chapter.xhtml", lang="en")
    chap.content = f"<html><head><meta charset='utf-8'/><link rel='stylesheet' href='style/style.css'/></head><body>{html}</body></html>"
    book.add_item(chap)

    # Add images, if any (so they’re available inside the EPUB)
    if image_dir and image_dir.exists():
        for p in sorted(image_dir.rglob("*")):
            if not p.is_file():
                continue
            mt = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
                ".webp": "image/webp",
            }.get(p.suffix.lower())
            if not mt:
                continue
            rel_name = f"images/{p.name}"
            img_item = epub.EpubItem(
                uid=rel_name, file_name=rel_name, media_type=mt, content=p.read_bytes()
            )
            book.add_item(img_item)

    # TOC & Spine
    book.toc = (epub.Link("chapter.xhtml", title, "chap1"),)
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    book.spine = ["nav", chap]

    epub.write_epub(str(out_path), book)


def build_pdf_weasy(html: str, out_path: Path, base_dir: Path):
    if HTML is None or CSS is None:
        raise RuntimeError("WeasyPrint not available.")
    HTML(string=html, base_url=str(base_dir)).write_pdf(
        str(out_path), stylesheets=[CSS(string=CSS_DEFAULT)]
    )


def build_pdf_reportlab(markdown_text: str, out_path: Path, title: str):
    """Plain fallback PDF—preserves text (no full HTML layout)."""
    if canvas is None or LETTER is None:
        raise RuntimeError("ReportLab not available.")
    c = canvas.Canvas(str(out_path), pagesize=LETTER)
    width, height = LETTER
    x_margin, y_margin = 1.0 * inch, 1.0 * inch
    y = height - y_margin
    c.setTitle(title)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, title)
    y -= 0.5 * inch
    c.setFont("Helvetica", 10)
    for line in markdown_text.splitlines():
        line = line.replace("\t", "    ")
        if y < y_margin:
            c.showPage()
            y = height - y_margin
            c.setFont("Helvetica", 10)
        c.drawString(x_margin, y, line[:110])
        y -= 12
    c.showPage()
    c.save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to book/manuscript.md")
    ap.add_argument("--epub", help="Output EPUB path")
    ap.add_argument("--pdf", help="Output PDF path")
    ap.add_argument("--cover", help="Cover image (jpg preferred)")
    ap.add_argument("--images-dir", help="Images directory to include in EPUB")
    args = ap.parse_args()

    in_md = Path(args.input).resolve()
    if not in_md.exists():
        print(f"ERROR: manuscript not found: {in_md}", file=sys.stderr)
        sys.exit(1)

    cover = Path(args.cover).resolve() if args.cover else None
    images_dir = Path(args.images_dir).resolve() if args.images_dir else None
    base_dir = in_md.parent

    md_text = read_text(in_md)
    title = guess_title(md_text)
    html = md_to_html(md_text)
    html_full = f"<article>{html}</article>"

    if args.epub:
        out_epub = Path(args.epub).resolve()
        out_epub.parent.mkdir(parents=True, exist_ok=True)
        build_epub(html_full, out_epub, title, images_dir, cover)

    if args.pdf:
        out_pdf = Path(args.pdf).resolve()
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        # Prefer WeasyPrint, fallback to ReportLab
        try:
            build_pdf_weasy(html_full, out_pdf, base_dir)
        except Exception:
            # Fallback is plain text layout but reliable for CI
            build_pdf_reportlab(md_text, out_pdf, title)

    print("OK")


if __name__ == "__main__":
    main()