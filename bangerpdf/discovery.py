"""
Brand discovery: extract brand identity from a website URL.

Supports two backends:
  1. Brand Fetch API (optional, requires BRANDFETCH_API_KEY env var)
  2. Web scrape fallback (stdlib only: urllib.request + html.parser)

Zero new dependencies — everything uses Python stdlib.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class DiscoveredBrand:
    """Brand identity extracted from a website or API."""
    name: str = ""
    colors: dict = field(default_factory=dict)   # {"primary": "#hex", ...}
    fonts: list = field(default_factory=list)
    logo_url: str | None = None
    logo_local: str | None = None
    source_url: str = ""
    method: str = "scrape"  # "brandfetch" | "scrape" | "manual"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def discover_brand(url: str, output_dir: Path | None = None) -> DiscoveredBrand:
    """Auto-discover brand identity. Tries Brand Fetch first, falls back to scrape."""
    # Try Brand Fetch if API key available
    result = _try_brandfetch(url)
    if result:
        if output_dir and result.logo_url:
            local = download_logo(result.logo_url, output_dir)
            if local:
                result.logo_local = str(local)
        return result
    # Fall back to web scrape
    result = _scrape_brand(url)
    if output_dir and result.logo_url:
        local = download_logo(result.logo_url, output_dir)
        if local:
            result.logo_local = str(local)
    return result


def download_logo(logo_url: str, output_dir: Path) -> Path | None:
    """Download a logo image to the output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine filename from URL
    url_path = logo_url.split("?")[0]  # strip query params
    ext = Path(url_path).suffix or ".png"
    if ext not in (".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico"):
        ext = ".png"
    dest = output_dir / f"logo{ext}"

    try:
        req = urllib.request.Request(
            logo_url,
            headers={"User-Agent": _USER_AGENT},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return dest
    except (urllib.error.URLError, OSError, ValueError):
        return None


def brand_to_kit(discovered: DiscoveredBrand) -> dict:
    """Convert DiscoveredBrand to brand-kit.yaml format.

    Maps to the existing BrandKit dataclass structure used by bangerpdf.brand.
    """
    brand_section: dict = {}

    if discovered.name:
        brand_section["name"] = discovered.name

    # Color mapping
    if discovered.colors.get("primary"):
        brand_section["primary"] = discovered.colors["primary"]
    if discovered.colors.get("accent"):
        brand_section["accent"] = discovered.colors["accent"]
    if discovered.colors.get("neutral_dark"):
        brand_section["neutral_dark"] = discovered.colors["neutral_dark"]
    if discovered.colors.get("neutral_light"):
        brand_section["neutral_light"] = discovered.colors["neutral_light"]

    # Font mapping
    if discovered.fonts:
        brand_section["heading_font"] = discovered.fonts[0]
        brand_section["body_font"] = discovered.fonts[1] if len(discovered.fonts) > 1 else discovered.fonts[0]

    # Logo
    if discovered.logo_local:
        brand_section["logo"] = discovered.logo_local
    elif discovered.logo_url:
        brand_section["logo"] = discovered.logo_url

    return {
        "brand": brand_section,
        "print": {
            "default_tier": "desktop",
        },
    }


# ---------------------------------------------------------------------------
# Brand Fetch API (optional)
# ---------------------------------------------------------------------------

def _try_brandfetch(url: str) -> DiscoveredBrand | None:
    """Optional Brand Fetch API. Returns None if key unavailable."""
    api_key = os.environ.get("BRANDFETCH_API_KEY")
    if not api_key:
        return None

    # Extract domain from URL
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]

    try:
        req = urllib.request.Request(
            f"https://api.brandfetch.io/v2/brands/{domain}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        brand = DiscoveredBrand(source_url=url, method="brandfetch")
        brand.name = data.get("name", domain)

        # Extract colors
        for c in data.get("colors", []):
            color_type = c.get("type", "")
            hex_val = c.get("hex", "")
            if not hex_val:
                continue
            if color_type == "accent":
                brand.colors["primary"] = hex_val
            elif color_type == "brand":
                brand.colors.setdefault("primary", hex_val)
            elif color_type == "dark":
                brand.colors["neutral_dark"] = hex_val
            elif color_type == "light":
                brand.colors["neutral_light"] = hex_val

        # Extract fonts
        for f in data.get("fonts", []):
            if f.get("name"):
                brand.fonts.append(f["name"])

        # Extract logo
        for logo in data.get("logos", []):
            if logo.get("type") == "logo":
                for fmt in logo.get("formats", []):
                    if fmt.get("format") in ("svg", "png"):
                        brand.logo_url = fmt.get("src")
                        break
                if brand.logo_url:
                    break

        return brand

    except (urllib.error.URLError, json.JSONDecodeError, KeyError, OSError):
        return None


# ---------------------------------------------------------------------------
# Web scrape fallback (stdlib only)
# ---------------------------------------------------------------------------

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# CSS custom property patterns commonly used for brand colors
_CSS_COLOR_VAR_PATTERNS = [
    re.compile(r"--(?:primary|brand|main|theme)[-_]?color\s*:\s*(#[0-9a-fA-F]{3,8})", re.IGNORECASE),
    re.compile(r"--(?:accent|secondary|highlight)[-_]?color\s*:\s*(#[0-9a-fA-F]{3,8})", re.IGNORECASE),
    re.compile(r"--(?:dark|neutral[-_]dark|text)[-_]?color\s*:\s*(#[0-9a-fA-F]{3,8})", re.IGNORECASE),
    re.compile(r"--(?:light|neutral[-_]light|bg|background)[-_]?color\s*:\s*(#[0-9a-fA-F]{3,8})", re.IGNORECASE),
]

# Font-family extraction from CSS
_FONT_FAMILY_RE = re.compile(
    r"font-family\s*:\s*([^;}{]+)",
    re.IGNORECASE,
)

# Hex color in any CSS context
_HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{6})\b")


