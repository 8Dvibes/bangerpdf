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

from bangerpdf.qa import density, images, orphans, variables
from bangerpdf.qa.types import FileReport, QAReport, Severity


# Mapping of check name → callable. Each callable takes (doc, pdf_path) and
# returns list[CheckResult]. Special-case: density also returns the per-page
# density list, so it has its own handling in _check_file.
CHECKS = {
    "density":      density.check_density,         # special: returns (results, densities)
    "page_count":   density.check_page_count,      # special: needs expected
    "orphan_sig":   orphans.check_orphan_signature,
    "orphan_hdr":   orphans.check_orphan_section_header,
    "unresolved":   variables.check_unresolved_vars,
    "images":       images.check_image_refs,
}


class QARunner:
    """Run QA checks against a directory or single PDF.

    Args:
        corpus_dir: Path to a directory of PDFs OR a single PDF file.
        expected_pages: Optional dict mapping pdf filename → expected page count.
        only: Optional set of check names to run (default: all active checks).
        data_path: Optional path to a data.json file for non-PDF checks
            (currently used for the Jinja2 dict.items collision check).
    """

    def __init__(
        self,
        corpus_dir: str | Path,
        expected_pages: dict[str, int] | None = None,
        only: set[str] | None = None,
        data_path: str | Path | None = None,
    ):
        self.corpus_dir = Path(corpus_dir).expanduser().resolve()
        self.expected_pages = expected_pages or {}
        self.only = set(only) if only else None
        self.data_path = Path(data_path).expanduser().resolve() if data_path else None

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
        results = []
        avg_density = 0.0

        try:
            # density check is special: it also returns the per-page density list,
            # which we need for the FileReport summary
            if self._should_run("density"):
                d_results, densities = density.check_density(doc, str(pdf_path))
                results.extend(d_results)
                if densities:
                    avg_density = sum(densities) / len(densities)
            else:
                # Still compute density for the summary even if check is suppressed
                densities = [density.page_density(p) for p in doc]
                if densities:
                    avg_density = sum(densities) / len(densities)

            # page_count check is special: needs expected
            if self._should_run("page_count"):
                expected = self.expected_pages.get(pdf_path.name)
                results.extend(density.check_page_count(doc, str(pdf_path), expected))

            # orphan signature check
            if self._should_run("orphan_sig"):
                results.extend(orphans.check_orphan_signature(doc, str(pdf_path)))

            # orphan section header check
            if self._should_run("orphan_hdr"):
                results.extend(orphans.check_orphan_section_header(doc, str(pdf_path)))

            # unresolved Jinja2 vars
            if self._should_run("unresolved"):
                results.extend(variables.check_unresolved_vars(doc, str(pdf_path)))

            # broken image refs
            if self._should_run("images"):
                results.extend(images.check_image_refs(doc, str(pdf_path)))

            return FileReport(
                pdf_path=str(pdf_path),
                page_count=doc.page_count,
                avg_density=avg_density,
                results=results,
            )
        finally:
            doc.close()

    def run(self) -> QAReport:
        report = QAReport(corpus_dir=str(self.corpus_dir))

        # File-level checks
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
                from bangerpdf.qa.types import CheckResult
                file_report.results.append(CheckResult(
                    severity=Severity.ERROR,
                    code="QA_RUN_FAILED",
                    message=f"QA failed to read PDF: {e}",
                    pdf_path=str(pdf_path),
                    check="runner",
                ))
                report.files.append(file_report)

        # Data-level checks (Jinja2 dict.items collision)
        if self.data_path and self.data_path.exists() and self._should_run("unresolved"):
            report.cross_doc_results.extend(
                variables.check_jinja_collisions(self.data_path)
            )

        return report
