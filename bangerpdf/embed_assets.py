"""
embed_assets — Convert external image references to base64 inline data URIs.

This is the single most important step for PDF fidelity. External image
references are the #1 cause of broken images in PDF output.

Lifted from JJ's pdf-toolkit `embed-assets.py` (commit ae5cbf73d, Mar 2 2026)
with no logic changes — JJ's implementation is battle-tested and correct.

Usage:
    from bangerpdf.embed_assets import embed_assets
    html, count = embed_assets(html_string, base_dir="/path/to/html/dir")
"""

import argparse
import base64
import mimetypes
import os
import re
import sys
from pathlib import Path


def get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    mime, _ = mimetypes.guess_type(file_path)
    if mime:
        return mime
    # Fallback for common image types
    ext = Path(file_path).suffix.lower()
    return {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
        '.ico': 'image/x-icon',
        '.bmp': 'image/bmp',
    }.get(ext, 'application/octet-stream')


def file_to_data_uri(file_path: str) -> str | None:
    """Convert a local file to a base64 data URI."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        mime = get_mime_type(file_path)
        b64 = base64.b64encode(data).decode('ascii')
        return f'data:{mime};base64,{b64}'
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"  WARNING: Could not read {file_path}: {e}", file=sys.stderr)
        return None


def is_local_path(src: str) -> bool:
    """Check if a src attribute is a local file (not a URL or data URI)."""
    if not src:
        return False
    if src.startswith(('data:', 'http://', 'https://', '//')):
        return False
    return True


def resolve_path(src: str, base_dir: str) -> str:
    """Resolve a relative path against the HTML file's directory."""
    if os.path.isabs(src):
        return src
    return os.path.normpath(os.path.join(base_dir, src))


def embed_img_tags(html: str, base_dir: str) -> tuple[str, int]:
    """Replace <img src="..."> with base64 data URIs."""
    count = 0

    def replace_img(match):
        nonlocal count
        full_match = match.group(0)
        src = match.group(1)

        if not is_local_path(src):
            return full_match

        resolved = resolve_path(src, base_dir)
        data_uri = file_to_data_uri(resolved)

        if data_uri:
            count += 1
            return full_match.replace(src, data_uri)
        return full_match

    # Match src="..." or src='...' in img tags
    pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
    return re.sub(pattern, replace_img, html, flags=re.IGNORECASE), count


def embed_css_urls(html: str, base_dir: str) -> tuple[str, int]:
    """Replace url(...) references in CSS with base64 data URIs."""
    count = 0

    def replace_url(match):
        nonlocal count
        full_match = match.group(0)
        src = match.group(1).strip('\'"')

        if not is_local_path(src):
            return full_match

        resolved = resolve_path(src, base_dir)
        data_uri = file_to_data_uri(resolved)

        if data_uri:
            count += 1
            return f'url("{data_uri}")'
        return full_match

    pattern = r'url\(([^)]+)\)'
    return re.sub(pattern, replace_url, html), count


def embed_assets(html: str, base_dir: str) -> tuple[str, int]:
    """Embed all local assets in HTML as base64 data URIs.

    Args:
        html: The HTML source.
        base_dir: The directory the HTML was loaded from (used to resolve
                  relative image and CSS url() paths).

    Returns:
        (modified_html, total_assets_embedded)
    """
    total = 0

    html, img_count = embed_img_tags(html, base_dir)
    total += img_count

    html, css_count = embed_css_urls(html, base_dir)
    total += css_count

    return html, total


def main():
    """Standalone CLI for embed-assets (for backwards compat with JJ scripts)."""
    parser = argparse.ArgumentParser(
        description='Convert external image references to base64 inline data URIs'
    )
    parser.add_argument('input', help='Input HTML file')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--in-place', action='store_true',
                        help='Modify the input file directly')
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    base_dir = os.path.dirname(input_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()

    result, count = embed_assets(html, base_dir)

    print(f"Embedded {count} asset(s)", file=sys.stderr)

    if args.in_place:
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Updated {input_path}", file=sys.stderr)
    elif args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(result)


if __name__ == '__main__':
    main()
