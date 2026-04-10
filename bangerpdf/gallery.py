"""
Gallery and pattern management for bundled reference assets.

Patterns: reusable HTML+CSS layout snippets (bangerpdf/patterns/)
Gallery: full reference packs by vibe (bangerpdf/gallery/)
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path


# ---------------------------------------------------------------------------
# Patterns (bundled HTML+CSS layout snippets)
# ---------------------------------------------------------------------------

def _patterns_dir() -> Path | None:
    """Locate the patterns directory using importlib.resources."""
    try:
        # Python 3.12+ files() API
        ref = importlib.resources.files("bangerpdf") / "patterns"
        # Convert to a path if possible (only works for on-disk packages)
        path = Path(str(ref))
        if path.is_dir():
            return path
    except (TypeError, FileNotFoundError, ModuleNotFoundError):
        pass

    # Fallback: look relative to this file
    fallback = Path(__file__).parent / "patterns"
    if fallback.is_dir():
        return fallback

    return None


def list_patterns() -> list[dict]:
    """List available layout patterns from bangerpdf/patterns/.

    Returns a list of dicts with keys: name, filename, path, description.
    """
    patterns_dir = _patterns_dir()
    if not patterns_dir:
        return []

    patterns = []
    for html_file in sorted(patterns_dir.glob("*.html")):
        # Read the first line for a comment-based description
        description = ""
        try:
            first_lines = html_file.read_text(encoding="utf-8")[:500]
            # Look for <!-- description --> comment
            if "<!--" in first_lines:
                start = first_lines.index("<!--") + 4
                end = first_lines.index("-->", start) if "-->" in first_lines[start:] else -1
                if end > 0:
                    description = first_lines[start:end].strip()
        except (OSError, ValueError):
            pass

        patterns.append({
            "name": html_file.stem,
            "filename": html_file.name,
            "path": str(html_file),
            "description": description,
        })

    return patterns


def show_pattern(name: str) -> str:
    """Return HTML+CSS source for a named pattern.

    Raises FileNotFoundError if the pattern doesn't exist.
    """
    patterns_dir = _patterns_dir()
    if not patterns_dir:
        raise FileNotFoundError("Patterns directory not found.")

    # Try exact match first, then with .html extension
    candidates = [
        patterns_dir / name,
        patterns_dir / f"{name}.html",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")

    available = [p.stem for p in patterns_dir.glob("*.html")]
    raise FileNotFoundError(
        f"Pattern '{name}' not found. Available: {', '.join(available) or 'none'}"
    )


# ---------------------------------------------------------------------------
# Gallery (full reference packs by vibe)
# ---------------------------------------------------------------------------

def _gallery_dir() -> Path | None:
    """Locate the gallery directory using importlib.resources."""
    try:
        ref = importlib.resources.files("bangerpdf") / "gallery"
        path = Path(str(ref))
        if path.is_dir():
            return path
    except (TypeError, FileNotFoundError, ModuleNotFoundError):
        pass

    fallback = Path(__file__).parent / "gallery"
    if fallback.is_dir():
        return fallback

    return None


def list_gallery(vibe: str | None = None) -> list[dict]:
    """List reference packs, optionally filtered by vibe.

    Returns a list of dicts with keys: name, path, has_notes, has_brand_kit, vibe.
    """
    gallery_dir = _gallery_dir()
    if not gallery_dir:
        return []

    entries = []
    for entry in sorted(gallery_dir.iterdir()):
        if not entry.is_dir():
            continue

        # Determine vibe from directory name or notes.md
        entry_vibe = entry.name  # convention: directory name IS the vibe

        if vibe and entry_vibe.lower() != vibe.lower():
            continue

        entries.append({
            "name": entry.name,
            "path": str(entry),
            "has_notes": (entry / "notes.md").exists(),
            "has_brand_kit": (entry / "brand-kit.yaml").exists(),
            "vibe": entry_vibe,
        })

    return entries


def show_gallery_notes(name: str) -> str:
    """Return annotation notes for a gallery entry.

    Raises FileNotFoundError if the entry or notes don't exist.
    """
    gallery_dir = _gallery_dir()
    if not gallery_dir:
        raise FileNotFoundError("Gallery directory not found.")

    notes_path = gallery_dir / name / "notes.md"
    if not notes_path.is_file():
        available = [e.name for e in gallery_dir.iterdir() if e.is_dir()]
        raise FileNotFoundError(
            f"No notes found for gallery entry '{name}'. "
            f"Available entries: {', '.join(available) or 'none'}"
        )

    return notes_path.read_text(encoding="utf-8")
