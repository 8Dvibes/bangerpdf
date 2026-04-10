# bangerpdf Layout Patterns

Tested, copy-pasteable HTML+CSS layout snippets for WeasyPrint. Each file is a self-contained pattern that renders correctly in WeasyPrint without external dependencies.

## What Are Patterns?

Patterns are battle-tested building blocks extracted from real production PDFs (like the Carhartt Company Gear bid package). They solve specific WeasyPrint layout challenges that are hard to figure out from scratch -- flex-wrap pagination bugs, background-image clipping at page boundaries, color-stripping on print backgrounds, and more.

## How to Use

1. **Reference from templates:** Copy the HTML structure and CSS into your template. Patterns are designed to be composable -- mix and match them within a single document.
2. **Agent reads for layout inspiration:** When bangerpdf's agent needs to build a layout, it reads the relevant pattern file to get the exact CSS that works.
3. **CLI access:** `bangerpdf patterns list` shows all available patterns. `bangerpdf patterns show <name>` displays the full pattern.

## CSS Custom Properties

All patterns use CSS custom properties so they adapt to any brand-kit.yaml:

| Variable | Purpose | Typical Value |
|----------|---------|---------------|
| `--primary` | Primary brand color | `#B77729` |
| `--accent` | Accent / highlight color | `#F5A600` |
| `--dark` | Near-black for text and dark backgrounds | `#1A1A1A` |
| `--cream` | Warm light background | `#F5F1EB` |
| `--surface` | Card / elevated surface background | `#FDFAF5` |
| `--neutral-mid` | Secondary text, captions | `#5C5C5C` |
| `--neutral-border` | Borders, dividers | `#D4C5B0` |

Set these in your `:root` block or brand-kit.yaml and all patterns inherit the palette automatically.

## Pattern Index

| File | Best Vibe | Description |
|------|-----------|-------------|
| `hero-fullbleed.html` | Bold | Full-page hero with background image, gradient overlay, white text at bottom |
| `hero-gradient.html` | Corporate, Minimal | Hero section with pure CSS gradient background, no image needed |
| `product-grid-2col.html` | Bold | 2x2 product cards using explicit row containers (fixes WeasyPrint flex-wrap) |
| `product-grid-3col.html` | Bold, Editorial | 3-column product strip for wider layouts or smaller cards |
| `stats-bar.html` | Bold, Corporate | Horizontal bar with 3-5 key metrics, dark or light variant |
| `tier-cards.html` | Bold, Corporate | 3 pricing tier cards, middle card featured with accent badge |
| `timeline-vertical.html` | Corporate, Bold | Vertical milestones as styled table or visual dot-line timeline |
| `two-column-text.html` | Corporate, Bold | Side-by-side text columns for paired content (Clarifications / Exclusions) |
| `lifestyle-divider.html` | Bold | Full-width image with gradient overlay and text, visual section break |
| `signature-block.html` | All | Dual-column signature area, never splits across pages |
| `cover-page-photo.html` | Bold, Editorial | Full-bleed cover page with background photo, logo, title, date |
| `cover-page-minimal.html` | Minimal, Corporate | Text-only cover page with maximum whitespace and subtle accent |
| `callout-box.html` | All | Accent-bordered callout with label; default, gold, and dark variants |
| `table-styled.html` | All | Professional table with section headers, subtotals, and grand total row |
| `info-cards.html` | All | Side-by-side info cards for metadata (Submitted To / Submitted By) |

## WeasyPrint Notes

Key lessons baked into these patterns:

- **Use `<img>` not `background-image`** for images that span page boundaries. WeasyPrint clips CSS backgrounds at page edges.
- **Use explicit row containers** instead of `flex-wrap` for grids. WeasyPrint does not paginate flex-wrapped content correctly.
- **Always set `print-color-adjust: exact`** on elements with background colors. Without it, WeasyPrint may strip backgrounds during rendering.
- **Use named `@page` rules** with zero margins for full-bleed pages. The `page: <name>` CSS property on a container triggers the named page rule.
- **Set `page-break-inside: avoid`** on atomic elements (cards, signatures, callouts, table rows) to prevent them from splitting across pages.