class _BrandHTMLParser(HTMLParser):
    """Extract brand signals from HTML: meta tags, link tags, and style blocks."""

    def __init__(self) -> None:
        super().__init__()
        self.theme_color: str | None = None
        self.og_image: str | None = None
        self.favicon: str | None = None
        self.apple_touch_icon: str | None = None
        self.title: str | None = None
        self.style_blocks: list[str] = []
        self._in_style = False
        self._in_title = False
        self._title_parts: list[str] = []
        self._current_data: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k.lower(): v for k, v in attrs if v is not None}

        if tag == "meta":
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            content = attr_dict.get("content", "")

            if name == "theme-color" and content:
                self.theme_color = content
            elif prop == "og:image" and content:
                self.og_image = content
            elif name == "msapplication-tilecolor" and content:
                # Fallback brand color
                if not self.theme_color:
                    self.theme_color = content

        elif tag == "link":
            rel = attr_dict.get("rel", "").lower()
            href = attr_dict.get("href", "")

            if "apple-touch-icon" in rel and href:
                self.apple_touch_icon = href
            elif "icon" in rel and href and not self.favicon:
                self.favicon = href

        elif tag == "style":
            self._in_style = True
            self._current_data = []

        elif tag == "title":
            self._in_title = True
            self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self._current_data.append(data)
        if self._in_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "style" and self._in_style:
            self._in_style = False
            self.style_blocks.append("".join(self._current_data))
            self._current_data = []
        elif tag == "title" and self._in_title:
            self._in_title = False
            self.title = "".join(self._title_parts).strip()


def _resolve_url(base_url: str, href: str) -> str:
    """Resolve a potentially relative URL against a base URL."""
    if href.startswith(("http://", "https://", "//")):
        if href.startswith("//"):
            return "https:" + href
        return href

    # Handle absolute path
    if href.startswith("/"):
        # Extract scheme + host from base
        parts = base_url.split("/")
        if len(parts) >= 3:
            return "/".join(parts[:3]) + href
        return href

    # Relative path
    if "/" in base_url:
        return base_url.rsplit("/", 1)[0] + "/" + href
    return href


