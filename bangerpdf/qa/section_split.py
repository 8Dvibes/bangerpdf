"""
qa.section_split — heading on one page, most of its body content on the next.

Detects the case where a section heading is at the bottom of page N and
the majority of its body content lands on page N+1. This creates a poor
reading experience — the heading should move to page N+1 with its content.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# A heading in the bottom 30% of the page is a candidate for splitting
BOTTOM_CANDIDATE_FRACTION = 0.70

# Heading must be at least this factor larger than median body font
HEADING_SIZE_FACTOR = 1.3

# If >60% of the next-page body text belongs to this section, it's a split
SPLIT_THRESHOLD = 0.60


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
    """Median font size across text spans on a page."""
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


def _text_block_area(block: dict) -> float:
    """Compute the bounding box area of a text block."""
    bbox = block.get("bbox", (0, 0, 0, 0))
    w = max(0.0, bbox[2] - bbox[0])
    h = max(0.0, bbox[3] - bbox[1])
    return w * h


def check_section_split(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect heading on one page with most body content on the next page."""
    results: list[CheckResult] = []
    total_pages = doc.page_count

    for i in range(total_pages - 1):
        page_num = i + 1
        page = doc[i]
        next_page = doc[i + 1]

        page_dict = page.get_text("dict")
        text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
        meaningful = [b for b in text_blocks if _block_text(b)]

        if not meaningful:
            continue

        median_body = _median_body_size(text_blocks)
        if median_body <= 0:
            continue

        page_height = page.rect.height
        bottom_threshold = page_height * BOTTOM_CANDIDATE_FRACTION

        # Sort by vertical position
        meaningful.sort(key=lambda b: b["bbox"][1])

        # Find headings in the bottom portion
        for block in meaningful:
            if block["bbox"][1] < bottom_threshold:
                continue

            font_size = _block_max_font_size(block)
            text = _block_text(block)

            if font_size < median_body * HEADING_SIZE_FACTOR:
                continue
            if len(text) > 100:
                continue

            # Count body text area below this heading on the CURRENT page
            block_bottom = block["bbox"][3]
            body_area_current = 0.0
            for other in meaningful:
                if other["bbox"][1] > block_bottom:
                    if _block_max_font_size(other) < font_size:
                        body_area_current += _text_block_area(other)

            # Count body text area on the NEXT page (before any next heading)
            next_dict = next_page.get_text("dict")
            next_blocks = [
                b for b in next_dict.get("blocks", [])
                if b.get("type") == 0 and _block_text(b)
            ]
            next_blocks.sort(key=lambda b: b["bbox"][1])

            body_area_next = 0.0
            for nb in next_blocks:
                nb_size = _block_max_font_size(nb)
                if nb_size >= median_body * HEADING_SIZE_FACTOR and len(_block_text(nb)) <= 100:
                    break  # hit the next heading
                body_area_next += _text_block_area(nb)

            total_body = body_area_current + body_area_next
            if total_body <= 0:
                continue

            next_ratio = body_area_next / total_body
            if next_ratio >= SPLIT_THRESHOLD:
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="SECTION_SPLIT",
                    message=(
                        f"Heading '{text[:50]}' on page {page_num} but "
                        f"{next_ratio:.0%} of its body is on page {page_num + 1}"
                    ),
                    pdf_path=pdf_path,
                    check="section_split",
                    page=page_num,
                ))

    return results
