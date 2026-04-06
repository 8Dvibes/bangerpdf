"""
qa.bleed — verify bleed area is present for digital-press and commercial tiers.

Bleed is the part of a printed design that extends past the trim line so
the cut sheet has color all the way to the edge with no white slivers from
trimming inaccuracy. Standard bleed is 0.125 inches (9 PDF points) on all
four sides.

In PDF terms:
  - MediaBox = the actual sheet size (including bleed area)
  - TrimBox  = where the printer cuts (the final trimmed page size)
  - The difference between them on each axis is 2 × bleed_in (one side per edge)

If a PDF is destined for a digital-press or commercial-offset tier and
the MediaBox does not extend past the TrimBox by the expected bleed, the
print shop will likely reject it or print white slivers at the edges.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# 1 inch = 72 PDF points
PT_PER_INCH = 72.0
DEFAULT_BLEED_IN = 0.125
TOLERANCE_PT = 1.0


def check_bleed(
    doc: fitz.Document,
    pdf_path: str,
    expected_bleed_in: float = 0.0,
) -> list[CheckResult]:
    """Verify the bleed area on every page meets expectations.

    Args:
        doc: open PDF document
        pdf_path: file path for error messages
        expected_bleed_in: required bleed in inches. Pass 0 to skip the check
            (used for the desktop tier where bleed isn't required).
    """
    results: list[CheckResult] = []

    if expected_bleed_in <= 0:
        return results

    expected_bleed_pt = expected_bleed_in * PT_PER_INCH

    for i, page in enumerate(doc):
        # PyMuPDF: page.mediabox is the MediaBox; page.trimbox is the TrimBox
        # if defined, otherwise the same as mediabox.
        try:
            mediabox = page.mediabox
            trimbox = page.trimbox
        except AttributeError:
            # Older PyMuPDF versions
            mediabox = page.rect
            trimbox = page.rect

        # Compute the inset of trimbox relative to mediabox on each side
        try:
            left = trimbox.x0 - mediabox.x0
            top = trimbox.y0 - mediabox.y0
            right = mediabox.x1 - trimbox.x1
            bottom = mediabox.y1 - trimbox.y1
        except AttributeError:
            # If we can't read it, skip silently
            continue

        min_inset = min(left, top, right, bottom)
        if min_inset < expected_bleed_pt - TOLERANCE_PT:
            results.append(CheckResult(
                severity=Severity.ERROR,
                code="BLEED_MISSING",
                message=(
                    f"Page bleed is {min_inset / PT_PER_INCH:.3f}in but expected "
                    f"{expected_bleed_in}in — the print shop will reject this for the "
                    f"commercial tier"
                ),
                pdf_path=pdf_path,
                check="bleed",
                page=i + 1,
            ))

    return results
