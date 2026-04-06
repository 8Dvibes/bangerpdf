"""
qa.types — shared dataclasses and enums for the QA checker.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    @property
    def marker(self) -> str:
        return {"info": "·", "warning": "⚠", "error": "✗"}[self.value]


@dataclass
class CheckResult:
    """Single finding from a QA check.

    Multiple results can be returned by one check (e.g. one per page that
    triggered). The runner aggregates all results across all checks across
    all PDFs in the corpus.
    """
    severity: Severity
    code: str                           # e.g. "DENSITY_LOW", "ORPHAN_SIGNATURE"
    message: str                        # human-readable
    pdf_path: str                       # absolute path to the PDF
    check: str                          # check name (e.g. "density")
    page: int | None = None             # 1-indexed page number when applicable
    bbox: tuple[float, float, float, float] | None = None  # PDF points

    def __str__(self) -> str:
        loc = f" p.{self.page}" if self.page else ""
        return f"{self.severity.marker} [{self.code}]{loc} {self.message}"


@dataclass
class FileReport:
    """Aggregated QA results for a single PDF file."""
    pdf_path: str
    page_count: int
    avg_density: float                  # 0.0–1.0, average across pages
    results: list[CheckResult] = field(default_factory=list)

    @property
    def errors(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == Severity.WARNING]

    @property
    def infos(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == Severity.INFO]

    @property
    def is_clean(self) -> bool:
        return not self.errors and not self.warnings


@dataclass
class QAReport:
    """Top-level QA report covering an entire corpus."""
    corpus_dir: str
    files: list[FileReport] = field(default_factory=list)
    cross_doc_results: list[CheckResult] = field(default_factory=list)

    @property
    def all_results(self) -> list[CheckResult]:
        out = list(self.cross_doc_results)
        for f in self.files:
            out.extend(f.results)
        return out

    @property
    def errors(self) -> list[CheckResult]:
        return [r for r in self.all_results if r.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[CheckResult]:
        return [r for r in self.all_results if r.severity == Severity.WARNING]

    @property
    def is_clean(self) -> bool:
        return not self.errors and not self.warnings

    def exit_code(self, strict: bool = False) -> int:
        """Return the right exit code for the CLI.

        Strict mode: exit nonzero on any warning OR error.
        Non-strict: exit nonzero only on errors.
        """
        if self.errors:
            return 2
        if strict and self.warnings:
            return 1
        return 0
