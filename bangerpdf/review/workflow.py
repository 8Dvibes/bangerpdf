"""
workflow — State machine for Review Bundle lifecycle.

States: draft -> awaiting-feedback -> revising -> approved

The state is persisted in meta.json inside the review bundle directory.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Valid state transitions
_TRANSITIONS = {
    "draft": {"awaiting-feedback"},
    "awaiting-feedback": {"revising", "approved"},
    "revising": {"awaiting-feedback", "approved"},
    "approved": set(),  # terminal state
}


def _now_iso() -> str:
    """ISO-8601 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _meta_path(review_dir: str | Path) -> Path:
    return Path(review_dir) / "meta.json"


def _load_meta(review_dir: str | Path) -> dict:
    path = _meta_path(review_dir)
    if not path.exists():
        raise FileNotFoundError(f"No meta.json found in {review_dir}")
    with open(path) as f:
        return json.load(f)


def _save_meta(review_dir: str | Path, meta: dict) -> None:
    path = _meta_path(review_dir)
    with open(path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _transition(meta: dict, target: str) -> None:
    """Validate and apply a state transition."""
    current = meta["status"]
    allowed = _TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValueError(
            f"Cannot transition from '{current}' to '{target}'. "
            f"Allowed: {sorted(allowed) if allowed else 'none (terminal state)'}"
        )
    meta["status"] = target


def init_meta(review_dir: str | Path, source_pack: str | Path) -> dict:
    """Create meta.json for a new review bundle.

    Sets initial status to 'draft' with an empty decisions list.
    """
    review_dir = Path(review_dir)
    review_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "version": "v1",
        "status": "draft",
        "source_pack": str(Path(source_pack).resolve()),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "decisions": [],
        "approved_by": None,
        "approved_at": None,
    }

    _save_meta(review_dir, meta)
    return meta


def get_status(review_dir: str | Path) -> str:
    """Return the current status string from meta.json."""
    meta = _load_meta(review_dir)
    return meta["status"]


def get_meta(review_dir: str | Path) -> dict:
    """Return the full meta.json dict."""
    return _load_meta(review_dir)


def set_status(review_dir: str | Path, status: str) -> dict:
    """Directly set the status (with transition validation)."""
    meta = _load_meta(review_dir)
    _transition(meta, status)
    meta["updated_at"] = _now_iso()
    _save_meta(review_dir, meta)
    return meta


def add_annotation(
    review_dir: str | Path,
    doc: str,
    page: int,
    note: str,
) -> dict:
    """Append a decision/annotation to the review bundle.

    Automatically transitions from 'draft' to 'awaiting-feedback' on first
    annotation.
    """
    meta = _load_meta(review_dir)

    # Auto-transition draft -> awaiting-feedback on first annotation
    if meta["status"] == "draft":
        meta["status"] = "awaiting-feedback"

    # Generate decision ID
    decision_id = f"d{len(meta['decisions']) + 1}"

    decision = {
        "id": decision_id,
        "doc": doc,
        "page": page,
        "note": note,
        "resolved": False,
        "created_at": _now_iso(),
    }

    meta["decisions"].append(decision)
    meta["updated_at"] = _now_iso()
    _save_meta(review_dir, meta)
    return meta


def revise(review_dir: str | Path) -> dict:
    """Bump the review version (v1 -> v2, v2 -> v3, etc.) and set status to revising.

    Copies current PDFs into the next version's assets directory.
    """
    meta = _load_meta(review_dir)
    review_dir = Path(review_dir)

    # Parse current version number
    current_num = int(meta["version"].lstrip("v"))
    next_num = current_num + 1
    next_version = f"v{next_num}"

    # Transition to revising
    if meta["status"] not in ("awaiting-feedback", "revising"):
        raise ValueError(
            f"Cannot revise from status '{meta['status']}'. "
            f"Must be 'awaiting-feedback' or 'revising'."
        )

    meta["status"] = "revising"

    # Copy PDFs to next version directory
    current_pdf_dir = review_dir / "assets" / "pdfs" / meta["version"]
    next_pdf_dir = review_dir / "assets" / "pdfs" / next_version
    next_thumb_dir = review_dir / "assets" / "thumbnails" / next_version

    if current_pdf_dir.is_dir():
        next_pdf_dir.mkdir(parents=True, exist_ok=True)
        next_thumb_dir.mkdir(parents=True, exist_ok=True)

        for pdf_file in current_pdf_dir.glob("*.pdf"):
            shutil.copy2(pdf_file, next_pdf_dir / pdf_file.name)

    meta["version"] = next_version
    meta["updated_at"] = _now_iso()
    _save_meta(review_dir, meta)
    return meta


def approve(review_dir: str | Path, approver_name: str | None = None) -> dict:
    """Set the review bundle status to approved with a timestamp.

    Args:
        review_dir: Path to the review bundle.
        approver_name: Name of the person approving. Defaults to 'Client'.
    """
    meta = _load_meta(review_dir)

    if meta["status"] == "approved":
        raise ValueError("Review bundle is already approved.")

    if meta["status"] not in ("awaiting-feedback", "revising"):
        raise ValueError(
            f"Cannot approve from status '{meta['status']}'. "
            f"Must be 'awaiting-feedback' or 'revising'."
        )

    meta["status"] = "approved"
    meta["approved_by"] = approver_name or "Client"
    meta["approved_at"] = _now_iso()
    meta["updated_at"] = _now_iso()
    _save_meta(review_dir, meta)
    return meta
