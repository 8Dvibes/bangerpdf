"""
cli — argparse dispatcher for the `bangerpdf` command.

Subcommand groups:
    convert     HTML → PDF (single or batch)
    proof       PDF → PNG for visual review
    init        Scaffold a new pack from a starter
    build       Render data + templates → PDFs (across print tiers)
    qa          Run the QA checker against rendered PDFs
    review      Manage Review Bundles (v1 → v2 → approval)
    brand       Show or edit brand-kit.yaml
    list-packs  Inspect installed starter packs
    skills      Install/uninstall bundled Claude Code skills
    doctor      Verify dependencies and installation
    --version   Print version
"""

import argparse
import sys

from bangerpdf import __version__


def cmd_convert(args: argparse.Namespace) -> int:
    """HTML → PDF conversion."""
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
    """PDF → PNG for visual review."""
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


def cmd_doctor(args: argparse.Namespace) -> int:
    """Verify dependencies and installation."""
    print(f"bangerpdf {__version__}")
    print()

    checks = []

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 10)
    checks.append(("Python", py_ver, py_ok, "≥3.10 required"))

    # WeasyPrint
    try:
        import weasyprint
        wp_ver = weasyprint.__version__
        wp_ok = True
    except ImportError as e:
        wp_ver = f"NOT INSTALLED ({e})"
        wp_ok = False
    checks.append(("WeasyPrint", wp_ver, wp_ok, "≥67.0 for CMYK support"))

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
    checks.append(("pdf2image", p2i_ver, p2i_ok, "PDF → PNG proofs"))

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
        marker = "✓" if ok else "✗"
        print(f"  {marker} {name:<{width}}  {version:<25}  {note}")
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


def cmd_not_yet_implemented(args: argparse.Namespace) -> int:
    """Stub for subcommands landing in later phases."""
    cmd = getattr(args, "_command", "this command")
    print(f"`bangerpdf {cmd}` is not yet implemented in v0.1.0.", file=sys.stderr)
    print("Coming in a future phase. Track progress at github.com/8Dvibes/bangerpdf",
          file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bangerpdf",
        description="Make banger PDFs from HTML or data — print-ready output across desktop, "
                    "digital press, and commercial offset tiers.",
    )
    parser.add_argument("--version", action="version", version=f"bangerpdf {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # convert
    p_convert = sub.add_parser("convert", help="HTML → PDF conversion (single or batch)")
    p_convert.add_argument("input", nargs="+", help="Input HTML file(s) or glob patterns")
    p_convert.add_argument("-o", "--output", help="Output PDF path (single file mode)")
    p_convert.add_argument("--output-dir", help="Output directory (batch mode)")
    p_convert.add_argument("--size", choices=["letter", "a4"], default="letter",
                           help="Page size (default: letter)")
    p_convert.add_argument("--embed-assets", action="store_true",
                           help="Embed local images as base64 before conversion")
    p_convert.set_defaults(func=cmd_convert)

    # proof
    p_proof = sub.add_parser("proof", help="PDF → PNG for visual review")
    p_proof.add_argument("input", help="Input PDF file")
    p_proof.add_argument("-o", "--output-dir", help="Output directory")
    p_proof.add_argument("--dpi", type=int, default=150,
                         help="Resolution in DPI (default: 150)")
    p_proof.add_argument("--format", choices=["png", "jpeg"], default="png",
                         help="Output format (default: png)")
    p_proof.set_defaults(func=cmd_proof)

    # doctor
    p_doctor = sub.add_parser("doctor", help="Verify dependencies and installation")
    p_doctor.set_defaults(func=cmd_doctor)

    # Stubs for later phases (registered so --help shows them)
    for cmd_name, helptext in [
        ("init", "Scaffold a new pack from a starter (Phase 4)"),
        ("build", "Render data + templates → PDFs across tiers (Phase 4)"),
        ("qa", "Run the QA checker against rendered PDFs (Phase 3)"),
        ("review", "Manage Review Bundles (Phase 7)"),
        ("brand", "Show or edit brand-kit.yaml (Phase 4)"),
        ("list-packs", "Inspect installed starter packs (Phase 5)"),
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
