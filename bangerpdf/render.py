"""
render — Render pack engine (generalized from Fishback build.py).

Loads a pack directory (pack.yaml + data.json + templates/ + brand-kit.yaml),
renders Jinja2 templates with data context, injects brand CSS variables,
and converts the resulting HTML to PDF via bangerpdf.convert.

Usage:
    from bangerpdf.render import build_pack
    result = build_pack("/path/to/my-bid")
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from bangerpdf.brand import BrandKit, load_brand, to_css_vars


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class DocSpec:
    """One document entry from pack.yaml."""
    name: str
    template: str
    expected_pages: int | None = None


@dataclass
class PackContext:
    """Everything needed to render a pack."""
    pack_dir: Path
    name: str
    description: str
    version: str
    documents: list[DocSpec]
    default_tier: str
    data: dict[str, Any]
    brand: BrandKit
    base_css: str  # contents of styles.css if present, else empty


@dataclass
class DocResult:
    """Result of rendering one document."""
    name: str
    html_path: Path
    pdf_path: Path
    page_count: int
    size_bytes: int


@dataclass
class BuildResult:
    """Top-level result of building a pack."""
    pack_dir: Path
    tier: str
    docs: list[DocResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def pdf_count(self) -> int:
        return len(self.docs)


# ---------------------------------------------------------------------------
# Custom Jinja2 filters
# ---------------------------------------------------------------------------

def _filter_money(value: Any) -> str:
    """Format a number as $X,XXX (no cents)."""
    try:
        n = int(float(value))
        return f"${n:,}"
    except (ValueError, TypeError):
        return str(value)


def _filter_usd(value: Any) -> str:
    """Format a number as $X,XXX.XX (with cents)."""
    try:
        n = float(value)
        return f"${n:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def _filter_phone(value: str) -> str:
    """Format a phone number. Passes through if already formatted."""
    digits = re.sub(r'\D', '', str(value))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return str(value)


def _filter_date_iso(value: str) -> str:
    """Pass through a date string (templates handle their own formatting)."""
    return str(value)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_pack(pack_dir: str | Path) -> PackContext:
    """Load a pack directory into a PackContext.

    Expects the directory to contain at minimum:
        pack.yaml       - manifest with documents list
        data.json       - template data
        brand-kit.yaml  - brand settings (optional, defaults used if missing)

    Optionally:
        styles.css      - base stylesheet
        templates/      - Jinja2 HTML templates
    """
    pack_dir = Path(pack_dir).resolve()

    # pack.yaml (required)
    pack_yaml_path = pack_dir / "pack.yaml"
    if not pack_yaml_path.exists():
        raise FileNotFoundError(f"No pack.yaml found in {pack_dir}")

    with open(pack_yaml_path) as f:
        pack_manifest = yaml.safe_load(f)

    if not isinstance(pack_manifest, dict):
        raise ValueError(f"pack.yaml must be a YAML mapping, got {type(pack_manifest).__name__}")

    # data.json (required)
    data_json_path = pack_dir / "data.json"
    if not data_json_path.exists():
        raise FileNotFoundError(f"No data.json found in {pack_dir}")

    with open(data_json_path) as f:
        data = json.load(f)

    # brand-kit.yaml (optional, uses defaults if missing)
    brand = load_brand(pack_dir)

    # styles.css (optional)
    styles_path = pack_dir / "styles.css"
    base_css = styles_path.read_text() if styles_path.exists() else ""

    # Parse document specs
    documents = []
    for doc_entry in pack_manifest.get("documents", []):
        documents.append(DocSpec(
            name=doc_entry["name"],
            template=doc_entry["template"],
            expected_pages=doc_entry.get("expected_pages"),
        ))

    return PackContext(
        pack_dir=pack_dir,
        name=pack_manifest.get("name", pack_dir.name),
        description=pack_manifest.get("description", ""),
        version=pack_manifest.get("version", "0.0"),
        documents=documents,
        default_tier=pack_manifest.get("default_tier", "desktop"),
        data=data,
        brand=brand,
        base_css=base_css,
    )


def build_env(pack: PackContext) -> Environment:
    """Create a Jinja2 Environment configured for the pack.

    Template search path includes:
        1. templates/ under the pack dir
        2. The pack dir itself (for templates referenced without templates/ prefix)
    """
    search_paths = []

    templates_dir = pack.pack_dir / "templates"
    if templates_dir.is_dir():
        search_paths.append(str(templates_dir))

    # Also allow templates that reference the pack root directly
    search_paths.append(str(pack.pack_dir))

    env = Environment(
        loader=FileSystemLoader(search_paths),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )

    # Register custom filters
    env.filters["money"] = _filter_money
    env.filters["usd"] = _filter_usd
    env.filters["phone"] = _filter_phone
    env.filters["date_iso"] = _filter_date_iso

    return env


def inject_brand_css(base_css: str, brand: BrandKit) -> str:
    """Prepend :root CSS variables from the brand kit to the base CSS."""
    css_vars = to_css_vars(brand)
    if base_css:
        return css_vars + "\n" + base_css
    return css_vars


def render_document(
    pack: PackContext,
    doc_spec: DocSpec,
    env: Environment,
    tier: str = "desktop",
) -> DocResult:
    """Render a single document: template -> HTML -> PDF.

    Writes intermediate HTML to rendered/{tier}/ and final PDF to pdfs/{tier}/.
    """
    import weasyprint

    # Prepare output dirs
    html_out_dir = pack.pack_dir / "rendered" / tier
    pdf_out_dir = pack.pack_dir / "pdfs" / tier
    html_out_dir.mkdir(parents=True, exist_ok=True)
    pdf_out_dir.mkdir(parents=True, exist_ok=True)

    # Render template with data context
    template_path = doc_spec.template
    # Strip leading "templates/" prefix if present since the loader already
    # has templates/ on its search path
    if template_path.startswith("templates/"):
        template_path = template_path[len("templates/"):]

    template = env.get_template(template_path)
    html_str = template.render(**pack.data)

    # Write intermediate HTML for debugging
    html_filename = f"{doc_spec.name}.html"
    html_out = html_out_dir / html_filename
    html_out.write_text(html_str)

    # Build combined CSS: brand vars + base styles
    combined_css = inject_brand_css(pack.base_css, pack.brand)

    # Convert to PDF using WeasyPrint directly (gives us page count)
    pdf_filename = f"{doc_spec.name}.pdf"
    pdf_out = pdf_out_dir / pdf_filename

    html_doc = weasyprint.HTML(
        string=html_str,
        base_url=str(pack.pack_dir),
    )

    # Apply combined CSS as an additional stylesheet
    stylesheets = []
    if combined_css.strip():
        stylesheets.append(weasyprint.CSS(string=combined_css))

    document = html_doc.render(stylesheets=stylesheets)
    page_count = len(document.pages)
    document.write_pdf(str(pdf_out))

    size_bytes = pdf_out.stat().st_size

    return DocResult(
        name=doc_spec.name,
        html_path=html_out,
        pdf_path=pdf_out,
        page_count=page_count,
        size_bytes=size_bytes,
    )


def build_pack(
    pack_dir: str | Path,
    tiers: list[str] | None = None,
    only: str | None = None,
) -> BuildResult:
    """Build all documents in a pack across the requested tiers.

    This is the top-level entry point for `bangerpdf build`.

    Args:
        pack_dir: Path to the pack directory.
        tiers: List of tiers to build (default: ["desktop"]).
        only: If set, only build the document whose name contains this string.

    Returns:
        BuildResult with all rendered documents and any errors.
    """
    pack_dir = Path(pack_dir).resolve()

    if tiers is None:
        tiers = ["desktop"]

    # For Phase 4, we only process the first tier (extend later)
    tier = tiers[0]

    try:
        pack = load_pack(pack_dir)
    except (FileNotFoundError, ValueError) as e:
        result = BuildResult(pack_dir=pack_dir, tier=tier)
        result.errors.append(str(e))
        return result

    env = build_env(pack)

    # Filter documents if --only specified
    docs_to_build = pack.documents
    if only:
        docs_to_build = [d for d in docs_to_build if only in d.name or only in d.template]
        if not docs_to_build:
            result = BuildResult(pack_dir=pack_dir, tier=tier)
            result.errors.append(
                f"No documents matching '{only}'. "
                f"Available: {[d.name for d in pack.documents]}"
            )
            return result

    result = BuildResult(pack_dir=pack_dir, tier=tier)

    print(f"Building {pack.name} (v{pack.version})...")
    print(f"  Pack:      {pack_dir}")
    print(f"  Tier:      {tier}")
    print(f"  Brand:     {pack.brand.name}")
    print(f"  Documents: {len(docs_to_build)}")
    print()

    for doc_spec in docs_to_build:
        try:
            doc_result = render_document(pack, doc_spec, env, tier=tier)
            result.docs.append(doc_result)

            size_kb = doc_result.size_bytes / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            print(
                f"  {doc_result.name:30s} -> pdfs/{tier}/{doc_result.name}.pdf "
                f"({size_str}, {doc_result.page_count} page{'s' if doc_result.page_count != 1 else ''})"
            )
        except Exception as e:
            error_msg = f"Error rendering {doc_spec.name}: {e}"
            result.errors.append(error_msg)
            print(f"  ERROR: {error_msg}", file=sys.stderr)

    print()
    if result.errors:
        print(f"Done with {len(result.errors)} error(s). {result.pdf_count} PDF(s) built.")
    else:
        print(f"Done. {result.pdf_count} PDF(s) in pdfs/{tier}/")

    return result
