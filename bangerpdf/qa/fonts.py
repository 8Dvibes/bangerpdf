"""
qa.fonts — font embedding and subsetting verification.

Print-shop pre-press requires every font in the PDF to be embedded so the
output renders identically on the operator's machine. Type3 fonts are also
problematic — they're bitmap-based and look terrible at higher print DPI.

Uses PyMuPDF's page.get_fonts() which returns tuples of:
    (xref, ext, type, basefont, name, encoding, referencer)

The `ext` field is the embedded font file extension. Empty string means
the font is NOT embedded (only its name is referenced — the renderer has
to substitute a fallback).
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Standard 14 PDF base fonts that don't need embedding (PDF readers always have them)
PDF_BASE_FONTS = {
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Symbol", "ZapfDingbats",
}


def check_fonts_embedded(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Verify every non-base font in the document is fully embedded."""
    results: list[CheckResult] = []
    seen: set[tuple[str, str]] = set()

    for i, page in enumerate(doc):
        for font_tuple in page.get_fonts():
            # Defensive: PyMuPDF returns tuples of varying length
            if len(font_tuple) < 4:
                continue
            xref = font_tuple[0]
            ext = font_tuple[1]
            type_ = font_tuple[2]
            basefont = font_tuple[3]

            key = (basefont, type_)
            if key in seen:
                continue
            seen.add(key)

            # Skip the standard 14 base fonts
            stripped_basefont = basefont.split("+")[-1] if "+" in basefont else basefont
            if stripped_basefont in PDF_BASE_FONTS:
                continue

            # Type3 fonts are bitmap-based, problematic for print
            if type_ == "Type3":
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="FONT_TYPE3",
                    message=f"Font '{basefont}' is Type3 (bitmap-based) — not ideal for print",
                    pdf_path=pdf_path,
                    check="fonts",
                    page=i + 1,
                ))
                continue

            # Empty ext means not embedded
            if not ext:
                results.append(CheckResult(
                    severity=Severity.ERROR,
                    code="FONT_NOT_EMBEDDED",
                    message=(
                        f"Font '{basefont}' is not embedded — the print shop won't have it "
                        f"and a fallback font will be substituted"
                    ),
                    pdf_path=pdf_path,
                    check="fonts",
                ))

    return results
