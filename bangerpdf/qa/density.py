"""
qa.density — content density and page count checks.

Catches Joe Fishback bid bugs #1 + #2 (90% empty cover letter page 3, 70%
empty bid proposal page 3) and bug #4 (leave-behind spilled to 2 pages when
expected 1).

Uses PyMuPDF's page.get_text("dict") which returns nested blocks → lines →
spans, each with bbox: [x0, y0, x1, y1] in PDF points.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Density thresholds (fraction of page area covered by text+image block bboxes).
#
# These are calibrated against Joe Fishback's tightened bid PDFs (where pages
# range 21–39% density and are visually correct) and the original buggy state
# (where the broken pages were ~10% density). A typical professional document
# with 1" margins + normal line spacing lands in the 25–55% range.
DENSITY_ORPHAN_MAX = 0.18        # below this = page is mostly empty whitespace
DENSITY_OVERFLOW_MIN = 0.95      # above this = content packed too tightly
DENSITY_SINGLE_BLOCK_MAX = 0.10  # below this = page has only one tiny element


def page_density(page: fitz.Page) -> float:
    """Return the fraction of page area covered by text and image blocks."""
    page_area = page.rect.width * page.rect.height
    if page_area <= 0:
        return 0.0

    covered = 0.0
    page_dict = page.get_text("dict")
    for block in page_dict.get("blocks", []):
        bbox = block.get("bbox")
        if not bbox:
            continue
        x0, y0, x1, y1 = bbox
        w = max(0.0, x1 - x0)
        h = max(0.0, y1 - y0)
        covered += w * h

    return min(covered / page_area, 1.0)


def check_density(doc: fitz.Document, pdf_path: str) -> tuple[list[CheckResult], list[float]]:
    """Run the density check on every page.

    Returns:
        (results, per_page_densities)
    """
    results: list[CheckResult] = []
    densities: list[float] = []

    total_pages = doc.page_count

    for i, page in enumerate(doc):
        page_num = i + 1
        density = page_density(page)
        densities.append(density)

        # The last page is allowed to be sparse (it often is by design)
        is_last_page = page_num == total_pages

        if density < DENSITY_SINGLE_BLOCK_MAX and not is_last_page:
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="DENSITY_SINGLE_BLOCK",
                message=f"Page contains a single small element ({density:.0%} density)",
                pdf_path=pdf_path,
                check="density",
                page=page_num,
            ))
        elif density < DENSITY_ORPHAN_MAX and not is_last_page:
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="DENSITY_LOW",
                message=f"Page is mostly empty whitespace ({density:.0%} density)",
                pdf_path=pdf_path,
                check="density",
                page=page_num,
            ))
        elif density > DENSITY_OVERFLOW_MIN:
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="DENSITY_HIGH",
                message=f"Page is densely packed ({density:.0%} density), verify legibility",
                pdf_path=pdf_path,
                check="density",
                page=page_num,
            ))

    return results, densities


def check_page_count(
    doc: fitz.Document,
    pdf_path: str,
    expected: int | None = None,
) -> list[CheckResult]:
    """Verify page count matches expected.

    Catches Joe bug #4: leave-behind spilled from 1 page to 2.
    """
    results: list[CheckResult] = []
    actual = doc.page_count

    if expected is None:
        # No expectation — emit info only
        return results

    if actual != expected:
        results.append(CheckResult(
            severity=Severity.ERROR,
            code="PAGE_COUNT_MISMATCH",
            message=f"Expected {expected} page(s), got {actual}",
            pdf_path=pdf_path,
            check="page_count",
        ))

    return results
