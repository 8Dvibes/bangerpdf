"""
qa.overflow — content running off the page boundary.

Distinct from the density check (which detects EMPTY pages), this catches
content whose bounding box extends past the page edge. Common cause: a wide
table or image that wasn't sized correctly for the page width, or a long
piece of unbreakable text (URL, code, etc).
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Tolerance in PDF points (1pt = 1/72 inch). 2pt is about 0.7mm, slightly
# more than the rendering rounding error so we don't false-positive on
# content that just touches the page edge.
OVERFLOW_TOLERANCE_PT = 2.0


def check_content_overflow(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect any block that extends past the page boundary."""
    results: list[CheckResult] = []

    for i, page in enumerate(doc):
        page_w = page.rect.width
        page_h = page.rect.height
        page_dict = page.get_text("dict")

        worst_block = None
        worst_overflow = 0.0

        for block in page_dict.get("blocks", []):
            bbox = block.get("bbox")
            if not bbox:
                continue
            x0, y0, x1, y1 = bbox

            right_overflow = max(0.0, x1 - page_w)
            bottom_overflow = max(0.0, y1 - page_h)
            left_overflow = max(0.0, -x0)
            top_overflow = max(0.0, -y0)

            total = right_overflow + bottom_overflow + left_overflow + top_overflow
            if total > OVERFLOW_TOLERANCE_PT and total > worst_overflow:
                worst_overflow = total
                worst_block = (bbox, right_overflow, bottom_overflow, left_overflow, top_overflow)

        if worst_block:
            bbox, r, b, l, t = worst_block
            sides = []
            if r > 0:
                sides.append(f"{r:.0f}pt past right edge")
            if b > 0:
                sides.append(f"{b:.0f}pt past bottom edge")
            if l > 0:
                sides.append(f"{l:.0f}pt past left edge")
            if t > 0:
                sides.append(f"{t:.0f}pt past top edge")
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="CONTENT_OVERFLOW",
                message=f"Content extends past page boundary ({', '.join(sides)})",
                pdf_path=pdf_path,
                check="overflow",
                page=i + 1,
                bbox=tuple(bbox),
            ))

    return results
