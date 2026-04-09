"""
brand — Brand kit loader and CSS variable generator.

Reads brand-kit.yaml files and produces CSS custom properties that templates
can reference. Supports a merge order: pack default -> project root -> CLI
overrides so that every project can inherit a starter brand and then customize.

Usage:
    from bangerpdf.brand import load_brand, to_css_vars
    brand = load_brand("/path/to/project")
    css_block = to_css_vars(brand)
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PrintConfig:
    """Print-related settings from brand-kit.yaml."""
    default_tier: str = "desktop"
    bleed_in: float = 0.0
    crop_marks: bool = False


@dataclass
class BrandKit:
    """Immutable representation of a brand-kit.yaml file."""
    name: str = "Untitled"
    primary: str = "#2B5EA7"
    accent: str = "#F5A623"
    neutral_dark: str = "#1A1A1A"
    neutral_light: str = "#F7F7F7"
    body_font: str = "Inter"
    heading_font: str = "Inter"
    logo: str = ""
    footer_html: str = ""
    print_config: PrintConfig = field(default_factory=PrintConfig)

    def as_dict(self) -> dict[str, Any]:
        """Return a flat dict suitable for display or serialization."""
        return {
            "brand.name": self.name,
            "brand.primary": self.primary,
            "brand.accent": self.accent,
            "brand.neutral_dark": self.neutral_dark,
            "brand.neutral_light": self.neutral_light,
            "brand.body_font": self.body_font,
            "brand.heading_font": self.heading_font,
            "brand.logo": self.logo,
            "brand.footer_html": self.footer_html,
            "print.default_tier": self.print_config.default_tier,
            "print.bleed_in": self.print_config.bleed_in,
            "print.crop_marks": self.print_config.crop_marks,
        }


def _parse_brand_yaml(data: dict) -> BrandKit:
    """Parse a raw YAML dict into a BrandKit dataclass."""
    brand_section = data.get("brand", {})
    print_section = data.get("print", {})

    pc = PrintConfig(
        default_tier=print_section.get("default_tier", "desktop"),
        bleed_in=float(print_section.get("bleed_in", 0.0)),
        crop_marks=bool(print_section.get("crop_marks", False)),
    )

    return BrandKit(
        name=brand_section.get("name", "Untitled"),
        primary=brand_section.get("primary", "#2B5EA7"),
        accent=brand_section.get("accent", "#F5A623"),
        neutral_dark=brand_section.get("neutral_dark", "#1A1A1A"),
        neutral_light=brand_section.get("neutral_light", "#F7F7F7"),
        body_font=brand_section.get("body_font", "Inter"),
        heading_font=brand_section.get("heading_font", "Inter"),
        logo=brand_section.get("logo", ""),
        footer_html=brand_section.get("footer_html", ""),
        print_config=pc,
    )


def _merge_brand(base: BrandKit, overlay: dict) -> BrandKit:
    """Merge an overlay dict (raw YAML) on top of a base BrandKit.

    Only keys present in the overlay are updated; everything else is kept
    from base.
    """
    brand_section = overlay.get("brand", {})
    print_section = overlay.get("print", {})

    return BrandKit(
        name=brand_section.get("name", base.name),
        primary=brand_section.get("primary", base.primary),
        accent=brand_section.get("accent", base.accent),
        neutral_dark=brand_section.get("neutral_dark", base.neutral_dark),
        neutral_light=brand_section.get("neutral_light", base.neutral_light),
        body_font=brand_section.get("body_font", base.body_font),
        heading_font=brand_section.get("heading_font", base.heading_font),
        logo=brand_section.get("logo", base.logo),
        footer_html=brand_section.get("footer_html", base.footer_html),
        print_config=PrintConfig(
            default_tier=print_section.get("default_tier", base.print_config.default_tier),
            bleed_in=float(print_section.get("bleed_in", base.print_config.bleed_in)),
            crop_marks=bool(print_section.get("crop_marks", base.print_config.crop_marks)),
        ),
    )


def _read_yaml(path: Path) -> dict:
    """Read a YAML file, returning an empty dict on failure."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"  WARNING: Could not read {path}: {e}", file=sys.stderr)
        return {}


def load_brand(project_dir: str | Path, pack_dir: str | Path | None = None) -> BrandKit:
    """Load and merge brand kits in order: pack default -> project root -> CLI overrides.

    Args:
        project_dir: The project directory (where the user runs bangerpdf build).
        pack_dir: Optional path to a starter pack directory that may contain
                  its own brand-kit.yaml as the base layer.

    Returns:
        A fully merged BrandKit.
    """
    project_dir = Path(project_dir)

    # Layer 1: pack default (if present)
    base = BrandKit()
    if pack_dir:
        pack_brand_path = Path(pack_dir) / "brand-kit.yaml"
        if pack_brand_path.exists():
            base = _parse_brand_yaml(_read_yaml(pack_brand_path))

    # Layer 2: project root brand-kit.yaml
    project_brand_path = project_dir / "brand-kit.yaml"
    if project_brand_path.exists():
        overlay = _read_yaml(project_brand_path)
        base = _merge_brand(base, overlay)

    return base


def to_css_vars(brand: BrandKit) -> str:
    """Generate a :root CSS block from a BrandKit.

    Templates reference these as var(--primary), var(--accent), etc.
    """
    return (
        ":root {\n"
        f'  --primary: {brand.primary};\n'
        f'  --accent: {brand.accent};\n'
        f'  --neutral-dark: {brand.neutral_dark};\n'
        f'  --neutral-light: {brand.neutral_light};\n'
        f'  --body-font: {brand.body_font};\n'
        f'  --heading-font: {brand.heading_font};\n'
        f'  --brand-name: "{brand.name}";\n'
        "}\n"
    )


def brand_to_yaml(brand: BrandKit) -> str:
    """Serialize a BrandKit back to YAML string."""
    data = {
        "brand": {
            "name": brand.name,
            "primary": brand.primary,
            "accent": brand.accent,
            "neutral_dark": brand.neutral_dark,
            "neutral_light": brand.neutral_light,
            "body_font": brand.body_font,
            "heading_font": brand.heading_font,
            "logo": brand.logo,
            "footer_html": brand.footer_html,
        },
        "print": {
            "default_tier": brand.print_config.default_tier,
            "bleed_in": brand.print_config.bleed_in,
            "crop_marks": brand.print_config.crop_marks,
        },
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def update_brand_yaml(path: Path, key: str, value: str) -> None:
    """Update a single key in a brand-kit.yaml file.

    Key format: "brand.primary" or "print.default_tier" (dot-separated section.field).
    """
    data = _read_yaml(path)

    # Parse the dotted key
    parts = key.split(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Key must be 'section.field' (e.g. 'brand.primary'), got: {key}")

    section, field_name = parts

    if section not in ("brand", "print"):
        raise ValueError(f"Unknown section '{section}'. Use 'brand' or 'print'.")

    if section not in data:
        data[section] = {}

    # Type coercion for known fields
    if field_name == "bleed_in":
        value = float(value)  # type: ignore[assignment]
    elif field_name == "crop_marks":
        value = value.lower() in ("true", "1", "yes")  # type: ignore[assignment]

    data[section][field_name] = value

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
