"""
proof — PDF → PNG conversion for visual proofing and side-by-side comparison.

Lifted from JJ's pdf-toolkit `pdf-to-images.py` (commit ae5cbf73d, Mar 2 2026)
with the .venv auto-discovery hack removed.

Useful for sharing proofs without sending the PDF, comparing v1 vs v2 in
Review Bundles, and generating thumbnails for the QA dashboard.

Usage:
    from bangerpdf.proof import pdf_to_images
    paths = pdf_to_images("output.pdf", dpi=150)
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    print("ERROR: pdf2image not installed. Install bangerpdf with: pip install bangerpdf",
          file=sys.stderr)
    sys.exit(1)


def pdf_to_images(
    input_path: str,
    output_dir: str | None = None,
    dpi: int = 150,
    fmt: str = 'png',
) -> list[str]:
    """Convert PDF pages to images. Returns list of output paths.

    Args:
        input_path: Path to a PDF file.
        output_dir: Directory for output images. Defaults to same dir as input.
        dpi: Resolution. 150 for screen review, 300 for print-quality proofs.
        fmt: 'png' or 'jpeg'.

    Returns:
        List of absolute paths to the generated image files.
    """
    input_path = os.path.abspath(input_path)
    stem = Path(input_path).stem

    if output_dir:
        out_dir = os.path.abspath(output_dir)
    else:
        out_dir = os.path.dirname(input_path)

    os.makedirs(out_dir, exist_ok=True)

    print(f"Converting {input_path} to {fmt.upper()} at {dpi} DPI...")

    try:
        images = convert_from_path(input_path, dpi=dpi)
    except Exception as e:
        if 'poppler' in str(e).lower() or 'pdftoppm' in str(e).lower():
            print("ERROR: poppler not found. Install it: brew install poppler",
                  file=sys.stderr)
            sys.exit(1)
        raise

    output_paths = []
    for i, image in enumerate(images, 1):
        filename = f"{stem}-page{i}.{fmt}"
        out_path = os.path.join(out_dir, filename)
        image.save(out_path, fmt.upper())
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  ✓ {out_path} ({image.width}×{image.height}, {size_kb:.0f} KB)")
        output_paths.append(out_path)

    print(f"\n{len(images)} page{'s' if len(images) != 1 else ''} exported.")
    return output_paths


def main():
    """Standalone CLI (for backwards compat with JJ scripts)."""
    parser = argparse.ArgumentParser(
        description='Convert PDF pages to PNG images for proofing'
    )
    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: same as input)')
    parser.add_argument('--dpi', type=int, default=150,
                        help='Resolution in DPI (default: 150, use 300 for print-quality)')
    parser.add_argument('--format', choices=['png', 'jpeg'], default='png',
                        help='Output format (default: png)')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: {args.input} not found.", file=sys.stderr)
        sys.exit(1)

    pdf_to_images(
        input_path=args.input,
        output_dir=args.output_dir,
        dpi=args.dpi,
        fmt=args.format,
    )


if __name__ == '__main__':
    main()
