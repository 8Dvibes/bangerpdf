"""
qa.variables — unresolved Jinja2 variable detection.

Catches Joe Fishback bid bug #6: a Jinja2 dict.items collision shadowed
the Python method, leaving raw `{{ items }}` text in the rendered PDF.

Two checks:
  - check_unresolved_vars(doc): scan rendered PDF text for surviving `{{` / `}}`
  - check_jinja_collisions(data): inspect data.json for keys that shadow
    builtin dict methods (items, keys, values, update, get, pop, copy, etc.)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


# Jinja2 delimiters that should never survive a successful render
UNRESOLVED_PATTERN = re.compile(r"\{\{[^}]*\}\}|\{%[^%]*%\}")

# Python dict methods that collide with Jinja2 attribute lookup
RESERVED_DICT_METHODS = {
    "items", "keys", "values", "update", "get", "pop", "popitem",
    "copy", "clear", "setdefault", "fromkeys",
}


def check_unresolved_vars(doc: fitz.Document, pdf_path: str) -> list[CheckResult]:
    """Scan every page for surviving Jinja2 delimiters."""
    results: list[CheckResult] = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        matches = UNRESOLVED_PATTERN.findall(text)
        if matches:
            sample = matches[0][:60]
            results.append(CheckResult(
                severity=Severity.ERROR,
                code="UNRESOLVED_JINJA_VAR",
                message=f"Found {len(matches)} unresolved Jinja2 expression(s) on page (e.g. '{sample}')",
                pdf_path=pdf_path,
                check="variables",
                page=i + 1,
            ))

    return results


def check_jinja_collisions(data_path: str | Path) -> list[CheckResult]:
    """Inspect a data.json file for keys that shadow Python dict methods.

    Catches Joe bug #6 BEFORE rendering: if data['items'] exists, then
    data.items in a Jinja2 template will return [('a', 1), ('b', 2)] instead
    of the value of data['items'].
    """
    results: list[CheckResult] = []
    p = Path(data_path)
    if not p.exists():
        return results

    try:
        with p.open() as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        results.append(CheckResult(
            severity=Severity.ERROR,
            code="DATA_JSON_INVALID",
            message=f"Could not parse {p.name}: {e}",
            pdf_path=str(p),
            check="variables",
        ))
        return results

    def walk(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                key_path = f"{path}.{key}" if path else key
                if key in RESERVED_DICT_METHODS:
                    results.append(CheckResult(
                        severity=Severity.WARNING,
                        code="JINJA_DICT_COLLISION",
                        message=(
                            f"Key '{key_path}' shadows the Python dict.{key}() method — "
                            f"in Jinja2 templates, `data.{key}` will return the method, not the value. "
                            f"Use `data['{key}']` or rename the key."
                        ),
                        pdf_path=str(p),
                        check="variables",
                    ))
                walk(value, key_path)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]")

    walk(data)
    return results