def _extract_fonts_from_css(css_text: str) -> list[str]:
    """Extract unique font family names from CSS text."""
    fonts: list[str] = []
    seen: set[str] = set()

    for match in _FONT_FAMILY_RE.finditer(css_text):
        raw = match.group(1).strip()
        # Parse the font stack (comma-separated, possibly quoted)
        for part in raw.split(","):
            name = part.strip().strip("'\"").strip()
            # Skip generic families
            if name.lower() in (
                "serif", "sans-serif", "monospace", "cursive", "fantasy",
                "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace",
                "inherit", "initial", "unset",
            ):
                continue
            if name and name.lower() not in seen:
                seen.add(name.lower())
                fonts.append(name)

    return fonts


def _extract_colors_from_css(css_text: str) -> dict[str, str]:
    """Extract brand colors from CSS custom properties and common hex values."""
    colors: dict[str, str] = {}

    # First try named CSS custom properties
    patterns_map = [
        ("primary", _CSS_COLOR_VAR_PATTERNS[0]),
        ("accent", _CSS_COLOR_VAR_PATTERNS[1]),
        ("neutral_dark", _CSS_COLOR_VAR_PATTERNS[2]),
        ("neutral_light", _CSS_COLOR_VAR_PATTERNS[3]),
    ]
    for key, pattern in patterns_map:
        match = pattern.search(css_text)
        if match:
            colors[key] = match.group(1)

    # If we didn't find a primary, collect hex colors and pick the most frequent
    if "primary" not in colors:
        hex_counts: dict[str, int] = {}
        for match in _HEX_COLOR_RE.finditer(css_text):
            hex_val = "#" + match.group(1).upper()
            # Skip near-black, near-white, and grays
            r, g, b = int(hex_val[1:3], 16), int(hex_val[3:5], 16), int(hex_val[5:7], 16)
            if r == g == b:
                continue  # pure gray
            if r < 20 and g < 20 and b < 20:
                continue  # near-black
            if r > 235 and g > 235 and b > 235:
                continue  # near-white
            hex_counts[hex_val] = hex_counts.get(hex_val, 0) + 1

        if hex_counts:
            # Most frequent non-gray color is likely the brand color
            most_common = max(hex_counts, key=hex_counts.get)  # type: ignore[arg-type]
            colors["primary"] = most_common

    return colors


def _scrape_brand(url: str) -> DiscoveredBrand:
    """Fallback: scrape website for brand signals.

    Extracts:
      - Meta tags: theme-color, og:image, msapplication-tilecolor
      - Link tags: favicon, apple-touch-icon
      - Style blocks: CSS custom properties for colors, font-family declarations
      - Title tag: site name
    """
    brand = DiscoveredBrand(source_url=url, method="scrape")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            # Read up to 512 KB (we only need the <head> and early <body>)
            html = resp.read(512 * 1024).decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, ValueError):
        return brand

    # Parse HTML
    parser = _BrandHTMLParser()
    try:
        parser.feed(html)
    except Exception:
        pass  # HTMLParser is lenient but can still choke on extreme markup

    # Extract name from title or domain
    if parser.title:
        # Strip common suffixes like " | Company" or " - Company"
        name = re.split(r"\s*[|–—-]\s*", parser.title)[0].strip()
        brand.name = name if name else parser.title
    else:
        # Fall back to domain
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        brand.name = domain.split(".")[0].title()

    # Extract colors from theme-color meta tag
    if parser.theme_color:
        color = parser.theme_color.strip()
        if color.startswith("#"):
            brand.colors["primary"] = color

    # Extract colors and fonts from style blocks
    all_css = "\n".join(parser.style_blocks)

    # Also try to extract inline style attributes from the raw HTML
    inline_styles = re.findall(r'style="([^"]*)"', html)
    all_css += "\n" + "\n".join(inline_styles)

    css_colors = _extract_colors_from_css(all_css)
    for key, val in css_colors.items():
        brand.colors.setdefault(key, val)

    css_fonts = _extract_fonts_from_css(all_css)
    brand.fonts = css_fonts

    # Logo: prefer apple-touch-icon > og:image > favicon
    logo_candidates = [
        parser.apple_touch_icon,
        parser.og_image,
        parser.favicon,
    ]
    for candidate in logo_candidates:
        if candidate:
            brand.logo_url = _resolve_url(url, candidate)
            break

    return brand
