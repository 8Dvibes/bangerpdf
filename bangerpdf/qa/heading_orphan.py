"""
qa.heading_orphan — heading in bottom 15% of page with no body text following.

Catches the anti-pattern where a section heading lands at the very bottom
of a page, creating an awkward break with no content below it to anchor the
reader's eye. Different from orphans.check_orphan_section_header which uses
a 20% threshold — this is a stricter, v2 check using 15%.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Bottom 15% of the page
BOTTOM_ZONE_FRACTION = 0.85

# Heading must be at least this factor larger than the page's median body font
HEADING_SIZE_FACTOR = 1.3

# Headings are short — skip long blocks
MAX_HEADING_CHARS = 100


def _block_text(block: dict) -> str:
    """Concatenate all spans in a text block."""
    parts = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            parts.append(span.get("text", ""))
        parts.append(" ")
    return "".join(parts).strip()


def _block_max_font_size(block: dict) -> float:
    """Return the max font size across all spans."""
    sizes = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            sizes.append(span.get("size", 0.0))
    return max(sizes) if sizes else 0.0


def _median_body_size(blocks: list[dict]) -> float:
    """Median font size across all text spans on a page."""
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


def check_heading_orphan(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect headings in the bottom 15% of a page with no body text following."""
    results: list[CheckResult] = []
    total_pages = doc.page_count

    for i, page in enumerate(doc):
        page_num = i + 1
        if page_num == total_pages:
            continue  # last page can't orphan forward

        page_dict = page.get_text("dict")
        text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
        meaningful = [b for b in text_blocks if _block_text(b)]

        if not meaningful:
            continue

        median_body = _median_body_size(text_blocks)
        if median_body <= 0:
            continue

        page_height = page.rect.height
        bottom_threshold = page_height * BOTTOM_ZONE_FRACTION

        # Sort blocks top-to-bottom by their top edge
        meaningful.sort(key=lambda b: b["bbox"][1])

        # Find blocks in the bottom zone
        bottom_blocks = [b for b in meaningful if b["bbox"][1] >= bottom_threshold]
        if not bottom_blocks:
            continue

        for block in bottom_blocks:
            font_size = _block_max_font_size(block)
            text = _block_text(block)

            # Is it heading-sized?
            if font_size < median_body * HEADING_SIZE_FACTOR:
                continue

            # Is it short enough to be a heading?
            if len(text) > MAX_HEADING_CHARS:
                continue

            # Is there any body text below it on this page?
            block_bottom = block["bbox"][3]
            has_body_below = False
            for other in meaningful:
                if other["bbox"][1] > block_bottom:
                    other_size = _block_max_font_size(other)
                    if other_size < font_size:
                        has_body_below = True
                        break

            if not has_body_below:
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="HEADING_ORPHAN",
                    message=(
                        f"Heading '{text[:50]}' in bottom 15% of page "
                        f"with no body text following"
                    ),
                    pdf_path=pdf_path,
                    check="heading_orphan",
                    page=page_num,
                ))

    return results
