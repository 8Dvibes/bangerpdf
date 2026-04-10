"""
qa.single_element — page with only one content block (excluding page numbers/footers).

Catches pages that contain a single lonely element — typically a sign of
content that should have been merged with the previous or next page. Page
numbers and footer text are excluded since they're structural, not content.
"""

from __future__ import annotations

import re

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Footer zone: bottom 10% of the page
FOOTER_ZONE_FRACTION = 0.90

# Minimum density for the single block to be considered intentional
# (e.g., a full-page image is fine)
MIN_SINGLE_BLOCK_DENSITY = 0.40

# Page number patterns
_PAGE_NUMBER_RE = re.compile(
    r"^\s*(?:page\s+)?\d{1,4}\s*$|"
    r"^\s*-\s*\d{1,4}\s*-\s*$|"
    r"^\s*\d{1,4}\s*/\s*\d{1,4}\s*$",
    re.IGNORECASE,
)

# Footer-like patterns
_FOOTER_PATTERNS = [
    re.compile(r"confidential", re.IGNORECASE),
    re.compile(r"proprietary", re.IGNORECASE),
    re.compile(r"\u00a9|\bcopyright\b", re.IGNORECASE),  # copyright
    re.compile(r"all\s+rights\s+reserved", re.IGNORECASE),
    re.compile(r"^\s*www\.", re.IGNORECASE),
]


def _block_text(block: dict) -> str:
    """Concatenate all spans in a text block."""
    parts = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            parts.append(span.get("text", ""))
        parts.append(" ")
    return "".join(parts).strip()


def _is_footer_or_page_number(block: dict, page_height: float) -> bool:
    """Check if a block is a page number or footer text."""
    bbox = block.get("bbox", (0, 0, 0, 0))
    text = _block_text(block)

    if not text:
        return True  # empty blocks don't count as content

    # In the footer zone?
    if bbox[1] >= page_height * FOOTER_ZONE_FRACTION:
        # Page number?
        if _PAGE_NUMBER_RE.match(text):
            return True
        # Footer text?
        for pat in _FOOTER_PATTERNS:
            if pat.search(text):
                return True

    # Also check for page numbers at the top (header area, top 8%)
    if bbox[3] <= page_height * 0.08:
        if _PAGE_NUMBER_RE.match(text):
            return True

    return False


def _block_area(block: dict) -> float:
    """Bounding box area of a block."""
    bbox = block.get("bbox", (0, 0, 0, 0))
    w = max(0.0, bbox[2] - bbox[0])
    h = max(0.0, bbox[3] - bbox[1])
    return w * h


def check_single_element(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect pages with only one content block (excluding footers/page numbers)."""
    results: list[CheckResult] = []
    total_pages = doc.page_count

    for i, page in enumerate(doc):
        page_num = i + 1
        page_height = page.rect.height
        page_area = page.rect.width * page.rect.height

        # Skip first page (covers are often single-element by design)
        if page_num == 1:
            continue
        # Skip last page (often sparse by design)
        if page_num == total_pages:
            continue

        page_dict = page.get_text("dict")
        all_blocks = page_dict.get("blocks", [])

        # Separate content blocks from footer/page-number blocks
        content_blocks = []
        for block in all_blocks:
            text = _block_text(block) if block.get("type") == 0 else ""
            is_image = block.get("type") == 1

            if is_image:
                content_blocks.append(block)
            elif text and not _is_footer_or_page_number(block, page_height):
                content_blocks.append(block)

        if len(content_blocks) != 1:
            continue

        # If the single element is large enough, it's probably intentional
        # (e.g., a full-page chart or image)
        single = content_blocks[0]
        block_density = _block_area(single) / page_area if page_area > 0 else 0

        if block_density >= MIN_SINGLE_BLOCK_DENSITY:
            continue  # large enough to be intentional

        text = _block_text(single) if single.get("type") == 0 else "[image]"
        results.append(CheckResult(
            severity=Severity.WARNING,
            code="SINGLE_ELEMENT_PAGE",
            message=(
                f"Page contains only one content block: "
                f"'{text[:60]}' ({block_density:.0%} of page)"
            ),
            pdf_path=pdf_path,
            check="single_element",
            page=page_num,
        ))

    return results
