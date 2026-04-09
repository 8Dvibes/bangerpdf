# bangerpdf — Advanced Reference

Extended from JJ's HTML-to-PDF toolkit reference (commit ae5cbf73d, Mar 2 2026).

## @page CSS Rules

The `@page` rule controls physical page properties in PDF output.

### Page Size
```css
@page { size: letter; }               /* 8.5in x 11in */
@page { size: A4; }                   /* 210mm x 297mm */
@page { size: letter landscape; }     /* Landscape orientation */
@page { size: 6in 9in; }             /* Custom size */
```

### Page Margins
```css
@page {
    size: letter;
    margin: 0.75in;                   /* All sides */
    margin: 0.5in 0.75in;            /* Top/bottom, left/right */
    margin: 0.5in 0.75in 1in 0.75in; /* Top, right, bottom, left */
}
```

### Page Selectors (WeasyPrint Supported)
```css
@page :first { margin-top: 1in; }    /* First page only */
@page :left { margin-right: 1in; }   /* Left-side pages (even) */
@page :right { margin-left: 1in; }   /* Right-side pages (odd) */
@page :blank { /* blank page styles */ }
```

### Margin Boxes (Headers and Footers)
WeasyPrint supports all 16 margin box positions. Most common:
```css
@page {
    @top-center {
        content: "Document Title";
        font-size: 9pt;
        color: #94a3b8;
    }
    @bottom-center {
        content: "Company Name  |  Page " counter(page) " of " counter(pages);
        font-size: 8pt;
        color: #94a3b8;
        border-top: 0.5pt solid #cbd5e1;
        padding-top: 6pt;
    }
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-size: 8pt;
    }
}
```

### Bleed and Crop Marks (Digital Press / Commercial Tiers)
```css
@page {
    size: letter;
    margin: 0.75in;
    bleed: 0.125in;
    marks: crop cross;
}
```

**Note:** WeasyPrint 68.1 supports `marks: crop` and `bleed:` natively. bangerpdf's digital-press and commercial-offset tiers inject these automatically.

## Print-Safe CSS (What Works in WeasyPrint)

### Safe to Use
- Flexbox (`display: flex`)
- CSS Grid (`display: grid`)
- `border-radius`, `box-shadow`
- Linear and radial gradients
- CSS transforms (2D)
- CSS variables (`var(--primary)`)
- `calc()` expressions
- `opacity`
- Google Fonts (auto-embedded by WeasyPrint)
- `@font-face` with base64-encoded fonts
- `::first-line` pseudo-element (WeasyPrint 67+)
- CSS layers (WeasyPrint 67+)
- Grid layout page breaks (WeasyPrint 67+)

### Not Safe (Will Be Ignored or Break)
- `backdrop-filter`
- `position: fixed` / `position: sticky`
- CSS animations / transitions
- `filter: blur()` and other filter functions
- `mix-blend-mode`
- `mask-image`
- JavaScript (no scripting in WeasyPrint)
- `@media` queries based on viewport width (use `@media print` instead)

## Brand Kit CSS Variables

bangerpdf starter packs use CSS variables injected from `brand-kit.yaml`:
```css
:root {
    --primary: #2B5EA7;
    --accent: #F5A623;
    --neutral-dark: #1A1A1A;
    --neutral-light: #F7F7F7;
    --body-font: 'Inter', sans-serif;
    --heading-font: 'Inter', sans-serif;
}

h1, h2, h3 { color: var(--primary); font-family: var(--heading-font); }
body { color: var(--neutral-dark); font-family: var(--body-font); }
.accent-bar { background: var(--accent); }
```

Edit `brand-kit.yaml` and re-run `bangerpdf build` to rebrand the entire pack. No template edits needed.

## Page Break Controls
```css
/* Force a page break before this element */
.page-break {
    page-break-before: always;
    break-before: page;
}

/* Keep content together (don't split across pages) */
.no-break {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Keep a heading with its first paragraph */
h2 {
    page-break-after: avoid;
    break-after: avoid;
}

/* Keep table rows together */
tr { break-inside: avoid; }
```

## Print Color Forcing
Always include this to prevent browsers/renderers from stripping backgrounds:
```css
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
}
```

bangerpdf's `convert` command auto-injects this if missing.

## PyMuPDF QA Patterns

The bangerpdf QA checker uses PyMuPDF (`import fitz`) to inspect rendered PDFs.

### Extracting Text Blocks with Bounding Boxes
```python
import fitz
doc = fitz.open("output.pdf")
for page in doc:
    page_dict = page.get_text("dict")
    for block in page_dict["blocks"]:
        if block["type"] == 0:  # text block
            x0, y0, x1, y1 = block["bbox"]
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    font = span["font"]
                    size = span["size"]
```

### Checking Font Embedding
```python
for page in doc:
    for font_tuple in page.get_fonts():
        xref, ext, type_, basefont, name, encoding = font_tuple[:6]
        is_embedded = bool(ext)  # empty string = not embedded
```

### Checking Links
```python
for page in doc:
    for link in page.get_links():
        uri = link.get("uri")  # external URL
        # page.get_links() also returns internal links (page refs)
```

### Page Geometry (Bleed Check)
```python
page = doc[0]
mediabox = page.mediabox   # full sheet including bleed
trimbox = page.trimbox     # where the cut happens
# Difference = bleed area
```

## WeasyPrint 68.1 Feature Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| @page size, margins | Full support | Named sizes (letter, A4) + custom |
| @page :first/:left/:right/:blank | Full support | All pseudo-class selectors work |
| Margin boxes (16 positions) | Full support | Headers/footers via CSS |
| `counter(page)` / `counter(pages)` | Full support | "Page X of Y" in margin boxes |
| `marks: crop cross` | Full support | For digital-press tier |
| `bleed:` property | Full support | Standard 0.125in for print |
| Named pages | Limited | Prefer pseudo-class selectors instead |
| Min/max on margin boxes | Not supported | Don't use responsive sizing in headers |
| PDF/A (1a through 4f) | v67+ | For archival compliance |
| PDF/X-4 | v67+ | For commercial print interchange |
| CMYK color output | v67+ | Native, no Ghostscript needed |
| PDF/UA accessibility | v67+ | Structural tagging |
| Flexbox | Full support | Preferred layout method |
| CSS Grid | Full support | Page breaks respected (v67+) |
| Google Fonts | Auto-download | Embedded automatically |
| `calc()` | Full support | v67+ |
| CSS layers | Full support | v67+ |

## Typography Best Practices for Print

- Use `pt` for font sizes (not `px`). 1pt = 1/72 inch.
- Body text: 10-11pt for letter size, 9-10pt for A4
- Headings: 14-24pt depending on hierarchy
- Line height: 1.4-1.6 for body, 1.2 for headings
- Paragraph spacing: 0.5em-1em margin-bottom
- Use `in` or `mm` for page dimensions and margins
- Prefer Inter, Helvetica Neue, or system fonts for maximum compatibility
- For branded work, use Google Fonts (WeasyPrint auto-embeds them)
