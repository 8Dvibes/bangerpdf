"""
tiers — Three-tier print pipeline definitions and application.

bangerpdf supports three print tiers:
- **desktop**: Screen viewing / home printer. No bleed, no crop marks, sRGB.
- **digital-press**: Professional digital printers (Indigo, iGen, etc.).
  Adds 1/8" bleed and crop marks, still sRGB.
- **commercial-offset**: Offset lithography. Bleed + crop marks + CMYK
  color mode + PDF/X-4 output intent.

Tiers are defined as YAML configs in bangerpdf/print_profiles/ and loaded
at runtime. The apply_tier() function modifies HTML/CSS and returns
WeasyPrint kwargs so the render pipeline can produce tier-appropriate PDFs.

Usage:
    from bangerpdf.tiers import load_tier, list_tiers, apply_tier

    tier = load_tier("digital-press")
    html, wp_kwargs = apply_tier(tier, html_str, css_str)
    # Then pass wp_kwargs to WeasyPrint's write_pdf()
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import yaml

from bangerpdf.cmyk import get_weasyprint_kwargs
from bangerpdf.crop_marks import inject_crop_marks


@dataclass
class PrintTier:
    """A print output tier defining bleed, marks, color, and PDF settings."""
    name: str               # "desktop" | "digital-press" | "commercial-offset"
    bleed_in: float         # 0 for desktop, 0.125 otherwise
    crop_marks: bool        # False for desktop
    color_mode: str         # "srgb" | "cmyk"
    icc_profile: str | None  # None for desktop, profile name for commercial
    pdf_variant: str | None  # None | "pdf/x-4" | "pdf/a-2b"


def _profiles_dir() -> Path:
    """Return the path to the print_profiles package directory.

    Uses importlib.resources for robust path resolution whether bangerpdf
    is installed as a package, run from source, or used in editable mode.
    """
    # For Python 3.10+ we can use importlib.resources.files()
    ref = resources.files("bangerpdf.print_profiles")
    # Materialize to a real path (works for both installed and editable).
    return Path(str(ref))


def load_tier(name: str) -> PrintTier:
    """Load a print tier definition from its YAML config.

    Args:
        name: The tier name (e.g. "desktop", "digital-press", "commercial-offset").
              Must match a YAML filename in bangerpdf/print_profiles/.

    Returns:
        A PrintTier instance.

    Raises:
        FileNotFoundError: If no YAML config exists for the given tier name.
        ValueError: If the YAML config is missing required fields.
    """
    profiles_dir = _profiles_dir()
    yaml_path = profiles_dir / f"{name}.yaml"

    if not yaml_path.is_file():
        available = [p.stem for p in profiles_dir.glob("*.yaml")]
        raise FileNotFoundError(
            f"No print tier '{name}' found. "
            f"Available tiers: {', '.join(sorted(available))}"
        )

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    required_fields = {"name", "bleed_in", "crop_marks", "color_mode"}
    missing = required_fields - set(data.keys())
    if missing:
        raise ValueError(
            f"Tier config '{name}.yaml' is missing required fields: "
            f"{', '.join(sorted(missing))}"
        )

    return PrintTier(
        name=data["name"],
        bleed_in=float(data["bleed_in"]),
        crop_marks=bool(data["crop_marks"]),
        color_mode=data["color_mode"],
        icc_profile=data.get("icc_profile"),
        pdf_variant=data.get("pdf_variant"),
    )


def list_tiers() -> list[PrintTier]:
    """List all available print tiers.

    Scans the bangerpdf/print_profiles/ directory for YAML configs and
    returns a PrintTier for each one, sorted by name.

    Returns:
        List of PrintTier instances, sorted alphabetically by name.
    """
    profiles_dir = _profiles_dir()
    tiers = []
    for yaml_path in sorted(profiles_dir.glob("*.yaml")):
        try:
            tiers.append(load_tier(yaml_path.stem))
        except (ValueError, FileNotFoundError):
            # Skip malformed configs rather than failing the entire listing.
            continue
    return tiers


def apply_tier(tier: PrintTier, html: str, css: str) -> tuple[str, dict]:
    """Apply a print tier's settings to HTML and CSS.

    Modifies the CSS to include crop marks / bleed if the tier requires it,
    and returns WeasyPrint kwargs for color mode and PDF variant settings.

    For desktop tier: no modifications, empty kwargs.
    For digital-press: injects `marks: crop cross` + `bleed: 0.125in` into
        @page CSS rules.
    For commercial-offset: same CSS injection as digital-press, plus
        WeasyPrint kwargs for CMYK / PDF/X-4 output.

    Args:
        tier: The PrintTier to apply.
        html: The HTML content (returned unmodified for now; future phases
              may inject tier-specific markup).
        css: The CSS content to modify.

    Returns:
        A tuple of (modified_html, weasyprint_kwargs) where:
        - modified_html is the (possibly unchanged) HTML string
        - weasyprint_kwargs is a dict to spread into write_pdf()
    """
    modified_html = html
    modified_css = css

    # Inject crop marks and bleed into CSS if the tier requires them.
    if tier.crop_marks and tier.bleed_in > 0:
        modified_css = inject_crop_marks(modified_css, tier.bleed_in)

    # Build WeasyPrint kwargs for color mode and PDF variant.
    wp_kwargs = get_weasyprint_kwargs(tier)

    # If CSS was modified, the caller needs to know. We return the modified
    # CSS bundled back into the HTML via a <style> injection. However, to
    # keep this function composable (the caller may handle CSS separately),
    # we embed the modified CSS only if the input CSS differs from the output.
    if modified_css != css:
        # Inject the modified CSS into the HTML. The render pipeline
        # can use this directly with WeasyPrint.
        style_block = f"\n<style>\n{modified_css}\n</style>\n"
        if "</head>" in modified_html:
            modified_html = modified_html.replace(
                "</head>", f"{style_block}</head>", 1
            )
        else:
            modified_html = style_block + modified_html

    return modified_html, wp_kwargs
