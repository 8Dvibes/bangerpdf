"""
qa.pdfx — PDF/X and PDF/A compliance markers.

Print shops require PDF/X (subset of PDF designed for graphics interchange)
for commercial offset jobs. Compliance markers live in the XMP metadata.

Notable PDF/X variants:
  - PDF/X-1a: oldest, no live transparency, all CMYK
  - PDF/X-3: allows color management, RGB and CMYK
  - PDF/X-4: live transparency + layers, modern standard for commercial print

PDF/A is a separate ISO standard for archival PDFs. We can detect it but
it's optional unless the user explicitly required it.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


PDFX_MARKERS = [
    "GTS_PDFXVersion",
    "pdfx:GTS_PDFXVersion",
    "pdfxid:GTS_PDFXVersion",
]

PDFA_MARKERS = [
    "pdfaid:part",
    "PDF/A",
]


def _detect_pdfx_version(xml_metadata: str) -> str | None:
    """Extract the PDF/X version from XMP metadata if present."""
    if not xml_metadata:
        return None
    for marker in PDFX_MARKERS:
        if marker in xml_metadata:
            # Try to extract the version string after the marker
            try:
                idx = xml_metadata.index(marker)
                snippet = xml_metadata[idx:idx + 200]
                # Look for >X-NaN<
                if "PDF/X-" in snippet:
                    start = snippet.index("PDF/X-")
                    end = snippet.find("<", start)
                    if end > start:
                        return snippet[start:end].strip()
                return marker
            except ValueError:
                continue
    return None


def _detect_pdfa(xml_metadata: str) -> bool:
    if not xml_metadata:
        return False
    return any(marker in xml_metadata for marker in PDFA_MARKERS)


def check_pdfx_compliance(
    doc: fitz.Document,
    pdf_path: str,
    require_pdfx: bool = False,
    require_pdfa: bool = False,
) -> list[CheckResult]:
    """Inspect XMP metadata for PDF/X and PDF/A markers.

    Args:
        doc: open PDF document
        pdf_path: file path for error messages
        require_pdfx: if True, missing PDF/X markers raise an error
        require_pdfa: if True, missing PDF/A markers raise an error
    """
    results: list[CheckResult] = []

    try:
        xml_meta = doc.xref_xml_metadata() if hasattr(doc, "xref_xml_metadata") else ""
    except Exception:
        xml_meta = ""

    if not xml_meta:
        try:
            xml_meta = doc.get_xml_metadata() or ""
        except Exception:
            xml_meta = ""

    pdfx_version = _detect_pdfx_version(xml_meta)
    has_pdfa = _detect_pdfa(xml_meta)

    if require_pdfx and not pdfx_version:
        results.append(CheckResult(
            severity=Severity.ERROR,
            code="PDFX_MISSING",
            message="No PDF/X compliance markers found in XMP metadata — print shop will reject for commercial tier",
            pdf_path=pdf_path,
            check="pdfx",
        ))

    if require_pdfa and not has_pdfa:
        results.append(CheckResult(
            severity=Severity.ERROR,
            code="PDFA_MISSING",
            message="No PDF/A compliance markers found in XMP metadata",
            pdf_path=pdf_path,
            check="pdfx",
        ))

    return results
