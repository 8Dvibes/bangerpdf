"""
cli — argparse dispatcher for the `bangerpdf` command.

Subcommand groups:
    convert     HTML -> PDF (single or batch)
    proof       PDF -> PNG for visual review
    init        Scaffold a new pack from a starter
    build       Render data + templates -> PDFs (across print tiers)
    qa          Run the QA checker against rendered PDFs
    review      Manage Review Bundles (v1 -> v2 -> approval)
    brand       Show or edit brand-kit.yaml
    list-packs  Inspect installed starter packs
    show        Pretty-print data.json
    set         Mutate a key in data.json
    validate    Validate data.json against schema
    skills      Install/uninstall bundled Claude Code skills
    doctor      Verify dependencies and installation
    --version   Print version
"""

import argparse
import json
import sys
from pathlib import Path

from bangerpdf import __version__


# ---------------------------------------------------------------------------
# Existing commands (unchanged)
# ---------------------------------------------------------------------------

def cmd_convert(args: argparse.Namespace) -> int:
    """HTML -> PDF conversion."""
    from bangerpdf.convert import convert_batch
    import glob

    files = []
    for pattern in args.input:
        expanded = glob.glob(pattern)
        if expanded:
            files.extend(expanded)
        else:
            files.append(pattern)

    if not files:
        print("ERROR: No input files found.", file=sys.stderr)
        return 1

    try:
        success, total = convert_batch(
            files=files,
            output_path=args.output,
            size=args.size,
            embed=args.embed_assets,
            output_dir=args.output_dir,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0 if success == total else 1


def cmd_proof(args: argparse.Namespace) -> int:
    """PDF -> PNG for visual review."""
    from bangerpdf.proof import pdf_to_images
    import os

    if not os.path.isfile(args.input):
        print(f"ERROR: {args.input} not found.", file=sys.stderr)
        return 1

    pdf_to_images(
        input_path=args.input,
        output_dir=args.output_dir,
        dpi=args.dpi,
        fmt=args.format,
    )
    return 0


def cmd_qa(args: argparse.Namespace) -> int:
    """Run the QA checker against a directory of PDFs (or a single PDF)."""
    from bangerpdf.qa.runner import QARunner
    from bangerpdf.qa.dashboard import render_dashboard, render_json

    # Parse --expected as "filename=N,filename=N"
    expected_pages = None
    if args.expected:
        expected_pages = {}
        for pair in args.expected.split(","):
            if "=" not in pair:
                continue
            name, count = pair.split("=", 1)
            try:
                expected_pages[name.strip()] = int(count.strip())
            except ValueError:
                print(f"WARNING: invalid --expected entry: {pair}", file=sys.stderr)

    # Parse --headlines as "label=value,label=value"
    headlines = None
    if args.headlines:
        headlines = {}
        for pair in args.headlines.split(","):
            if "=" not in pair:
                continue
            label, value = pair.split("=", 1)
            headlines[label.strip()] = value.strip()

    only = set(args.only.split(",")) if args.only else None

    runner = QARunner(
        corpus_dir=args.input,
        expected_pages=expected_pages,
        only=only,
        data_path=args.data,
        headlines=headlines,
        bleed_in=args.bleed_in,
        require_pdfx=args.require_pdfx,
        require_pdfa=args.require_pdfa,
        check_links=args.check_links,
    )
    report = runner.run()

    if args.json:
        print(render_json(report))
    else:
        print(render_dashboard(report))

    return report.exit_code(strict=args.strict)


def cmd_doctor(args: argparse.Namespace) -> int:
    """Verify dependencies and installation."""
    print(f"bangerpdf {__version__}")
    print()

    checks = []

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 10)
    checks.append(("Python", py_ver, py_ok, ">=3.10 required"))

    # WeasyPrint
    try:
        import weasyprint
        wp_ver = weasyprint.__version__
        wp_ok = True
    except ImportError as e:
        wp_ver = f"NOT INSTALLED ({e})"
        wp_ok = False
    checks.append(("WeasyPrint", wp_ver, wp_ok, ">=67.0 for CMYK support"))

    # PyMuPDF
    try:
        import fitz
        fitz_ver = fitz.version[0]
        fitz_ok = True
    except ImportError as e:
        fitz_ver = f"NOT INSTALLED ({e})"
        fitz_ok = False
    checks.append(("PyMuPDF", fitz_ver, fitz_ok, "QA checker"))

    # Jinja2
    try:
        import jinja2
        j2_ver = jinja2.__version__
        j2_ok = True
    except ImportError as e:
        j2_ver = f"NOT INSTALLED ({e})"
        j2_ok = False
    checks.append(("Jinja2", j2_ver, j2_ok, "templating"))

    # PyYAML
    try:
        import yaml
        yaml_ver = yaml.__version__
        yaml_ok = True
    except ImportError as e:
        yaml_ver = f"NOT INSTALLED ({e})"
        yaml_ok = False
    checks.append(("PyYAML", yaml_ver, yaml_ok, "brand-kit + pack manifests"))

    # pdf2image (for proof)
    try:
        import pdf2image
        p2i_ver = "installed"
        p2i_ok = True
    except ImportError as e:
        p2i_ver = f"NOT INSTALLED ({e})"
        p2i_ok = False
    checks.append(("pdf2image", p2i_ver, p2i_ok, "PDF -> PNG proofs"))

    # Pillow
    try:
        import PIL
        pil_ver = PIL.__version__
        pil_ok = True
    except ImportError as e:
        pil_ver = f"NOT INSTALLED ({e})"
        pil_ok = False
    checks.append(("Pillow", pil_ver, pil_ok, "image manipulation"))

    # Print results
    width = max(len(c[0]) for c in checks)
    all_ok = True
    for name, version, ok, note in checks:
        marker = "OK" if ok else "MISSING"
        print(f"  {marker:7s} {name:<{width}}  {version:<25}  {note}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("All dependencies present. bangerpdf is ready to use.")
        return 0
    else:
        print("Some dependencies are missing. Run: pip install bangerpdf --break-system-packages",
              file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Phase 4: new commands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    """Scaffold a new pack from a starter."""
    from bangerpdf.packs import init_pack

    # Build brand overrides from CLI flags
    brand_overrides = None
    has_override = args.brand or args.primary or args.logo
    if has_override:
        brand_overrides = {"brand": {}}
        if args.brand:
            brand_overrides["brand"]["name"] = args.brand
        if args.primary:
            brand_overrides["brand"]["primary"] = args.primary
        if args.logo:
            brand_overrides["brand"]["logo"] = args.logo

    try:
        init_pack(
            pack_name=args.pack,
            target_dir=args.dir,
            brand_overrides=brand_overrides,
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Render data + templates -> PDFs across tiers."""
    from bangerpdf.render import build_pack

    # Determine tiers
    if args.tier == "all":
        tiers = ["desktop", "digital-press", "commercial"]
    else:
        tiers = [args.tier]

    result = build_pack(
        pack_dir=args.dir or ".",
        tiers=tiers,
        only=args.only,
    )

    if not result.success:
        return 1
    return 0


def cmd_brand(args: argparse.Namespace) -> int:
    """Show or edit brand-kit.yaml."""
    brand_action = getattr(args, "brand_action", None)

    if brand_action == "set":
        return cmd_brand_set(args)
    else:
        # Default: show
        return cmd_brand_show(args)


def cmd_brand_show(args: argparse.Namespace) -> int:
    """Pretty-print brand-kit.yaml contents."""
    from bangerpdf.brand import load_brand

    project_dir = getattr(args, "dir", None) or "."
    brand_path = Path(project_dir) / "brand-kit.yaml"

    if not brand_path.exists():
        print(f"No brand-kit.yaml found in {Path(project_dir).resolve()}", file=sys.stderr)
        return 1

    brand = load_brand(project_dir)
    items = brand.as_dict()

    width = max(len(k) for k in items)
    print("Brand Kit:")
    print()
    for key, value in items.items():
        print(f"  {key:<{width}}  {value}")

    return 0


def cmd_brand_set(args: argparse.Namespace) -> int:
    """Update a key in brand-kit.yaml."""
    from bangerpdf.brand import update_brand_yaml

    project_dir = getattr(args, "dir", None) or "."
    brand_path = Path(project_dir) / "brand-kit.yaml"

    if not brand_path.exists():
        print(f"No brand-kit.yaml found in {Path(project_dir).resolve()}", file=sys.stderr)
        return 1

    try:
        update_brand_yaml(brand_path, args.key, args.value)
        print(f"Updated {args.key} = {args.value}")
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_list_packs(args: argparse.Namespace) -> int:
    """List installed starter packs."""
    from bangerpdf.packs import list_packs

    packs = list_packs()

    if not packs:
        print("No starter packs found.")
        return 0

    print(f"Installed starter packs ({len(packs)}):")
    print()

    name_width = max(len(p.name) for p in packs)
    for p in packs:
        print(f"  {p.name:<{name_width}}  v{p.version:<6}  {p.document_count} doc(s)  {p.description}")

    print()
    print("Use: bangerpdf init <pack> <directory>")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate data.json against data.schema.json."""
    from bangerpdf.packs import validate_data

    project_dir = args.dir or "."
    errors = validate_data(project_dir)

    if errors:
        print(f"Validation failed ({len(errors)} error(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("data.json is valid.")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Pretty-print data.json."""
    project_dir = args.dir or "."
    data_path = Path(project_dir) / "data.json"

    if not data_path.exists():
        print(f"No data.json found in {Path(project_dir).resolve()}", file=sys.stderr)
        return 1

    with open(data_path) as f:
        data = json.load(f)

    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    """Set a value in data.json using dot-notation keys."""
    project_dir = args.dir or "."
    data_path = Path(project_dir) / "data.json"

    if not data_path.exists():
        print(f"No data.json found in {Path(project_dir).resolve()}", file=sys.stderr)
        return 1

    with open(data_path) as f:
        data = json.load(f)

    # Navigate dot-notation key
    keys = args.key.split(".")
    target = data
    for k in keys[:-1]:
        if k not in target or not isinstance(target[k], dict):
            target[k] = {}
        target = target[k]

    # Try to parse value as JSON (for numbers, booleans, arrays)
    value = args.value
    try:
        value = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        pass  # Keep as string

    target[keys[-1]] = value

    with open(data_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Set {args.key} = {json.dumps(value)}")
    return 0


def cmd_not_yet_implemented(args: argparse.Namespace) -> int:
    """Stub for subcommands landing in later phases."""
    cmd = getattr(args, "_command", "this command")
    print(f"`bangerpdf {cmd}` is not yet implemented in v{__version__}.", file=sys.stderr)
    print("Coming in a future phase. Track progress at github.com/8Dvibes/bangerpdf",
          file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# Phase 8: Review Bundle commands
# ---------------------------------------------------------------------------

def cmd_review_init(args: argparse.Namespace) -> int:
    """Scaffold a review bundle from a rendered pack."""
    from bangerpdf.review.builder import init_review

    review_dir = args.review_dir or "./review-bundle"
    source = args.source

    if not source:
        print("ERROR: --from is required. Point it at a pack with rendered PDFs.", file=sys.stderr)
        return 1

    try:
        init_review(source, review_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_review_build(args: argparse.Namespace) -> int:
    """Render the review HTML templates."""
    from bangerpdf.review.builder import build_review

    review_dir = args.review_dir or "./review-bundle"

    meta_path = Path(review_dir) / "meta.json"
    if not meta_path.exists():
        print(f"ERROR: No meta.json found in {review_dir}. "
              f"Run 'bangerpdf review init' first.", file=sys.stderr)
        return 1

    try:
        build_review(review_dir)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_review_annotate(args: argparse.Namespace) -> int:
    """Add an annotation to a document in the review bundle."""
    from bangerpdf.review.workflow import add_annotation

    review_dir = args.review_dir or "./review-bundle"

    meta_path = Path(review_dir) / "meta.json"
    if not meta_path.exists():
        print(f"ERROR: No meta.json found in {review_dir}. "
              f"Run 'bangerpdf review init' first.", file=sys.stderr)
        return 1

    try:
        meta = add_annotation(review_dir, args.doc, args.page, args.note)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    decision = meta["decisions"][-1]
    print(f"Added annotation {decision['id']}: {args.doc} p{args.page} - {args.note}")
    print(f"Status: {meta['status']} ({len(meta['decisions'])} total annotation(s))")
    return 0


def cmd_review_revise(args: argparse.Namespace) -> int:
    """Bump version and enter revision state."""
    from bangerpdf.review.workflow import revise

    review_dir = args.review_dir or "./review-bundle"

    meta_path = Path(review_dir) / "meta.json"
    if not meta_path.exists():
        print(f"ERROR: No meta.json found in {review_dir}. "
              f"Run 'bangerpdf review init' first.", file=sys.stderr)
        return 1

    try:
        meta = revise(review_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Revised to {meta['version']}. Status: {meta['status']}")
    print(f"PDFs copied to assets/pdfs/{meta['version']}/")
    print(f"Run 'bangerpdf review build {review_dir}' to regenerate HTML.")
    return 0


def cmd_review_approve(args: argparse.Namespace) -> int:
    """Approve the review bundle."""
    from bangerpdf.review.workflow import approve

    review_dir = args.review_dir or "./review-bundle"

    meta_path = Path(review_dir) / "meta.json"
    if not meta_path.exists():
        print(f"ERROR: No meta.json found in {review_dir}. "
              f"Run 'bangerpdf review init' first.", file=sys.stderr)
        return 1

    try:
        meta = approve(review_dir, approver_name=args.approver)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Review bundle APPROVED by {meta['approved_by']} at {meta['approved_at']}")
    return 0


def cmd_review_status(args: argparse.Namespace) -> int:
    """Show current review bundle status."""
    from bangerpdf.review.workflow import get_meta

    review_dir = args.review_dir or "./review-bundle"

    meta_path = Path(review_dir) / "meta.json"
    if not meta_path.exists():
        print(f"ERROR: No meta.json found in {review_dir}.", file=sys.stderr)
        return 1

    try:
        meta = get_meta(review_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    docs = meta.get("documents", [])
    decisions = meta.get("decisions", [])
    resolved = sum(1 for d in decisions if d.get("resolved"))

    print(f"Review Bundle: {review_dir}")
    print(f"  Status:      {meta['status']}")
    print(f"  Version:     {meta['version']}")
    print(f"  Source:      {meta.get('source_pack', 'unknown')}")
    print(f"  Created:     {meta.get('created_at', 'unknown')}")
    print(f"  Documents:   {len(docs)}")
    print(f"  Annotations: {len(decisions)} ({resolved} resolved, {len(decisions) - resolved} open)")

    if meta.get("approved_by"):
        print(f"  Approved by: {meta['approved_by']}")
        print(f"  Approved at: {meta['approved_at']}")

    if decisions:
        print()
        print("  Annotations:")
        for d in decisions:
            status_mark = "[x]" if d.get("resolved") else "[ ]"
            print(f"    {status_mark} {d['id']}: {d['doc']} p{d['page']} - {d['note']}")

    return 0


# ---------------------------------------------------------------------------
# Skills commands
# ---------------------------------------------------------------------------

def cmd_skills_list(args: argparse.Namespace) -> int:
    from bangerpdf.skills import cmd_list
    cmd_list(as_json=getattr(args, "as_json", False))
    return 0


def cmd_skills_install(args: argparse.Namespace) -> int:
    from bangerpdf.skills import cmd_install
    names = args.names if args.names else None
    cmd_install(names=names, force=args.force, as_json=getattr(args, "as_json", False))
    return 0


def cmd_skills_uninstall(args: argparse.Namespace) -> int:
    from bangerpdf.skills import cmd_uninstall
    cmd_uninstall(names=args.names, as_json=getattr(args, "as_json", False))
    return 0


def cmd_skills_path(args: argparse.Namespace) -> int:
    from bangerpdf.skills import cmd_path
    cmd_path(as_json=getattr(args, "as_json", False))
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bangerpdf",
        description="Make banger PDFs from HTML or data -- print-ready output across desktop, "
                    "digital press, and commercial offset tiers.",
    )
    parser.add_argument("--version", action="version", version=f"bangerpdf {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # --- convert ---
    p_convert = sub.add_parser("convert", help="HTML -> PDF conversion (single or batch)")
    p_convert.add_argument("input", nargs="+", help="Input HTML file(s) or glob patterns")
    p_convert.add_argument("-o", "--output", help="Output PDF path (single file mode)")
    p_convert.add_argument("--output-dir", help="Output directory (batch mode)")
    p_convert.add_argument("--size", choices=["letter", "a4"], default="letter",
                           help="Page size (default: letter)")
    p_convert.add_argument("--embed-assets", action="store_true",
                           help="Embed local images as base64 before conversion")
    p_convert.set_defaults(func=cmd_convert)

    # --- proof ---
    p_proof = sub.add_parser("proof", help="PDF -> PNG for visual review")
    p_proof.add_argument("input", help="Input PDF file")
    p_proof.add_argument("-o", "--output-dir", help="Output directory")
    p_proof.add_argument("--dpi", type=int, default=150,
                         help="Resolution in DPI (default: 150)")
    p_proof.add_argument("--format", choices=["png", "jpeg"], default="png",
                         help="Output format (default: png)")
    p_proof.set_defaults(func=cmd_proof)

    # --- doctor ---
    p_doctor = sub.add_parser("doctor", help="Verify dependencies and installation")
    p_doctor.set_defaults(func=cmd_doctor)

    # --- qa ---
    p_qa = sub.add_parser("qa", help="Run the QA checker against rendered PDFs")
    p_qa.add_argument("input", nargs="?", default=".",
                      help="PDF file or directory of PDFs (default: current dir)")
    p_qa.add_argument("--strict", action="store_true",
                      help="Exit nonzero on warnings as well as errors")
    p_qa.add_argument("--json", action="store_true",
                      help="Emit machine-readable JSON instead of the dashboard")
    p_qa.add_argument("--expected",
                      help="Expected page counts as 'file.pdf=2,other.pdf=7'")
    p_qa.add_argument("--only",
                      help="Comma-separated check names to run (default: all active)")
    p_qa.add_argument("--data",
                      help="Path to data.json (enables Jinja2 dict.items collision check)")
    p_qa.add_argument("--headlines",
                      help="Cross-doc headline consistency: 'bid_total=$445000,client=Acme Corp'")
    p_qa.add_argument("--bleed-in", type=float, default=0.0,
                      help="Expected bleed in inches (0=skip, 0.125=standard print bleed)")
    p_qa.add_argument("--require-pdfx", action="store_true",
                      help="Treat missing PDF/X markers as an error (commercial tier)")
    p_qa.add_argument("--require-pdfa", action="store_true",
                      help="Treat missing PDF/A markers as an error (archival tier)")
    p_qa.add_argument("--check-links", action="store_true",
                      help="Ping every external URL (HEAD with cache, slow)")
    p_qa.set_defaults(func=cmd_qa)

    # --- init ---
    p_init = sub.add_parser("init", help="Scaffold a new pack from a starter")
    p_init.add_argument("pack", help="Starter pack name (e.g. 'demo', 'bid-package')")
    p_init.add_argument("dir", help="Target directory for the new project")
    p_init.add_argument("--brand", help="Brand name override")
    p_init.add_argument("--primary", help="Primary color hex override (e.g. '#FF0000')")
    p_init.add_argument("--logo", help="Path to logo file override")
    p_init.set_defaults(func=cmd_init)

    # --- build ---
    p_build = sub.add_parser("build", help="Render data + templates -> PDFs across tiers")
    p_build.add_argument("--dir", default=None,
                         help="Pack directory (default: current dir)")
    p_build.add_argument("--tier", choices=["desktop", "digital-press", "commercial", "all"],
                         default="desktop",
                         help="Print tier (default: desktop)")
    p_build.add_argument("--only", help="Only build documents matching this name")
    p_build.set_defaults(func=cmd_build)

    # --- brand (with subcommands: show, set) ---
    p_brand = sub.add_parser("brand", help="Show or edit brand-kit.yaml")
    p_brand.add_argument("--dir", default=None,
                         help="Project directory (default: current dir)")
    brand_sub = p_brand.add_subparsers(dest="brand_action", metavar="ACTION")

    p_brand_show = brand_sub.add_parser("show", help="Display current brand settings")
    p_brand_show.set_defaults(func=cmd_brand)

    p_brand_set = brand_sub.add_parser("set", help="Update a brand-kit.yaml value")
    p_brand_set.add_argument("key", help="Key to set (e.g. 'brand.primary', 'print.bleed_in')")
    p_brand_set.add_argument("value", help="New value")
    p_brand_set.set_defaults(func=cmd_brand)

    p_brand.set_defaults(func=cmd_brand)

    # --- list-packs ---
    p_list_packs = sub.add_parser("list-packs", help="Inspect installed starter packs")
    p_list_packs.set_defaults(func=cmd_list_packs)

    # --- validate ---
    p_validate = sub.add_parser("validate", help="Validate data.json against schema")
    p_validate.add_argument("--dir", default=None,
                            help="Project directory (default: current dir)")
    p_validate.set_defaults(func=cmd_validate)

    # --- show ---
    p_show = sub.add_parser("show", help="Pretty-print data.json")
    p_show.add_argument("--dir", default=None,
                        help="Project directory (default: current dir)")
    p_show.set_defaults(func=cmd_show)

    # --- set ---
    p_set = sub.add_parser("set", help="Set a value in data.json")
    p_set.add_argument("key", help="Dot-notation key (e.g. 'project.total')")
    p_set.add_argument("value", help="New value (JSON parsed if possible)")
    p_set.add_argument("--dir", default=None,
                       help="Project directory (default: current dir)")
    p_set.set_defaults(func=cmd_set)

    # --- review (with subcommands: init, build, annotate, revise, approve, status) ---
    p_review = sub.add_parser("review", help="Manage Review Bundles (init, build, annotate, revise, approve, status)")
    review_sub = p_review.add_subparsers(dest="review_action", metavar="ACTION")

    # review init
    p_review_init = review_sub.add_parser("init", help="Scaffold a review bundle from a pack")
    p_review_init.add_argument("review_dir", nargs="?", default=None,
                               help="Review bundle directory (default: ./review-bundle)")
    p_review_init.add_argument("--from", dest="source", required=True,
                               help="Source pack directory with rendered PDFs")
    p_review_init.set_defaults(func=cmd_review_init)

    # review build
    p_review_build = review_sub.add_parser("build", help="Render review HTML templates")
    p_review_build.add_argument("review_dir", nargs="?", default=None,
                                help="Review bundle directory (default: ./review-bundle)")
    p_review_build.set_defaults(func=cmd_review_build)

    # review annotate
    p_review_annotate = review_sub.add_parser("annotate", help="Add an annotation")
    p_review_annotate.add_argument("doc", help="PDF filename (e.g. 01_Cover_Letter.pdf)")
    p_review_annotate.add_argument("--page", type=int, required=True,
                                   help="Page number")
    p_review_annotate.add_argument("--note", required=True,
                                   help="Annotation text")
    p_review_annotate.add_argument("review_dir", nargs="?", default=None,
                                   help="Review bundle directory (default: ./review-bundle)")
    p_review_annotate.set_defaults(func=cmd_review_annotate)

    # review revise
    p_review_revise = review_sub.add_parser("revise", help="Bump version (v1 -> v2)")
    p_review_revise.add_argument("review_dir", nargs="?", default=None,
                                 help="Review bundle directory (default: ./review-bundle)")
    p_review_revise.set_defaults(func=cmd_review_revise)

    # review approve
    p_review_approve = review_sub.add_parser("approve", help="Approve the review bundle")
    p_review_approve.add_argument("--approver", default=None,
                                  help="Name of the approver (default: Client)")
    p_review_approve.add_argument("review_dir", nargs="?", default=None,
                                  help="Review bundle directory (default: ./review-bundle)")
    p_review_approve.set_defaults(func=cmd_review_approve)

    # review status
    p_review_status = review_sub.add_parser("status", help="Show current status")
    p_review_status.add_argument("review_dir", nargs="?", default=None,
                                 help="Review bundle directory (default: ./review-bundle)")
    p_review_status.set_defaults(func=cmd_review_status)

    # Default: show help when just "bangerpdf review" is run
    p_review.set_defaults(func=lambda args: (p_review.print_help(), 0)[-1])

    # --- skills ---
    p_skills = sub.add_parser("skills", help="Install/uninstall bundled Claude Code skills")
    skills_sub = p_skills.add_subparsers(dest="skills_action", metavar="ACTION")

    p_skills_list = skills_sub.add_parser("list", help="List bundled skills and install status")
    p_skills_list.add_argument("--json", dest="as_json", action="store_true")
    p_skills_list.set_defaults(func=cmd_skills_list)

    p_skills_install = skills_sub.add_parser("install", help="Install skills to ~/.claude/skills/")
    p_skills_install.add_argument("names", nargs="*", help="Skill name(s) (default: all)")
    p_skills_install.add_argument("--force", action="store_true", help="Overwrite existing")
    p_skills_install.add_argument("--json", dest="as_json", action="store_true")
    p_skills_install.set_defaults(func=cmd_skills_install)

    p_skills_uninstall = skills_sub.add_parser("uninstall", help="Remove installed skills")
    p_skills_uninstall.add_argument("names", nargs="+", help="Skill name(s) to remove")
    p_skills_uninstall.add_argument("--json", dest="as_json", action="store_true")
    p_skills_uninstall.set_defaults(func=cmd_skills_uninstall)

    p_skills_path = skills_sub.add_parser("path", help="Show the skills install directory")
    p_skills_path.add_argument("--json", dest="as_json", action="store_true")
    p_skills_path.set_defaults(func=cmd_skills_path)

    p_skills.set_defaults(func=lambda args: (p_skills.print_help(), 0)[-1])

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
