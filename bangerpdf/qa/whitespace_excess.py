"""
qa.whitespace_excess — page >70% whitespace with no full-bleed imagery.

Different from density.py's DENSITY_ORPHAN_MAX (18% density = 82% whitespace).
This check fires at a less extreme threshold (>70% whitespace = <30% density)
and specifically exempts pages with full-bleed images that are intentionally
sparse on text.

Catches pages that are accidentally mostly empty — not intentional hero pages.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# A page with less than 30% content density is flagged
WHITESPACE_DENSITY_MAX = 0.30

# An image covering >50% of the page is considered "full-bleed" and exempts the page
FULL_BLEED_IMAGE_FRACTION = 0.50


def _has_full_bleed_image(page: fitz.Page) -> bool:
    """Check if the page has an image covering >50% of its area."""
    page_area = page.rect.width * page.rect.height
    if page_area <= 0:
        return False

    page_dict = page.get_text("dict")
    for block in page_dict.get("blocks", []):
        # Image blocks have type == 1
        if block.get("type") != 1:
            continue
        bbox = block.get("bbox")
        if not bbox:
            continue
        w = max(0.0, bbox[2] - bbox[0])
        h = max(0.0, bbox[3] - bbox[1])
        image_area = w * h
        if image_area / page_area >= FULL_BLEED_IMAGE_FRACTION:
            return True

    return False


def _page_content_density(page: fitz.Page) -> float:
    """Fraction of page area covered by all blocks (text + image)."""
    page_area = page.rect.width * page.rect.height
    if page_area <= 0:
        return 0.0

    covered = 0.0
    page_dict = page.get_text("dict")
    for block in page_dict.get("blocks", []):
        bbox = block.get("bbox")
        if not bbox:
            continue
        w = max(0.0, bbox[2] - bbox[0])
        h = max(0.0, bbox[3] - bbox[1])
        covered += w * h

    return min(covered / page_area, 1.0)


def check_whitespace_excess(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect pages with >70% whitespace and no full-bleed imagery."""
    results: list[CheckResult] = []
    total_pages = doc.page_count

    for i, page in enumerate(doc):
        page_num = i + 1

        # Last page is allowed to be sparse
        if page_num == total_pages:
            continue

        density = _page_content_density(page)

        if density >= WHITESPACE_DENSITY_MAX:
            continue  # not excessively white

        # Exempt pages with full-bleed images (intentional hero/photo pages)
        if _has_full_bleed_image(page):
            continue

        results.append(CheckResult(
            severity=Severity.WARNING,
            code="WHITESPACE_EXCESS",
            message=(
                f"Page is {1 - density:.0%} whitespace with no full-bleed imagery "
                f"({density:.0%} content density)"
            ),
            pdf_path=pdf_path,
            check="whitespace_excess",
            page=page_num,
        ))

    return results
