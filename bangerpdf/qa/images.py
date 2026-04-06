"""
qa.images — broken image reference detection.

Catches Joe Fishback bid bug #5: the logo path was broken in cover_letter.html,
so WeasyPrint silently rendered the alt text "Fishback Plumbing" as plain
text where the logo should have been.

Detection strategy:
  - Walk every page's blocks via page.get_text("dict")
  - For each text block, check if its content matches a typical alt-text
    pattern (short, brand-like, near the top of a page where a logo would
    be expected)
  - Also count actual image XObjects per page; pages that semantically
    expect a logo (cover_letter, letterhead) but have zero images get
    flagged.

This is heuristic — false positives are possible. The strict source-of-truth
check happens upstream by validating that every <img src=...> in the rendered
HTML resolves to a real file. That check lives in the render pipeline (Phase 4)
and complements this PDF-level scan.
"""

from __future__ import annotations

import re

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Patterns suggesting a text block is rendered alt text from a missing image
SUSPICIOUS_ALT_PATTERNS = [
    re.compile(r"^[A-Z][a-zA-Z\s&,.'-]{2,40}$"),  # short proper-case phrase like "Fishback Plumbing"
    re.compile(r"^logo$", re.IGNORECASE),
    re.compile(r"^image$", re.IGNORECASE),
    re.compile(r"^\[image\]$", re.IGNORECASE),
]


def _count_images_on_page(page: fitz.Page) -> int:
    """Count image XObjects on a page (returns 0 if none rendered)."""
    try:
        return len(page.get_images())
    except Exception:
        return 0


def _block_font_size(block: dict) -> float:
    """Return the max font size across all spans in a text block."""
    sizes = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            sizes.append(span.get("size", 0.0))
    return max(sizes) if sizes else 0.0


def _page_median_font_size(blocks: list[dict]) -> float:
    """Return the median font size across all spans on the page."""
    sizes = []
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                sizes.append(span.get("size", 0.0))
    if not sizes:
        return 0.0
    sizes.sort()
    return sizes[len(sizes) // 2]


def check_image_refs(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Heuristic check for broken image references rendered as alt text.

    Strategy:
      1. Look only at page 1 (where logos/letterheads live).
      2. If page 1 has any image XObjects → skip (logo is fine).
      3. Walk top-of-page text blocks (top 25% of page).
      4. For each candidate: must match alt-text pattern AND be at body-font
         size or smaller (heading-sized blocks are intentional, not alt text).

    The body-font-size guard rules out headings like "Bid Proposal" or
    "Cover Letter" that match the proper-case-phrase pattern. The actual
    bug pattern (Fishback alt-text rendering) inherits body font size
    because the broken <img> falls back to its parent's font.
    """
    results: list[CheckResult] = []
    if doc.page_count == 0:
        return results

    page = doc[0]
    image_count = _count_images_on_page(page)

    # If the page already has images, no broken-ref check needed
    if image_count > 0:
        return results

    page_dict = page.get_text("dict")
    page_height = page.rect.height
    text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
    if not text_blocks:
        return results

    median_font = _page_median_font_size(text_blocks)
    if median_font <= 0:
        return results

    # Sort top-to-bottom
    text_blocks.sort(key=lambda b: b["bbox"][1])

    for block in text_blocks[:5]:  # only check the top 5 blocks
        # Must be in the top 25% of the page (where logos live)
        if block["bbox"][1] > page_height * 0.25:
            break

        text = ""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text += span.get("text", "")
            text += " "
        text = text.strip()

        if not text or len(text) > 60:
            continue

        # KEY GUARD: skip heading-sized blocks (intentional content, not alt text)
        block_size = _block_font_size(block)
        if block_size > median_font * 1.2:
            continue

        for pattern in SUSPICIOUS_ALT_PATTERNS:
            if pattern.match(text):
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="POSSIBLE_BROKEN_IMAGE",
                    message=(
                        f"Body-text '{text}' near top of page 1 may be alt text from a "
                        f"missing image — page has 0 image references"
                    ),
                    pdf_path=pdf_path,
                    check="images",
                    page=1,
                    bbox=tuple(block["bbox"]),
                ))
                return results  # one warning per file is enough

    return results
