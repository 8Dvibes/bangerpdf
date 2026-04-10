"""
Global preferences and brand profile management.

Config dir: ~/.config/bangerpdf/
Brand profiles: ~/.config/bangerpdf/brands/<name>/
Global preferences: ~/.config/bangerpdf/preferences.yaml
"""

from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import yaml


CONFIG_DIR = Path.home() / ".config" / "bangerpdf"
BRANDS_DIR = CONFIG_DIR / "brands"
PREFS_FILE = CONFIG_DIR / "preferences.yaml"


@dataclass
class GlobalPreferences:
    """User-wide defaults for bangerpdf."""
    default_vibe: str = "corporate"
    default_tier: str = "desktop"
    default_font_heading: str = "Inter"
    default_font_body: str = "Inter"
    default_accent: str = "#2563EB"
    auto_interview: bool = True
    auto_visual_generation: bool = True
    always_full_bleed_covers: bool = False
    footer_position: str = "bottom"


# ---------------------------------------------------------------------------
# Preferences CRUD
# ---------------------------------------------------------------------------

def load_preferences() -> GlobalPreferences:
    """Load preferences from disk, returning defaults if the file is missing."""
    if not PREFS_FILE.exists():
        return GlobalPreferences()

    try:
        with open(PREFS_FILE) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return GlobalPreferences()

        # Only use keys that are valid fields
        valid_keys = {fld.name for fld in fields(GlobalPreferences)}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return GlobalPreferences(**filtered)
    except (yaml.YAMLError, TypeError, OSError):
        return GlobalPreferences()


def save_preferences(prefs: GlobalPreferences) -> None:
    """Persist preferences to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PREFS_FILE, "w") as f:
        yaml.dump(asdict(prefs), f, default_flow_style=False, sort_keys=False)


def set_preference(key: str, value: str) -> GlobalPreferences:
    """Set a single preference key and persist.

    Handles type coercion for boolean fields.
    """
    prefs = load_preferences()

    valid_keys = {fld.name for fld in fields(GlobalPreferences)}
    if key not in valid_keys:
        raise ValueError(
            f"Unknown preference key '{key}'. "
            f"Valid keys: {', '.join(sorted(valid_keys))}"
        )

    # Type coercion based on field type
    field_type = {fld.name: fld.type for fld in fields(GlobalPreferences)}[key]
    if field_type == "bool":
        coerced: str | bool = value.lower() in ("true", "1", "yes", "on")
    else:
        coerced = value

    setattr(prefs, key, coerced)
    save_preferences(prefs)
    return prefs


# ---------------------------------------------------------------------------
# Brand profiles
# ---------------------------------------------------------------------------

def save_brand(name: str, project_dir: Path) -> Path:
    """Save a brand profile from a project directory.

    Copies brand-kit.yaml, design-brief.yaml (if exists), and assets/
    from the project directory to ~/.config/bangerpdf/brands/<name>/.

    Returns the path to the saved brand profile directory.
    """
    project_dir = Path(project_dir).resolve()
    brand_dir = BRANDS_DIR / name
    brand_dir.mkdir(parents=True, exist_ok=True)

    # Copy brand-kit.yaml (required)
    brand_kit = project_dir / "brand-kit.yaml"
    if not brand_kit.exists():
        raise FileNotFoundError(
            f"No brand-kit.yaml found in {project_dir}. "
            f"Cannot save brand profile."
        )
    shutil.copy2(brand_kit, brand_dir / "brand-kit.yaml")

    # Copy design-brief.yaml (optional)
    design_brief = project_dir / "design-brief.yaml"
    if design_brief.exists():
        shutil.copy2(design_brief, brand_dir / "design-brief.yaml")

    # Copy assets/ directory (optional)
    assets_dir = project_dir / "assets"
    if assets_dir.is_dir():
        dest_assets = brand_dir / "assets"
        if dest_assets.exists():
            shutil.rmtree(dest_assets)
        shutil.copytree(assets_dir, dest_assets)

    return brand_dir


def load_brand_profile(name: str) -> dict | None:
    """Load a saved brand profile by name.

    Returns the parsed brand-kit.yaml as a dict, or None if not found.
    """
    brand_dir = BRANDS_DIR / name
    brand_kit = brand_dir / "brand-kit.yaml"

    if not brand_kit.exists():
        return None

    try:
        with open(brand_kit) as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except (yaml.YAMLError, OSError):
        return None


def list_brands() -> list[dict]:
    """List all saved brand profiles.

    Returns a list of dicts with keys: name, path, has_brief, has_assets.
    """
    if not BRANDS_DIR.is_dir():
        return []

    brands = []
    for entry in sorted(BRANDS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if not (entry / "brand-kit.yaml").exists():
            continue

        brands.append({
            "name": entry.name,
            "path": str(entry),
            "has_brief": (entry / "design-brief.yaml").exists(),
            "has_assets": (entry / "assets").is_dir(),
        })

    return brands


def delete_brand(name: str) -> bool:
    """Delete a saved brand profile. Returns True if deleted, False if not found."""
    brand_dir = BRANDS_DIR / name
    if not brand_dir.is_dir():
        return False
    shutil.rmtree(brand_dir)
    return True
