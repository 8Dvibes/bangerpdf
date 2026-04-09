"""
cmyk — CMYK color management and WeasyPrint PDF variant configuration.

WeasyPrint 67+ added native support for:
- PDF/X variants (pdf/x-1a, pdf/x-3, pdf/x-4, pdf/x-5g) via `pdf_variant`
- PDF/A variants (pdf/a-1b through pdf/a-4f) via `pdf_variant`
- CMYK color() function in CSS (device-cmyk)
- ICC profile embedding via `color_profiles` dict on render()/write_pdf()

What WeasyPrint handles natively (no external tooling needed):
- PDF/X-4 output intent declarations (CGATS TR 001 standard)
- CMYK color values in CSS via color(device-cmyk ...)
- sRGB enforcement via the `srgb` option
- ICC profile embedding for custom color spaces

What requires external tooling (NOT handled here):
- Converting raster images from RGB to CMYK (use Pillow/ImageMagick)
- Soft-proofing / color simulation on screen
- Full preflight validation (use VeraPDF or Callas pdfToolbox)
- GCR/UCR ink optimization

Usage:
    from bangerpdf.cmyk import get_weasyprint_kwargs, resolve_icc_profile
    from bangerpdf.tiers import load_tier

    tier = load_tier("commercial-offset")
    kwargs = get_weasyprint_kwargs(tier)
    # kwargs = {'pdf_variant': 'pdf/x-4', 'presentational_hints': True}
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bangerpdf.tiers import PrintTier


# Directory containing bundled ICC profiles.
_ICC_DIR = Path(__file__).parent / "print_profiles" / "icc"

# Known ICC profiles and their filenames.
_ICC_PROFILES = {
    "sRGB_IEC61966-2-1": "sRGB_IEC61966-2-1.icc",
    "GRACoL2013_CRPC6": "GRACoL2013_CRPC6.icc",
}


def resolve_icc_profile(profile_name: str) -> Path | None:
    """Look up a bundled ICC profile by name.

    Checks the bangerpdf/print_profiles/icc/ directory for the given
    profile. Returns the path if the file exists, None otherwise.

    Args:
        profile_name: The ICC profile identifier (e.g. "GRACoL2013_CRPC6").

    Returns:
        Path to the ICC file if found and exists on disk, None otherwise.
    """
    filename = _ICC_PROFILES.get(profile_name)
    if filename is None:
        # Try as a direct filename (with or without .icc extension).
        candidate = profile_name if profile_name.endswith(".icc") else f"{profile_name}.icc"
        path = _ICC_DIR / candidate
        return path if path.is_file() else None

    path = _ICC_DIR / filename
    return path if path.is_file() else None


def get_weasyprint_kwargs(tier: PrintTier) -> dict:
    """Build the kwargs dict to pass to WeasyPrint's write_pdf() or render().

    Translates a PrintTier's settings into the appropriate WeasyPrint
    options. These kwargs are spread into HTML.write_pdf(**kwargs) or
    Document.write_pdf(**kwargs).

    The returned dict may include:
    - pdf_variant: str — e.g. "pdf/x-4" for commercial offset
    - presentational_hints: bool — enables CSS presentational hints,
      recommended for CMYK workflows to ensure color fidelity
    - srgb: bool — force sRGB color space (for desktop/digital tiers)

    Args:
        tier: A PrintTier instance defining the output requirements.

    Returns:
        Dict of kwargs suitable for WeasyPrint's write_pdf() or render().
    """
    kwargs: dict = {}

    # PDF variant (PDF/X-4 for commercial, PDF/A for archival, etc.)
    if tier.pdf_variant:
        kwargs["pdf_variant"] = tier.pdf_variant

    # Color mode handling.
    if tier.color_mode == "cmyk":
        # Enable presentational hints for better CSS-to-PDF fidelity
        # in CMYK workflows. This ensures CSS attributes like bgcolor
        # are respected in the PDF output.
        kwargs["presentational_hints"] = True
    elif tier.color_mode == "srgb":
        # For sRGB tiers, we can optionally enforce sRGB color space.
        # WeasyPrint's `srgb` option converts all colors to sRGB.
        # We leave this off by default since most content is already sRGB,
        # but the tier system makes it easy to enable if needed.
        pass

    return kwargs
