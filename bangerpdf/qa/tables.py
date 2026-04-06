"""
qa.tables — table row split detection.

Anti-pattern: a multi-row table whose rows get split across a page break.
The classic symptom is the last block on page N being a row of the same
table whose subsequent rows continue at the top of page N+1.

Detection is heuristic. We don't have semantic table awareness — we look
for visual patterns:

    1. Find horizontal "rows" on each page (groups of blocks with similar
       y positions and consistent x spacing).
    2. If a row is the bottom-most content on page N AND another row with
       similar x stride starts at the top of page N+1, flag it.

False positives are possible (any two-column layout will look table-y).
We bias toward NOT flagging unless the pattern is unambiguous (3+ blocks
in a row, page-break gap, similar layout on both sides).
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# How close on the y-axis blocks must be to count as the same "row" (PDF points)
ROW_Y_TOLERANCE_PT = 4.0

# Minimum number of blocks in a row for it to look like a table row
MIN_ROW_BLOCKS = 3

# How close to the page edge a row must be to count as page-bottom or page-top
EDGE_DISTANCE_PT = 30.0


def _find_rows(blocks: list[dict]) -> list[list[dict]]:
    """Group blocks into y-aligned rows."""
    text_blocks = [b for b in blocks if b.get("type") == 0 and b.get("bbox")]
    text_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))

    rows: list[list[dict]] = []
    current_row: list[dict] = []
    current_y: float | None = None

    for block in text_blocks:
        y = block["bbox"][1]
        if current_y is None or abs(y - current_y) <= ROW_Y_TOLERANCE_PT:
            current_row.append(block)
            current_y = y if current_y is None else (current_y + y) / 2
        else:
            if current_row:
                rows.append(current_row)
            current_row = [block]
            current_y = y

    if current_row:
        rows.append(current_row)

    # Sort each row left-to-right
    for row in rows:
        row.sort(key=lambda b: b["bbox"][0])

    return rows


def _row_x_stride(row: list[dict]) -> tuple[float, ...]:
    """Return the x-positions of the row's columns (signature for matching)."""
    return tuple(round(b["bbox"][0], 0) for b in row)


def check_table_split(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Detect tables whose rows are split across page breaks."""
    results: list[CheckResult] = []
    total_pages = doc.page_count
    if total_pages < 2:
        return results

    prev_bottom_row: tuple[float, ...] | None = None
    prev_page_num: int | None = None

    for i, page in enumerate(doc):
        page_num = i + 1
        page_dict = page.get_text("dict")
        rows = _find_rows(page_dict.get("blocks", []))

        if not rows:
            prev_bottom_row = None
            prev_page_num = page_num
            continue

        page_h = page.rect.height

        # Bottom row of this page
        bottom_row = rows[-1]
        bottom_y = bottom_row[0]["bbox"][3]  # y1 of first block in row
        is_at_bottom = (page_h - bottom_y) <= EDGE_DISTANCE_PT
        is_table_row = len(bottom_row) >= MIN_ROW_BLOCKS

        # Top row of this page
        top_row = rows[0]
        top_y = top_row[0]["bbox"][1]  # y0 of first block
        is_at_top = top_y <= EDGE_DISTANCE_PT
        is_top_table_row = len(top_row) >= MIN_ROW_BLOCKS

        # Match against previous page's bottom row
        if (
            prev_bottom_row is not None
            and is_top_table_row
            and is_at_top
            and _row_x_stride(top_row) == prev_bottom_row
        ):
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="TABLE_ROW_SPLIT",
                message=(
                    f"Table appears to span the page break between p.{prev_page_num} and p.{page_num} — "
                    f"keep the row group together with `page-break-inside: avoid`"
                ),
                pdf_path=pdf_path,
                check="tables",
                page=page_num,
            ))

        # Save bottom-row signature for next iteration
        if is_at_bottom and is_table_row:
            prev_bottom_row = _row_x_stride(bottom_row)
        else:
            prev_bottom_row = None
        prev_page_num = page_num

    return results
