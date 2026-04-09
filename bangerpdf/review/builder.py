"""
builder — Assemble review HTML from PDF artifacts.

Takes a completed render-pack directory and builds a self-contained HTML
review bundle that clients can open in any browser.

Directory structure created:
    review-bundle/
        meta.json               # state machine
        index.html              # landing page
        v1.html                 # document grid for v1
        approval.html           # sign-off page
        assets/
            pdfs/v1/            # PDF copies
            thumbnails/v1/      # page thumbnails (PNG)
        styles.css              # shared stylesheet
"""

import json
import os
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from bangerpdf.review.workflow import init_meta, get_meta, _save_meta


def _template_dir() -> Path:
    """Return the path to the bundled Jinja2 templates for review bundles."""
    return Path(__file__).parent / "templates"


def _build_jinja_env() -> Environment:
    """Create a Jinja2 environment pointing at the review templates."""
    env = Environment(
        loader=FileSystemLoader(str(_template_dir())),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def _find_pdfs(pack_dir: Path) -> list[Path]:
    """Find all PDFs in a pack directory, searching common output locations."""
    pdfs = []

    # Check pdfs/ subdirectories (tiered output)
    pdfs_dir = pack_dir / "pdfs"
    if pdfs_dir.is_dir():
        for tier_dir in sorted(pdfs_dir.iterdir()):
            if tier_dir.is_dir():
                pdfs.extend(sorted(tier_dir.glob("*.pdf")))

    # Check root level
    if not pdfs:
        pdfs = sorted(pack_dir.glob("*.pdf"))

    return pdfs


def _generate_thumbnails(pdf_path: Path, output_dir: Path, dpi: int = 150) -> list[Path]:
    """Generate thumbnail images for each page of a PDF.

    Returns list of thumbnail paths. Falls back gracefully if pdf2image
    is not available.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = pdf_path.stem

    try:
        from pdf2image import convert_from_path
        images = convert_from_path(str(pdf_path), dpi=dpi)
    except ImportError:
        print(f"  WARNING: pdf2image not installed, skipping thumbnails for {pdf_path.name}")
        return []
    except Exception as e:
        if "poppler" in str(e).lower() or "pdftoppm" in str(e).lower():
            print(f"  WARNING: poppler not found, skipping thumbnails for {pdf_path.name}")
            return []
        raise

    paths = []
    for i, image in enumerate(images, 1):
        thumb_path = output_dir / f"{stem}-page{i}.png"
        image.save(str(thumb_path), "PNG")
        paths.append(thumb_path)

    return paths


def _get_pdf_page_count(pdf_path: Path) -> int:
    """Get the page count of a PDF file."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        count = len(doc)
        doc.close()
        return count
    except ImportError:
        # Fallback: count thumbnails if they exist
        return 0


def _generate_diff_thumbnails(
    v1_dir: Path,
    v2_dir: Path,
    output_dir: Path,
    dpi: int = 150,
) -> dict[str, list[str]]:
    """Generate diff images between v1 and v2 PDFs.

    Returns a dict mapping document names to lists of changed page numbers.
    """
    changed: dict[str, list[str]] = {}
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image, ImageChops
        from pdf2image import convert_from_path
    except ImportError:
        return changed

    v2_pdfs = sorted(v2_dir.glob("*.pdf"))

    for v2_pdf in v2_pdfs:
        v1_pdf = v1_dir / v2_pdf.name
        if not v1_pdf.exists():
            # Entirely new document
            changed[v2_pdf.stem] = ["new"]
            continue

        try:
            v1_images = convert_from_path(str(v1_pdf), dpi=dpi)
            v2_images = convert_from_path(str(v2_pdf), dpi=dpi)
        except Exception:
            continue

        changed_pages = []
        max_pages = max(len(v1_images), len(v2_images))

        for i in range(max_pages):
            if i >= len(v1_images):
                # New page in v2
                changed_pages.append(str(i + 1))
                continue
            if i >= len(v2_images):
                # Page removed in v2
                changed_pages.append(str(i + 1))
                continue

            # Compare pixel data
            diff = ImageChops.difference(
                v1_images[i].convert("RGB"),
                v2_images[i].convert("RGB"),
            )

            # If there are any non-zero pixels, the page changed
            bbox = diff.getbbox()
            if bbox is not None:
                changed_pages.append(str(i + 1))
                # Save diff image
                diff_path = output_dir / f"{v2_pdf.stem}-page{i+1}-diff.png"
                diff.save(str(diff_path), "PNG")

        if changed_pages:
            changed[v2_pdf.stem] = changed_pages

    return changed


def init_review(source_pack_dir: str | Path, review_dir: str | Path) -> Path:
    """Create a review bundle structure from a completed render pack.

    Args:
        source_pack_dir: Path to the pack directory with rendered PDFs.
        review_dir: Path where the review bundle will be created.

    Returns:
        Path to the review bundle directory.
    """
    source_pack_dir = Path(source_pack_dir).resolve()
    review_dir = Path(review_dir).resolve()

    if not source_pack_dir.is_dir():
        raise FileNotFoundError(f"Source pack directory not found: {source_pack_dir}")

    # Find PDFs
    pdfs = _find_pdfs(source_pack_dir)
    if not pdfs:
        raise FileNotFoundError(
            f"No PDF files found in {source_pack_dir}. "
            f"Run 'bangerpdf build' first."
        )

    # Create directory structure
    pdf_dir = review_dir / "assets" / "pdfs" / "v1"
    thumb_dir = review_dir / "assets" / "thumbnails" / "v1"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir.mkdir(parents=True, exist_ok=True)

    # Initialize meta.json
    meta = init_meta(review_dir, source_pack_dir)

    # Copy PDFs and generate thumbnails
    print(f"Initializing review bundle at {review_dir}")
    print(f"  Source pack: {source_pack_dir}")
    print(f"  Found {len(pdfs)} PDF(s)")
    print()

    doc_info = []
    for pdf_path in pdfs:
        dest = pdf_dir / pdf_path.name
        shutil.copy2(pdf_path, dest)

        # Generate thumbnails
        thumbs = _generate_thumbnails(pdf_path, thumb_dir)
        page_count = _get_pdf_page_count(pdf_path) or len(thumbs)

        doc_info.append({
            "filename": pdf_path.name,
            "stem": pdf_path.stem,
            "page_count": page_count,
            "thumbnails": [t.name for t in thumbs],
            "size_kb": round(dest.stat().st_size / 1024, 1),
        })

        print(f"  {pdf_path.name}: {page_count} page(s), {len(thumbs)} thumbnail(s)")

    # Store document info in meta.json for template rendering
    meta["documents"] = doc_info
    _save_meta(review_dir, meta)

    print()
    print(f"Review bundle initialized. Run 'bangerpdf review build {review_dir}' to render HTML.")

    return review_dir


def build_review(review_dir: str | Path) -> Path:
    """Render the review HTML templates from meta.json and assets.

    Args:
        review_dir: Path to the review bundle directory.

    Returns:
        Path to the rendered index.html.
    """
    review_dir = Path(review_dir).resolve()
    meta = get_meta(review_dir)

    env = _build_jinja_env()

    # Collect document data for templates
    documents = meta.get("documents", [])
    decisions = meta.get("decisions", [])
    version = meta.get("version", "v1")
    status = meta.get("status", "draft")

    # Build decisions-by-doc lookup
    decisions_by_doc: dict[str, list] = {}
    for d in decisions:
        doc_name = d.get("doc", "")
        if doc_name not in decisions_by_doc:
            decisions_by_doc[doc_name] = []
        decisions_by_doc[doc_name].append(d)

    # Determine available versions
    pdfs_base = review_dir / "assets" / "pdfs"
    versions = sorted(
        [d.name for d in pdfs_base.iterdir() if d.is_dir()],
        key=lambda v: int(v.lstrip("v")),
    ) if pdfs_base.is_dir() else ["v1"]

    # Check for v2 diff data
    diff_data: dict[str, list[str]] = {}
    if len(versions) > 1:
        v1_pdf_dir = review_dir / "assets" / "pdfs" / "v1"
        latest_version = versions[-1]
        latest_pdf_dir = review_dir / "assets" / "pdfs" / latest_version
        diff_dir = review_dir / "assets" / "diffs"

        if v1_pdf_dir.is_dir() and latest_pdf_dir.is_dir():
            diff_data = _generate_diff_thumbnails(
                v1_pdf_dir, latest_pdf_dir, diff_dir
            )

    # Determine project name from source pack path
    source_pack = meta.get("source_pack", "")
    project_name = Path(source_pack).name if source_pack else "Review Bundle"

    # Common template context
    context = {
        "project_name": project_name,
        "version": version,
        "status": status,
        "created_at": meta.get("created_at", ""),
        "updated_at": meta.get("updated_at", ""),
        "documents": documents,
        "decisions": decisions,
        "decisions_by_doc": decisions_by_doc,
        "versions": versions,
        "diff_data": diff_data,
        "approved_by": meta.get("approved_by"),
        "approved_at": meta.get("approved_at"),
        "total_decisions": len(decisions),
        "resolved_decisions": sum(1 for d in decisions if d.get("resolved")),
        "unresolved_decisions": sum(1 for d in decisions if not d.get("resolved")),
    }

    # Render styles.css
    styles_template = env.get_template("styles.css")
    styles_html = styles_template.render(**context)
    (review_dir / "styles.css").write_text(styles_html)

    # Render index.html
    index_template = env.get_template("index.html")
    index_html = index_template.render(**context)
    (review_dir / "index.html").write_text(index_html)

    # Render v1.html
    v1_template = env.get_template("v1.html")
    v1_html = v1_template.render(**context)
    (review_dir / "v1.html").write_text(v1_html)

    # Render v2.html if there's a v2
    if len(versions) > 1:
        v2_template = env.get_template("v2.html")
        v2_html = v2_template.render(**context)
        latest = versions[-1]
        (review_dir / f"{latest}.html").write_text(v2_html)

    # Render approval.html
    approval_template = env.get_template("approval.html")
    approval_html = approval_template.render(**context)
    (review_dir / "approval.html").write_text(approval_html)

    print(f"Review bundle built at {review_dir}")
    print(f"  index.html    - Landing page")
    print(f"  v1.html       - Document grid (v1)")
    if len(versions) > 1:
        print(f"  {versions[-1]}.html      - Document grid ({versions[-1]}) with diff markers")
    print(f"  approval.html - Sign-off page")
    print(f"  styles.css    - Stylesheet")
    print()
    print(f"Open {review_dir / 'index.html'} in a browser to review.")

    return review_dir / "index.html"
