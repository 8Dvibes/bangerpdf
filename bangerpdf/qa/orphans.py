"""
qa.orphans — orphan section header and orphan signature block detection.

Catches Joe Fishback bid bug #3: bid proposal page 8 had only a signature
block, with the rest of the page empty. The signature block should have been
pulled up onto page 7 with the rest of the closing content.

Heuristics:
  - "Orphan section header" = the bottommost text block on a non-final page
    is significantly larger than body text (heading-sized) AND there is no
    body text block below it on the same page.
  - "Orphan signature block" = a page contains exactly one text block AND
    that block matches the signature/acceptance regex.
"""

from __future__ import annotations

import re

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


SIGNATURE_PATTERNS = [
    re.compile(r"\bsignature\b", re.IGNORECASE),
    re.compile(r"\baccepted?\s+by\b", re.IGNORECASE),
    re.compile(r"\bsigned\b", re.IGNORECASE),
    re.compile(r"\bauthorized\s+signature\b", re.IGNORECASE),
    re.compile(r"\bdate\s*[:_]", re.IGNORECASE),
    re.compile(r"_{5,}", re.IGNORECASE),  # signature line
    re.compile(r"X\s*_{3,}", re.IGNORECASE),  # X_____
]

# Heading-size threshold relative to median body font on the same page
HEADING_SIZE_MULTIPLIER = 1.4


def _block_text(block: dict) -> str:
    """Concatenate all spans in a text block to a single string."""
    out = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            out.append(span.get("text", ""))
        out.append(" ")
    return "".join(out).strip()


def _block_max_font_size(block: dict) -> float:
    """Return the max font size across all spans in a text block."""
    sizes = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            sizes.append(span.get("size", 0.0))
    return max(sizes) if sizes else 0.0


def _page_median_body_size(blocks: list[dict]) -> float:
    """Return the median font size across all spans on the page (body baseline)."""
    sizes = []
    for block in blocks:
        if block.get("type") != 0:  # only text blocks
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                sizes.append(span.get("size", 0.0))
    if not sizes:
        return 0.0
    sizes.sort()
    return sizes[len(sizes) // 2]


def _matches_signature(text: str) -> bool:
    return any(pat.search(text) for pat in SIGNATURE_PATTERNS)


def check_orphan_signature(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect pages whose only content is a signature block.

    Catches Joe bug #3.
    """
    results: list[CheckResult] = []

    for i, page in enumerate(doc):
        page_num = i + 1
        page_dict = page.get_text("dict")
        text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]

        # Filter out empty blocks
        meaningful = [b for b in text_blocks if _block_text(b)]

        if len(meaningful) == 0:
            continue

        # Check if all meaningful blocks combined match the signature pattern
        # AND there are very few of them (1-3 blocks max)
        if len(meaningful) <= 3:
            combined_text = " ".join(_block_text(b) for b in meaningful)
            if _matches_signature(combined_text):
                # Also confirm the page is mostly empty (signature blocks are small)
                page_area = page.rect.width * page.rect.height
                covered = sum(
                    max(0.0, (b["bbox"][2] - b["bbox"][0])) *
                    max(0.0, (b["bbox"][3] - b["bbox"][1]))
                    for b in meaningful
                )
                density = covered / page_area if page_area > 0 else 0
                if density < 0.30:
                    results.append(CheckResult(
                        severity=Severity.ERROR,
                        code="ORPHAN_SIGNATURE_BLOCK",
                        message=f"Page contains only a signature/acceptance block ({density:.0%} density)",
                        pdf_path=pdf_path,
                        check="orphans",
                        page=page_num,
                    ))

    return results


def check_orphan_section_header(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect heading-sized blocks at the bottom of a page with no body below.

    Anti-pattern: a section title that gets stranded at the bottom of one
    page while its body content starts on the next.
    """
    results: list[CheckResult] = []
    total_pages = doc.page_count

    for i, page in enumerate(doc):
        page_num = i + 1
        if page_num == total_pages:
            continue  # last page can't orphan a header

        page_dict = page.get_text("dict")
        text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
        meaningful = [b for b in text_blocks if _block_text(b)]
        if not meaningful:
            continue

        median_body = _page_median_body_size(text_blocks)
        if median_body <= 0:
            continue

        # Sort by y-position (top to bottom)
        meaningful.sort(key=lambda b: b["bbox"][1])

        # The bottom-most block
        last_block = meaningful[-1]
        last_size = _block_max_font_size(last_block)
        last_text = _block_text(last_block)

        # Heading-sized?
        if last_size < median_body * HEADING_SIZE_MULTIPLIER:
            continue

        # Short text (headings are short)
        if len(last_text) > 80:
            continue

        # And it's near the bottom of the page (last 20% of page height)
        page_height = page.rect.height
        block_y_top = last_block["bbox"][1]
        if block_y_top < page_height * 0.80:
            continue

        results.append(CheckResult(
            severity=Severity.WARNING,
            code="ORPHAN_SECTION_HEADER",
            message=f"Heading-sized block '{last_text[:50]}' at page bottom may be orphaned from its body",
            pdf_path=pdf_path,
            check="orphans",
            page=page_num,
        ))

    return results
