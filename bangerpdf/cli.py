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

    # --- Stubs for later phases ---
    for cmd_name, helptext in [
        ("review", "Manage Review Bundles (Phase 7)"),
        ("skills", "Install/uninstall bundled Claude Code skills (Phase 8)"),
    ]:
        p_stub = sub.add_parser(cmd_name, help=helptext)
        p_stub.set_defaults(func=cmd_not_yet_implemented, _command=cmd_name)

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
