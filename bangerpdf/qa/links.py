"""
qa.links — broken external URL detection.

Walks every page's link annotations, extracts http(s) URIs, and pings each
with a HEAD request. Results are cached to ~/.cache/bangerpdf/links-cache.json
so repeat runs over a stable corpus are fast.

Off by default — network checks are slow and depend on the user's connection.
Enable with `bangerpdf qa --check-links`.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import fitz  # PyMuPDF

from bangerpdf.qa.types import CheckResult, Severity


CACHE_PATH = Path("~/.cache/bangerpdf/links-cache.json").expanduser()
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 1 week
DEFAULT_TIMEOUT = 5.0


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        with CACHE_PATH.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CACHE_PATH.open("w") as f:
            json.dump(cache, f)
    except OSError:
        pass


def _check_url(uri: str, timeout: float) -> int:
    """Return HTTP status code, or -1 on connection error, -2 on timeout."""
    try:
        req = urllib.request.Request(uri, method="HEAD", headers={
            "User-Agent": "bangerpdf-qa/0.2 (link-check)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except urllib.error.URLError as e:
        if "timed out" in str(e).lower():
            return -2
        return -1
    except Exception:
        return -1


def check_links(
    doc: fitz.Document,
    pdf_path: str,
    enabled: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
) -> list[CheckResult]:
    """Verify external links return non-error HTTP status."""
    results: list[CheckResult] = []
    if not enabled:
        return results

    cache = _load_cache()
    now = time.time()
    cache_changed = False

    seen_uris: set[str] = set()

    for i, page in enumerate(doc):
        try:
            links = page.get_links()
        except Exception:
            continue

        for link in links:
            uri = link.get("uri")
            if not uri or not uri.startswith(("http://", "https://")):
                continue
            if uri in seen_uris:
                continue
            seen_uris.add(uri)

            # Cache lookup
            entry = cache.get(uri)
            if entry and (now - entry.get("checked_at", 0)) < CACHE_TTL_SECONDS:
                status = entry["status"]
            else:
                status = _check_url(uri, timeout)
                cache[uri] = {"status": status, "checked_at": now}
                cache_changed = True

            if status == -2:
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="LINK_TIMEOUT",
                    message=f"URL '{uri}' timed out after {timeout}s",
                    pdf_path=pdf_path,
                    check="links",
                    page=i + 1,
                ))
            elif status == -1:
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="LINK_UNREACHABLE",
                    message=f"URL '{uri}' could not be reached",
                    pdf_path=pdf_path,
                    check="links",
                    page=i + 1,
                ))
            elif status >= 400:
                results.append(CheckResult(
                    severity=Severity.WARNING,
                    code="LINK_BROKEN",
                    message=f"URL '{uri}' returned HTTP {status}",
                    pdf_path=pdf_path,
                    check="links",
                    page=i + 1,
                ))

    if cache_changed:
        _save_cache(cache)

    return results
