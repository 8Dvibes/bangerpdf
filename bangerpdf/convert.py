"""
convert — HTML → PDF conversion using WeasyPrint.

Lifted from JJ's pdf-toolkit `html-to-pdf.py` (commit ae5cbf73d, Mar 2 2026)
with the .venv auto-discovery hack and importlib sibling-script loader removed
(both unnecessary now that bangerpdf is a proper Python package).

The print-tier-aware variant lives in `bangerpdf.tiers`. This module handles
the basic single-tier (desktop) case.

Usage:
    from bangerpdf.convert import convert_html_to_pdf
    out_path = convert_html_to_pdf("brochure.html", embed=True)
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path

import weasyprint

from bangerpdf.embed_assets import embed_assets


PAGE_CSS = {
    'letter': '@page { size: letter; margin: 0.75in; }',
    'a4': '@page { size: A4; margin: 20mm; }',
}

PRINT_COLOR_CSS = """
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
}
"""


def has_page_rule(html: str) -> bool:
    """Check if the HTML already contains an @page CSS rule."""
    return bool(re.search(r'@page\s*[:{]', html))


def has_color_adjust(html: str) -> bool:
    """Check if the HTML already has print-color-adjust."""
    return 'print-color-adjust' in html or 'color-adjust' in html


def inject_css(html: str, css: str) -> str:
    """Inject CSS into the HTML, preferring existing <style> or <head>."""
    style_tag = f'\n<style>\n{css}\n</style>\n'

    # Try to inject before closing </head>
    if '</head>' in html:
        return html.replace('</head>', f'{style_tag}</head>', 1)

    # Try to inject after opening <html>
    if '<html' in html:
        match = re.search(r'<html[^>]*>', html)
        if match:
            pos = match.end()
            return html[:pos] + style_tag + html[pos:]

    # Fallback: prepend
    return style_tag + html


def convert_html_to_pdf(
    input_path: str,
    output_path: str | None = None,
    size: str = 'letter',
    embed: bool = False,
    output_dir: str | None = None,
) -> str:
    """Convert a single HTML file to PDF. Returns the output path."""
    input_path = os.path.abspath(input_path)
    base_dir = os.path.dirname(input_path)
    stem = Path(input_path).stem

    # Determine output path
    if output_path:
        out = os.path.abspath(output_path)
    elif output_dir:
        os.makedirs(output_dir, exist_ok=True)
        out = os.path.join(os.path.abspath(output_dir), f'{stem}.pdf')
    else:
        out = os.path.join(base_dir, f'{stem}.pdf')

    # Read HTML
    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Embed local assets if requested
    if embed:
        html, count = embed_assets(html, base_dir)
        if count > 0:
            print(f"  Embedded {count} asset(s)")

    # Inject @page CSS if not present
    css_to_inject = ''
    if not has_page_rule(html):
        css_to_inject += PAGE_CSS.get(size, PAGE_CSS['letter']) + '\n'

    if not has_color_adjust(html):
        css_to_inject += PRINT_COLOR_CSS

    if css_to_inject:
        html = inject_css(html, css_to_inject)

    # Generate PDF using WeasyPrint's document API for accurate page count
    html_doc = weasyprint.HTML(string=html, base_url=base_dir)
    document = html_doc.render()
    page_count = len(document.pages)
    document.write_pdf(out)

    # Report
    size_kb = os.path.getsize(out) / 1024
    size_str = f'{size_kb:.1f} KB' if size_kb < 1024 else f'{size_kb/1024:.1f} MB'
    print(f"  ✓ {out} ({size_str}, {page_count} page{'s' if page_count != 1 else ''})")

    return out


def convert_batch(
    files: list[str],
    output_path: str | None = None,
    size: str = 'letter',
    embed: bool = False,
    output_dir: str | None = None,
) -> tuple[int, int]:
    """Convert multiple HTML files. Returns (success_count, total_count)."""
    if len(files) > 1 and output_path:
        raise ValueError("output_path can only be used with a single input file. Use output_dir for batch.")

    print(f"Converting {len(files)} file{'s' if len(files) > 1 else ''} to PDF...")

    success = 0
    for f in files:
        if not os.path.isfile(f):
            print(f"  ERROR: {f} not found, skipping", file=sys.stderr)
            continue
        try:
            convert_html_to_pdf(
                input_path=f,
                output_path=output_path if len(files) == 1 else None,
                size=size,
                embed=embed,
                output_dir=output_dir,
            )
            success += 1
        except Exception as e:
            print(f"  ERROR converting {f}: {e}", file=sys.stderr)

    if len(files) > 1:
        print(f"\nDone: {success}/{len(files)} files converted successfully.")

    return success, len(files)


def main():
    """Standalone CLI (for backwards compat with JJ scripts)."""
    parser = argparse.ArgumentParser(
        description='Convert HTML files to print-ready PDFs using WeasyPrint'
    )
    parser.add_argument('input', nargs='+', help='Input HTML file(s) or glob patterns')
    parser.add_argument('-o', '--output', help='Output PDF path (single file mode)')
    parser.add_argument('--output-dir', help='Output directory (batch mode)')
    parser.add_argument('--size', choices=['letter', 'a4'], default='letter',
                        help='Page size (default: letter)')
    parser.add_argument('--embed-assets', action='store_true',
                        help='Embed local images as base64 before conversion')
    args = parser.parse_args()

    # Expand globs
    files = []
    for pattern in args.input:
        expanded = glob.glob(pattern)
        if expanded:
            files.extend(expanded)
        else:
            files.append(pattern)  # Let it fail with a clear error

    if not files:
        print("ERROR: No input files found.", file=sys.stderr)
        sys.exit(1)

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
        sys.exit(1)

    sys.exit(0 if success == total else 1)


if __name__ == '__main__':
    main()
