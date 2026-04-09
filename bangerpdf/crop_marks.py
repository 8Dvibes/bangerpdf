"""
crop_marks — CSS injection for crop marks and bleed areas.

Handles injecting `marks: crop cross` and `bleed: Xin` into @page CSS rules
for print-ready PDF output. Works with simple @page rules and named/pseudo-class
variants (:first, :left, :right, :blank).

Usage:
    from bangerpdf.crop_marks import inject_crop_marks, has_bleed_rules
    css = "@page { size: letter; margin: 0.75in; }"
    result = inject_crop_marks(css, bleed_in=0.125)
"""

import re


# Pattern to match @page rules, including named pages and pseudo-classes.
# Matches: @page, @page :first, @page :left, @page :right, @page :blank,
#          @page my-page, @page my-page:first, etc.
_PAGE_RULE_RE = re.compile(
    r'(@page\s*(?:[a-zA-Z_][\w-]*)?(?:\s*:\s*(?:first|left|right|blank))?'
    r'\s*\{)',
    re.IGNORECASE,
)

# Pattern to detect existing bleed or marks declarations.
_BLEED_RE = re.compile(r'\bbleed\s*:', re.IGNORECASE)
_MARKS_RE = re.compile(r'\bmarks\s*:', re.IGNORECASE)


def has_bleed_rules(css: str) -> bool:
    """Check if CSS already has bleed or marks rules in any @page block.

    Scans the entire CSS string for `bleed:` or `marks:` declarations.
    Returns True if either is found, meaning the CSS already handles
    print marks and the caller should avoid double-injection.
    """
    return bool(_BLEED_RE.search(css) or _MARKS_RE.search(css))


def inject_crop_marks(css: str, bleed_in: float = 0.125) -> str:
    """Add `marks: crop cross` and `bleed: Xin` to all @page rules.

    If the CSS already contains bleed or marks declarations, the original
    CSS is returned unmodified to avoid conflicts.

    For CSS with no @page rules at all, a new @page block is prepended
    with the marks and bleed declarations.

    Args:
        css: The CSS string to modify.
        bleed_in: Bleed area in inches (default 0.125 = 1/8 inch, the
                  industry standard for digital press and commercial offset).

    Returns:
        The modified CSS string with crop marks and bleed injected.
    """
    # Don't double-inject.
    if has_bleed_rules(css):
        return css

    marks_css = f"  marks: crop cross;\n  bleed: {bleed_in}in;"

    # Find all @page rules and inject marks + bleed after the opening brace.
    matches = list(_PAGE_RULE_RE.finditer(css))

    if not matches:
        # No @page rules exist; prepend a new one.
        return f"@page {{\n{marks_css}\n}}\n{css}"

    # Inject into each @page rule, working from the end to preserve offsets.
    result = css
    for match in reversed(matches):
        opening_brace_end = match.end()
        result = (
            result[:opening_brace_end]
            + "\n" + marks_css + "\n"
            + result[opening_brace_end:]
        )

    return result
