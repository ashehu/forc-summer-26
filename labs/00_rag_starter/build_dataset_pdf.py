#!/usr/bin/env python3
"""Generate the polished 20-page PDF supplied with the starter corpus."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

LAB_DIR = Path(__file__).resolve().parent
SOURCE_DIR = LAB_DIR / "data" / "source_txt"
OUTPUT_PATH = LAB_DIR / "data" / "rag_starter_corpus.pdf"
PAGE_MARKER = re.compile(r"^=== PAGE (\d+) ===$", re.MULTILINE)

INK = colors.HexColor("#102A33")
CORAL = colors.HexColor("#E76F51")
TEAL = colors.HexColor("#55B9AE")
PAPER = colors.HexColor("#F5F0E5")


def parse(path: Path) -> tuple[dict[str, str], list[tuple[int, str]]]:
    raw = path.read_text(encoding="utf-8")
    first = PAGE_MARKER.search(raw)
    if not first:
        raise ValueError(path)
    metadata = {}
    for line in raw[: first.start()].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
    matches = list(PAGE_MARKER.finditer(raw))
    pages = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        pages.append((int(match.group(1)), raw[match.end() : end].strip()))
    return metadata, pages


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    canvas.setStrokeColor(CORAL)
    canvas.setLineWidth(2)
    canvas.line(0.7 * inch, 0.65 * inch, 7.8 * inch, 0.65 * inch)
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(0.7 * inch, 0.42 * inch, "RAG STARTER · FICTIONAL TEACHING CORPUS")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(7.8 * inch, 0.42 * inch, f"{doc.page} / 20")
    canvas.restoreState()


def main() -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "DocTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24,
        leading=28, textColor=INK, alignment=TA_LEFT, spaceAfter=8,
    )
    meta = ParagraphStyle(
        "Meta", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8,
        leading=11, textColor=CORAL, uppercase=True, spaceAfter=18,
    )
    body = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=11,
        leading=16, textColor=INK, spaceAfter=13,
    )
    page_label = ParagraphStyle(
        "PageLabel", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9,
        leading=12, textColor=TEAL, spaceAfter=8,
    )
    story = []
    total = 0
    for path in sorted(SOURCE_DIR.glob("*.txt")):
        metadata, pages = parse(path)
        for source_page, page_text in pages:
            total += 1
            story.append(Paragraph(metadata["title"], title))
            story.append(Paragraph(
                f"{metadata['document_id']} &nbsp;&nbsp;|&nbsp;&nbsp; {metadata['document_type'].upper()}", meta
            ))
            story.append(Paragraph(f"SOURCE PAGE {source_page}", page_label))
            story.append(Spacer(1, 0.05 * inch))
            for paragraph in page_text.split("\n\n"):
                story.append(Paragraph(paragraph.replace("&", "&amp;"), body))
            if total < 20:
                story.append(PageBreak())
    if total != 20:
        raise SystemExit(f"Expected 20 source pages, found {total}")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH), pagesize=letter, rightMargin=0.7 * inch, leftMargin=0.7 * inch,
        topMargin=0.72 * inch, bottomMargin=0.85 * inch,
        title="Riverton Graduate Research Studio - RAG Starter Corpus",
        author="FORC '26 teaching materials",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
