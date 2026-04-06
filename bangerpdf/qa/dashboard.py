"""
qa.dashboard — terminal output renderer for QA reports.

Two modes:
  - render_dashboard(report) → human-readable terminal output (default)
  - render_json(report) → machine-readable JSON for piping
"""

from __future__ import annotations

import json
from pathlib import Path

from bangerpdf.qa.types import CheckResult, FileReport, QAReport, Severity


def _file_marker(file_report: FileReport) -> str:
    if file_report.errors:
        return "✗"
    if file_report.warnings:
        return "⚠"
    return "✓"


def _format_result(result: CheckResult, indent: str = "      ") -> str:
    loc = f" p.{result.page}" if result.page else ""
    return f"{indent}{result.severity.marker} [{result.code}]{loc} {result.message}"


def render_dashboard(report: QAReport) -> str:
    """Render a tier-aware human-readable QA dashboard."""
    lines: list[str] = []

    n_files = len(report.files)
    if n_files == 0:
        lines.append(f"No PDFs found in {report.corpus_dir}")
        return "\n".join(lines)

    lines.append(f"Checking {n_files} PDF{'s' if n_files != 1 else ''} in {report.corpus_dir}")
    lines.append("")

    # Per-file rows
    name_width = max((len(Path(f.pdf_path).name) for f in report.files), default=20)
    name_width = min(max(name_width, 20), 50)

    for file_report in report.files:
        name = Path(file_report.pdf_path).name
        marker = _file_marker(file_report)
        page_str = f"{file_report.page_count}p"
        density_str = f"{file_report.avg_density:.0%} avg density"
        lines.append(f"  {marker} {name:<{name_width}}  ({page_str}, {density_str})")

        # Show all errors first, then warnings, then infos
        for result in file_report.errors:
            lines.append(_format_result(result))
        for result in file_report.warnings:
            lines.append(_format_result(result))
        # infos suppressed by default to keep output tight

    # Cross-document section
    if report.cross_doc_results:
        lines.append("")
        lines.append("Cross-document consistency:")
        for result in report.cross_doc_results:
            lines.append(_format_result(result, indent="  "))

    # Summary
    lines.append("")
    n_err = len(report.errors)
    n_warn = len(report.warnings)
    if report.is_clean:
        lines.append(f"Result: 0 warnings, 0 errors. All {n_files} PDF{'s' if n_files != 1 else ''} clean.")
    else:
        parts = []
        if n_err:
            parts.append(f"{n_err} error{'s' if n_err != 1 else ''}")
        if n_warn:
            parts.append(f"{n_warn} warning{'s' if n_warn != 1 else ''}")
        lines.append(f"Result: {', '.join(parts)}.")

    return "\n".join(lines)


def render_json(report: QAReport) -> str:
    """Render the QA report as JSON for piping."""
    def result_to_dict(r: CheckResult) -> dict:
        return {
            "severity": r.severity.value,
            "code": r.code,
            "message": r.message,
            "pdf_path": r.pdf_path,
            "check": r.check,
            "page": r.page,
            "bbox": list(r.bbox) if r.bbox else None,
        }

    def file_to_dict(f: FileReport) -> dict:
        return {
            "pdf_path": f.pdf_path,
            "page_count": f.page_count,
            "avg_density": round(f.avg_density, 4),
            "results": [result_to_dict(r) for r in f.results],
        }

    out = {
        "corpus_dir": report.corpus_dir,
        "files": [file_to_dict(f) for f in report.files],
        "cross_doc_results": [result_to_dict(r) for r in report.cross_doc_results],
        "summary": {
            "n_files": len(report.files),
            "n_errors": len(report.errors),
            "n_warnings": len(report.warnings),
            "is_clean": report.is_clean,
        },
    }
    return json.dumps(out, indent=2)
