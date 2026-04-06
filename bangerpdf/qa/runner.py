"""
qa.runner — orchestrator for the bangerpdf QA checker.

Opens each PDF in a corpus once, runs every active check against it, and
returns a structured QAReport. Optimized to avoid re-parsing the document.

Usage:
    from bangerpdf.qa.runner import QARunner
    runner = QARunner("path/to/pdfs/", expected_pages={"01_Cover.pdf": 2})
    report = runner.run()
    print(report.exit_code(strict=False))
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from bangerpdf.qa import (
    bleed,
    cross_doc,
    density,
    fonts,
    images,
    links,
    orphans,
    overflow,
    pdfx,
    tables,
    variables,
)
from bangerpdf.qa.types import CheckResult, FileReport, QAReport, Severity


# Active per-file checks. Order matters for output readability.
PER_FILE_CHECKS = [
    "density",
    "page_count",
    "orphan_sig",
    "orphan_hdr",
    "tables",
    "overflow",
    "unresolved",
    "images",
    "fonts",
    "bleed",
    "pdfx",
    "links",
]

# Cross-corpus checks (run after all per-file checks)
CORPUS_CHECKS = [
    "jinja_collisions",
    "headline_consistency",
]

ALL_CHECKS = PER_FILE_CHECKS + CORPUS_CHECKS


class QARunner:
    """Run QA checks against a directory or single PDF.

    Args:
        corpus_dir: Path to a directory of PDFs OR a single PDF file.
        expected_pages: Optional dict mapping pdf filename → expected page count.
        only: Optional set of check names to run (default: all active checks).
        data_path: Optional path to a data.json file for the dict.items collision check.
        headlines: Optional dict of {label: expected_string} for cross-doc consistency.
        bleed_in: Expected bleed in inches (0 = skip, 0.125 = standard).
        require_pdfx: If True, missing PDF/X markers raise an error.
        require_pdfa: If True, missing PDF/A markers raise an error.
        check_links: If True, ping every external URL with HEAD requests.
    """

    def __init__(
        self,
        corpus_dir: str | Path,
        expected_pages: dict[str, int] | None = None,
        only: set[str] | None = None,
        data_path: str | Path | None = None,
        headlines: dict[str, str] | None = None,
        bleed_in: float = 0.0,
        require_pdfx: bool = False,
        require_pdfa: bool = False,
        check_links: bool = False,
    ):
        self.corpus_dir = Path(corpus_dir).expanduser().resolve()
        self.expected_pages = expected_pages or {}
        self.only = set(only) if only else None
        self.data_path = Path(data_path).expanduser().resolve() if data_path else None
        self.headlines = headlines or {}
        self.bleed_in = bleed_in
        self.require_pdfx = require_pdfx
        self.require_pdfa = require_pdfa
        self.check_links = check_links

    def _should_run(self, name: str) -> bool:
        return self.only is None or name in self.only

    def _discover_pdfs(self) -> list[Path]:
        if self.corpus_dir.is_file():
            if self.corpus_dir.suffix.lower() == ".pdf":
                return [self.corpus_dir]
            return []
        if not self.corpus_dir.is_dir():
            return []
        return sorted(self.corpus_dir.glob("*.pdf"))

    def _check_file(self, pdf_path: Path) -> FileReport:
        doc = fitz.open(pdf_path)
        results: list[CheckResult] = []
        avg_density = 0.0

        try:
            # density check is special: it also returns the per-page density list
            if self._should_run("density"):
                d_results, densities = density.check_density(doc, str(pdf_path))
                results.extend(d_results)
                if densities:
                    avg_density = sum(densities) / len(densities)
            else:
                densities = [density.page_density(p) for p in doc]
                if densities:
                    avg_density = sum(densities) / len(densities)

            # page_count check is special: needs expected
            if self._should_run("page_count"):
                expected = self.expected_pages.get(pdf_path.name)
                results.extend(density.check_page_count(doc, str(pdf_path), expected))

            if self._should_run("orphan_sig"):
                results.extend(orphans.check_orphan_signature(doc, str(pdf_path)))

            if self._should_run("orphan_hdr"):
                results.extend(orphans.check_orphan_section_header(doc, str(pdf_path)))

            if self._should_run("tables"):
                results.extend(tables.check_table_split(doc, str(pdf_path)))

            if self._should_run("overflow"):
                results.extend(overflow.check_content_overflow(doc, str(pdf_path)))

            if self._should_run("unresolved"):
                results.extend(variables.check_unresolved_vars(doc, str(pdf_path)))

            if self._should_run("images"):
                results.extend(images.check_image_refs(doc, str(pdf_path)))

            if self._should_run("fonts"):
                results.extend(fonts.check_fonts_embedded(doc, str(pdf_path)))

            if self._should_run("bleed"):
                results.extend(bleed.check_bleed(doc, str(pdf_path), self.bleed_in))

            if self._should_run("pdfx"):
                results.extend(pdfx.check_pdfx_compliance(
                    doc,
                    str(pdf_path),
                    require_pdfx=self.require_pdfx,
                    require_pdfa=self.require_pdfa,
                ))

            if self._should_run("links"):
                results.extend(links.check_links(
                    doc,
                    str(pdf_path),
                    enabled=self.check_links,
                ))

            return FileReport(
                pdf_path=str(pdf_path),
                page_count=doc.page_count,
                avg_density=avg_density,
                results=results,
            )
        finally:
            doc.close()

    def _run_corpus_checks(self, report: QAReport) -> None:
        # Jinja2 dict.items collision check (data.json based)
        if (
            self.data_path
            and self.data_path.exists()
            and self._should_run("jinja_collisions")
        ):
            report.cross_doc_results.extend(
                variables.check_jinja_collisions(self.data_path)
            )

        # Headline consistency across PDFs
        if self.headlines and self._should_run("headline_consistency"):
            report.cross_doc_results.extend(
                cross_doc.check_headline_consistency(
                    corpus_dir=self.corpus_dir,
                    headlines=self.headlines,
                )
            )

    def run(self) -> QAReport:
        report = QAReport(corpus_dir=str(self.corpus_dir))

        # Per-file checks
        pdf_files = self._discover_pdfs()
        for pdf_path in pdf_files:
            try:
                file_report = self._check_file(pdf_path)
                report.files.append(file_report)
            except Exception as e:
                # Don't let one bad PDF kill the whole run
                file_report = FileReport(
                    pdf_path=str(pdf_path),
                    page_count=0,
                    avg_density=0.0,
                )
                file_report.results.append(CheckResult(
                    severity=Severity.ERROR,
                    code="QA_RUN_FAILED",
                    message=f"QA failed to read PDF: {e}",
                    pdf_path=str(pdf_path),
                    check="runner",
                ))
                report.files.append(file_report)

        # Corpus-level checks
        self._run_corpus_checks(report)

        return report
