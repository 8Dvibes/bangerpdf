"""
qa.cross_doc — cross-document consistency checks.

When a doc pack contains multiple PDFs (cover letter + proposal + leave-behind +
phone scripts + thank-you email), the headline numbers should match across all
of them. The classic bug: bid amount changes in one doc but not the others.

Usage:
    cross_doc.check_headline_consistency(
        corpus_dir="/path/to/pdfs/",
        headlines={"bid_total": "$445,000", "client": "Atria Health"},
    )
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


def check_headline_consistency(
    corpus_dir: str | Path,
    headlines: dict[str, str],
) -> list[CheckResult]:
    """Verify each headline string appears in every PDF in the corpus.

    Args:
        corpus_dir: directory of PDFs to scan
        headlines: dict mapping a label (e.g. "bid_total") to the expected
            literal string to find (e.g. "$445,000")

    Returns:
        Warnings for headlines that are present in some but not all docs.
        (Headlines missing from EVERY doc are not flagged — that's intentional.)
    """
    results: list[CheckResult] = []
    if not headlines:
        return results

    corpus = Path(corpus_dir).expanduser().resolve()
    if corpus.is_file():
        return results  # cross-doc only applies to a directory

    if not corpus.is_dir():
        return results

    pdfs = sorted(corpus.glob("*.pdf"))
    if len(pdfs) < 2:
        return results  # need 2+ docs for cross-checking

    # Collect text from each PDF once
    full_texts: dict[str, str] = {}
    for pdf_path in pdfs:
        try:
            doc = fitz.open(pdf_path)
            try:
                full_texts[pdf_path.name] = " ".join(p.get_text("text") for p in doc)
            finally:
                doc.close()
        except Exception:
            continue

    for headline_name, expected in headlines.items():
        present_in: list[str] = []
        missing_in: list[str] = []

        for name, text in full_texts.items():
            if expected in text:
                present_in.append(name)
            else:
                missing_in.append(name)

        # Inconsistency = present in some but not all
        if present_in and missing_in:
            missing_str = ", ".join(missing_in[:3])
            if len(missing_in) > 3:
                missing_str += f" + {len(missing_in) - 3} more"
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="CROSS_DOC_INCONSISTENT",
                message=(
                    f"Headline '{headline_name}' = '{expected}' is in "
                    f"{len(present_in)}/{len(full_texts)} doc(s) but missing from: {missing_str}"
                ),
                pdf_path=str(corpus),
                check="cross_doc",
            ))
        elif not present_in and len(headlines) > 1:
            # Only flag entirely-missing if there are multiple headlines (so we
            # know the user is configured to cross-check this corpus)
            results.append(CheckResult(
                severity=Severity.WARNING,
                code="CROSS_DOC_MISSING",
                message=f"Headline '{headline_name}' = '{expected}' not found in any doc",
                pdf_path=str(corpus),
                check="cross_doc",
            ))

    return results
