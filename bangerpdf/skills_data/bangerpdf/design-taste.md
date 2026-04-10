# bangerpdf -- Design Taste Reference

Read this before generating any PDF. Every rule here is load-bearing. Violate them and you get PDF slop.

## 1. Layout & Spatial System

All spacing is multiples of 4pt. No exceptions.

| Token | Value | Use |
|-------|-------|-----|
| `--space-xs` | 4px | Icon padding, inline gaps |
| `--space-s` | 8px | Tight element spacing, list item gaps |
| `--space-m` | 16px | Paragraph spacing, card padding |
| `--space-l` | 24px | Section gaps, group padding |
| `--space-xl` | 32px | Major section breaks |
| `--space-xxl` | 48px | Page section dividers |
| `--space-xxxl` | 64px | Cover page vertical rhythm |

**Proximity rule:** space between groups = 2x space within groups. If items inside a card are 8px apart, cards themselves are 16px apart.

**Whitespace floor:** minimum 40% of any page must be whitespace. When in doubt, remove content rather than shrink spacing.

### Page Margins

| Format | Top | Right | Bottom | Left | Why |
|--------|-----|-------|--------|------|-----|
| US Letter | 1in | 1.5in | 1.25in | 1.5in | Optical centering -- bottom margin larger than top so content doesn't look like it's falling |
| A4 | 20mm | 25mm | 25mm | 25mm | Standard European document margins |

### Grid System

- **12-column grid** for multi-column layouts (proposals, data-heavy reports)
- **Single column** for text-heavy documents (white papers, letters, contracts)
- **Two columns** for proposals with sidebars, data-rich reports
- **Gutter:** minimum 0.25in (6mm), ideal 0.375in (9mm)
- Never use 3+ columns for body text in a PDF. This is not a newspaper.

## 2. Color

### The 60-30-10 Rule

| Proportion | Role | Typical Value |
|------------|------|---------------|
| 60% | Background | White `#FFFFFF` or off-white `#FAFAFA` |
| 30% | Secondary | Headers, sidebars, table stripes, subtle backgrounds |
| 10% | Accent | CTAs, callout borders, key data highlights |

Maximum 3-5 colors total including neutrals.

### Foundation Neutrals

Use these as your neutral palette. Pick one warm and one cool, plus a text color.

| Name | Hex | Use |
|------|-----|-----|
| Soft white | `#FAFAFA` | Page backgrounds, subtle contrast |
| Warm cream | `#F5F0EB` | Sidebar backgrounds, alternate rows |
| Light gray | `#F0F0F0` | Table headers, divider backgrounds |
| Medium gray | `#6B7280` | Secondary text, captions, metadata |
| Charcoal | `#374151` | Subheadings, secondary emphasis |
| Near-black | `#1A1A2E` | Primary text alternative (softer than pure black) |

### Accent Colors

Pick ONE. Do not mix accents.

| Name | Hex | Vibe |
|------|-----|------|
| Teal | `#0D9488` | Modern, trustworthy |
| Cobalt | `#2563EB` | Corporate, tech |
| Sage | `#6B8F71` | Natural, calm |
| Terracotta | `#C2703E` | Warm, approachable |
| Indigo | `#4F46E5` | Premium, creative |
| Slate blue | `#475569` | Conservative, legal |

### Contrast Minimums (WCAG AA)

| Element | Minimum Ratio |
|---------|--------------|
| Body text on white | 4.5:1 |
| Large text (18pt+) on white | 3:1 |
| UI components, borders | 3:1 |

**Body text:** always `#111827` or darker on white backgrounds. Never use a gray lighter than `#374151` for readable body text.

### Semantic Colors

| Meaning | Color | Hex |
|---------|-------|-----|
| Success | Green | `#059669` |
| Warning | Amber | `#D97706` |
| Error | Red | `#DC2626` |
| Info | Blue | `#2563EB` |

Use semantic colors only for their meaning. Green is not a decorative color.

### When to Use Color vs B&W

| Document Type | Color Approach |
|---------------|---------------|
| Contracts, legal, specs | B&W only |
| Invoices | B&W with optional brand accent for header |
| Proposals, marketing | Full brand palette |
| Reports, annual reports | Brand palette + data viz colors |
| Certificates | Brand accent, restrained |
| Letters | B&W with brand letterhead color |

## 3. Typography

### Type Scale (Perfect Fourth -- 1.333 ratio)

| Level | Size | Weight | Line Height | Use |
|-------|------|--------|-------------|-----|
| Body | 11pt | 400 | 1.45 | All paragraph text |
| Small | 9pt | 400 | 1.3 | Captions, footnotes, legal |
| H4 | 11pt | 600 | 1.3 | Inline headings, labels |
| H3 | 15pt | 600 | 1.2 | Subsection headings |
| H2 | 19pt | 700 | 1.15 | Section headings |
| H1 | 26pt | 700 | 1.1 | Page titles |
| Display | 34pt | 800 | 1.05 | Cover page title only |

### Font Pairing Rules

- **Maximum 2 fonts.** One for headings, one for body. Using the same font with weight variation counts as one.
- **3 fonts is the absolute ceiling** and only justified when a monospace font is needed for data/code.
- Weight variation within a single family is always safe.

### Recommended Pairings (Open Source, Google Fonts)

| Heading | Body | Vibe |
|---------|------|------|
| Montserrat | Merriweather | Modern corporate |
| Inter | Inter (weight variation) | Clean tech, SaaS |
| Playfair Display | Source Sans Pro | Editorial, premium |
| Libre Baskerville | Open Sans | Authoritative, legal |
| DM Sans | DM Sans (weight variation) | Friendly, startup |

### Line Length

- **Target:** 66 characters per line
- **Acceptable range:** 45-75 characters
- Lines shorter than 45 chars feel choppy. Lines longer than 75 chars cause eye fatigue.
- For two-column layouts, 45-55 chars per column is fine.

### Letter Spacing

| Context | Letter Spacing |
|---------|---------------|
| Body text | 0 (normal) |
| ALL CAPS text | +0.05em to +0.1em |
| Large headings (26pt+) | -0.01em to -0.02em |

### Alignment and Formatting

- **Left-align** all body text. Justified only with `hyphens: auto` enabled (prevents rivers).
- Set `orphans: 3; widows: 3;` in CSS. Always.
- No underlines except hyperlinks. Use **bold** or *italic* for emphasis.
- Smart quotes (`"..."`, `'...'`), not straight quotes. Em dashes (`---`), not double hyphens.

## 4. Visual Assets

### Data Visualization

| Chart Type | When to Use | When NOT to Use |
|------------|-------------|-----------------|
| Bar | Comparing categories | More than 12 categories |
| Line | Trends over time | Fewer than 3 data points |
| Pie | Parts of a whole (3-5 slices) | More than 5 slices, or slices < 5% |
| Table | Exact values matter | More than ~20 rows on one page |
| Stacked bar | Composition + comparison | More than 5 segments |

**Data-ink ratio:** remove gridlines, 3D effects, shadows, textures, gradient fills. Every pixel of ink should represent data.

Label data directly on or next to the element. Minimize legends -- if you need a legend with more than 5 items, the chart is too complex.

Every chart or figure MUST be referenced in the body text. No orphan visuals.

### Images

- **Resolution:** 300 DPI minimum for print tiers; 150 DPI acceptable for desktop tier
- **Format:** JPG for photos, PNG for screenshots/diagrams, SVG for logos/icons
- Never rasterize a logo. SVG always.
- Maintain aspect ratios. Never stretch or squish.
- **Consistency rule:** if one image has rounded corners (`border-radius`), ALL images in the document do. If one has a shadow, all do. Mixed treatments look broken.

### Dividers and Borders

- Thin rules only: 0.5pt-1pt in a neutral color (`#CBD5E1` or `#E5E7EB`)
- Never thick decorative borders
- Background shapes: subtle, geometric, low-opacity (< 0.1) only
- If you're using a colored sidebar or accent bar, keep it to one edge of the page

## 5. The 12 Deadly Sins (Anti-Slop Checklist)

Run this checklist before finalizing any PDF. Each violation is a quality defect.

| # | Sin | How to Detect |
|---|-----|---------------|
| 1 | 4+ fonts | Count font-family declarations in CSS |
| 2 | Generic stock photography | Any image that could be in any document = wrong image |
| 3 | No spatial system | Spacing values that aren't multiples of 4pt |
| 4 | Gradient/shadow/bevel abuse | Any `box-shadow` deeper than 4px, any gradient on text |
| 5 | Walls of text without hierarchy | Any text block > 6 lines with no heading, list, or visual break |
| 6 | Everything is "important" | More than 3 bold/colored/callout elements per page |
| 7 | Low-res or stretched images | Image natural size < rendered size, or aspect ratio distorted |
| 8 | Purposeless decoration | Any element that doesn't inform or guide the reader |
| 9 | Inconsistent page styling | Different heading sizes, colors, or spacing on different pages |
| 10 | Off-grid alignment | Elements that are close to aligned but not snapped to the grid |
| 11 | Zero whitespace | Less than 40% whitespace on a page; margins < 0.75in |
| 12 | Unmodified template feel | Default placeholder text, stock colors, no brand customization |

## 6. The Vibe Check Process

Before writing any HTML/CSS for a PDF, complete these steps in order:

1. **Identify the document type** (proposal, invoice, report, etc.) and look up its pattern in Section 7.
2. **Lock the system** -- choose type scale, spacing scale, and color palette. Write them as CSS variables FIRST.
3. **Set up `@page` rules** -- size, margins, margin boxes (headers/footers), bleed if needed.
4. **Build from the system** -- every `font-size`, `margin`, `padding`, and `color` value must reference a CSS variable or the type scale. Zero ad-hoc values.
5. **Squint test** -- zoom out to 25%. Can you see the heading hierarchy? Can you tell sections apart? If not, increase contrast between levels.
6. **Earn-your-place audit** -- look at every element. Does it inform the reader or guide their eye? If not, delete it.
7. **Constraint = quality.** Fewer colors, fewer fonts, more whitespace. When tempted to add, subtract instead.

## 7. Document Type Patterns

### Proposals

- Full-bleed cover page with brand color, logo, and title
- Executive summary on page 2, fits on ONE page, scannable via bullet points
- Interior pages: generous margins, clear heading hierarchy, sidebars for key stats
- Scope, timeline, and pricing in their own sections with distinct visual treatment
- Final page: next steps / CTA, contact info

### Reports

- Grid-based layout, modular sections
- Consistent chart language throughout (same colors, same label style, same axis treatment)
- Table of contents for 5+ pages
- Page numbers and section headers in margin boxes
- Data-heavy pages: two-column with charts; narrative pages: single column

### Invoices

- B&W default. Brand accent for header bar only.
- Visual hierarchy: "INVOICE" label and total amount are the two most prominent elements
- Z-pattern scan path: company info top-left, invoice # top-right, line items center, total bottom-right
- No decorative elements. Clean table, clear numbers, right-aligned currency.

### One-Pagers

- Single page, no page break
- Clear visual hierarchy: headline > subhead > 3-4 key points > CTA
- Brand accent used on 1-2 elements max (header bar, CTA button/block)
- Balance text and whitespace -- if it feels crowded, cut content

### Certificates

- Centered layout, generous margins (minimum 1.5in all sides)
- Decorative but restrained border (thin line or subtle pattern, not clip-art)
- Recipient name is the largest text on the page
- Date, issuer, and signature below. No clutter.

### Letters

- Traditional letterhead: logo + company info in header, address block
- Conservative font pairing (Libre Baskerville + Open Sans, or similar)
- Single column, 1in-1.5in margins
- Formal spacing: date, recipient address, salutation, body, closing, signature
- No sidebars, no accent bars, no callout boxes

## 8. Vibe System

Four predefined vibes that set the entire design direction. Pick one during the design interview. Each vibe defines fonts, palette, spacing, decoration rules, and a CSS override block you drop into your stylesheet.

### Corporate (Clean & Authoritative)

Best for: SaaS proposals, consulting reports, financial documents, government bids.

- **Fonts:** Inter or Helvetica Neue (heading), Inter (body) -- weight variation only, single family feel
- **Palette:** Navy `#1E3A5F` (primary), Steel Blue `#4A7DA8` (secondary), Light Gray `#F0F2F5` (background accent), White `#FFFFFF` (page background)
- **Spacing:** Standard 8pt scale, 1.5" side margins, `--space-l` (24px) between sections
- **Decoration:** Minimal -- thin 0.5pt borders, no gradients, no background images, no rounded corners above 2px
- **Images:** Charts and data visualizations only, no lifestyle photography. Metric cards and tables preferred over generated imagery.

```css
/* Corporate Vibe Override */
:root {
    --color-primary: #1E3A5F;
    --color-accent: #4A7DA8;
    --color-bg: #FFFFFF;
    --color-bg-subtle: #F0F2F5;
    --font-heading: 'Inter', 'Helvetica Neue', sans-serif;
    --font-body: 'Inter', 'Helvetica Neue', sans-serif;
}

@page {
    margin: 1in 1.5in 1.25in 1.5in;
}

h1, h2, h3 { letter-spacing: -0.01em; }
.callout { border-radius: 2px; }
```

### Bold (Full-Bleed & Visual)

Best for: merch bids, product catalogs, brand pitches, event proposals, look-books.

- **Fonts:** Montserrat or Impact (heading), Source Sans Pro (body) -- high contrast between heading weight and body
- **Palette:** Deep brand primary + high-contrast accent, dark backgrounds (`#111827` or darker) for hero sections, bright accent for CTAs
- **Spacing:** Generous -- `--space-xxxl` (64px) between major sections, full-bleed hero pages with zero margins
- **Decoration:** Background images with gradient overlays, accent bars (4-8pt), product grids, lifestyle photography sections
- **Images:** Lifestyle photography, product shots, generated mockups -- REQUIRED, not optional. Minimum 1 hero + 1 product grid.

```css
/* Bold Vibe Override */
:root {
    --color-primary: #111827;
    --color-accent: #F59E0B;
    --color-bg: #FFFFFF;
    --color-bg-subtle: #F9FAFB;
    --font-heading: 'Montserrat', 'Impact', sans-serif;
    --font-body: 'Source Sans Pro', sans-serif;
}

@page {
    margin: 0.75in 1in 1in 1in;
}

/* Full-bleed hero pages: name the page, zero out margins */
@page full-bleed {
    margin: 0;
}

.hero-page { page: full-bleed; }

.hero-section {
    background-size: cover;
    background-position: center;
    min-height: 100vh;
    display: flex;
    align-items: flex-end;
    padding: var(--space-xxxl);
}

.hero-overlay {
    background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 60%);
    position: absolute;
    inset: 0;
}

h1 {
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
```

### Editorial (Refined & Magazine)

Best for: consulting white papers, annual reports, thought leadership, luxury brand materials.

- **Fonts:** Playfair Display or Libre Baskerville (heading), Source Serif Pro or Merriweather (body) -- serif pairing, classic and refined
- **Palette:** Warm neutrals -- Cream `#F5F0EB` (background), Charcoal `#2D2D2D` (text), one muted accent (Sage `#6B8F71` or Terracotta `#C2703E`)
- **Spacing:** Extra generous -- 50%+ whitespace per page, wide margins (2" sides), `--space-xxl` (48px) minimum between sections
- **Decoration:** Pull quotes with large italic type, thin horizontal rules (0.5pt), large drop caps on chapter openers, generous leading (1.6+)
- **Images:** Selective, high-quality, editorial treatment -- desaturated, cropped tight, never more than 2 per spread

```css
/* Editorial Vibe Override */
:root {
    --color-primary: #2D2D2D;
    --color-accent: #6B8F71;
    --color-bg: #FFFFFF;
    --color-bg-subtle: #F5F0EB;
    --font-heading: 'Playfair Display', 'Libre Baskerville', serif;
    --font-body: 'Source Serif Pro', 'Merriweather', serif;
}

@page {
    margin: 1in 2in 1.25in 2in;
}

body { line-height: 1.6; }

h1 {
    font-weight: 700;
    font-style: italic;
    letter-spacing: -0.02em;
}

/* Pull quote */
blockquote {
    font-family: var(--font-heading);
    font-size: var(--text-h3);
    font-style: italic;
    color: var(--color-accent);
    border: none;
    padding: var(--space-xl) 0;
    margin: var(--space-xxl) 0;
    border-top: 0.5pt solid var(--color-border);
    border-bottom: 0.5pt solid var(--color-border);
}

/* Drop cap */
.chapter-opener p:first-of-type::first-letter {
    font-family: var(--font-heading);
    font-size: 3.5em;
    float: left;
    line-height: 0.8;
    margin-right: 0.08em;
    color: var(--color-primary);
}
```

### Minimal (Ultra-Clean)

Best for: freelancer invoices, contracts, simple letters, developer docs, internal memos.

- **Fonts:** Inter or SF Pro (heading and body) -- single font family, weight variation only
- **Palette:** White `#FFFFFF`, Near-black `#111111` (text), ONE accent color only (pick from brand or use `#2563EB`)
- **Spacing:** Maximum whitespace, 2"+ side margins, sparse content per page, `--space-xxl` (48px) between even minor sections
- **Decoration:** Almost none -- no borders, no background colors, no shadows. Maybe one thin horizontal rule per page. Let whitespace be the design element.
- **Images:** None, or one hero image only. If the page looks empty, it is working correctly.

```css
/* Minimal Vibe Override */
:root {
    --color-primary: #111111;
    --color-accent: #2563EB;
    --color-bg: #FFFFFF;
    --color-bg-subtle: #FFFFFF;
    --color-border: transparent;
    --font-heading: 'Inter', system-ui, sans-serif;
    --font-body: 'Inter', system-ui, sans-serif;
}

@page {
    margin: 1.25in 2in 1.5in 2in;
}

h1 { font-weight: 600; }
h2, h3 { font-weight: 500; color: var(--color-primary); }

.callout {
    background: transparent;
    border-left: 2pt solid var(--color-accent);
    padding-left: var(--space-m);
}

table { border-collapse: collapse; }
thead th { background: transparent; border-bottom: 1pt solid #111; }
td { border-bottom: 0.5pt solid #E5E7EB; }
tbody tr:nth-child(even) { background: transparent; }
```

## 9. Page Flow Rules

How content flows across pages matters as much as how it looks on any single page.

### Heading Protection
- Never let a heading sit alone in the bottom 20% of a page. If a heading lands there, break BEFORE it so it starts the next page.
- If a section (heading + first paragraph) cannot fit in the remaining space on the current page, break BEFORE the heading. A lonely heading with no body text following it is a layout defect.
- CSS enforcement: `h1, h2, h3 { page-break-after: avoid; break-after: avoid; orphans: 3; widows: 3; }`

### Reading Rhythm
- Alternate dense and sparse pages. Do not cram every page to capacity -- readers need visual breathing room.
- After a data-heavy page (tables, charts, dense text), follow with a page that has more whitespace or a visual element.
- Full-bleed hero/imagery pages serve as "palate cleansers" between content sections.

### Content Integrity
- Tables, card grids, and signature blocks: always `page-break-inside: avoid; break-inside: avoid;`. These elements must never split across pages.
- If a table is too tall for one page, split it into logical groups with repeated headers using explicit row containers, not `flex-wrap`.
- Callout boxes and blockquotes: keep them atomic. If one does not fit on the current page, push the whole thing to the next page.

### Whitespace Audit
- After building, scan every page: does any non-hero page have >60% whitespace with no imagery? If so, consolidate content from adjacent pages to fill the gap. Empty space without purpose looks like a bug.
- Exception: editorial and minimal vibes intentionally run 50%+ whitespace. The audit threshold for those vibes is 75%.

### Section Transitions
- Use explicit `page-break-before: always` on major section transitions (cover to body, executive summary to detailed scope, pricing to terms). Do not break before every subsection.
- Within a section, let content flow naturally. Only force breaks when the next subsection is a clear topic shift.

### Special Element Rules
- Premium product callouts (like a featured vest or flagship item) should NEVER be alone on a page -- keep them with their product grid or adjacent content.
- Signature blocks belong at the bottom of their page, not at the top of a new page. Use `margin-top: auto` in a flex column to push them down.
- Page numbers, headers, and footers go in `@page` margin boxes, never in the HTML body flow.

## 10. CSS Quick Reference

Copy this as a starting point. Override the CSS variable values per project.

```css
/* ============================================================
   bangerpdf — Base Design System
   ============================================================ */

/* --- Page Setup --- */
@page {
    size: letter;
    margin: 1in 1.5in 1.25in 1.5in; /* top right bottom left */

    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 8pt;
        font-family: var(--font-body);
        color: var(--color-muted);
        border-top: 0.5pt solid var(--color-border);
        padding-top: 6pt;
    }
}

@page :first {
    margin-top: 0;
    margin-bottom: 0;
    @bottom-center { content: none; }
}

/* --- Color Palette --- */
:root {
    /* Brand — override per project */
    --color-primary: #2563EB;
    --color-accent: #0D9488;

    /* Neutrals */
    --color-bg: #FFFFFF;
    --color-bg-subtle: #FAFAFA;
    --color-bg-muted: #F0F0F0;
    --color-text: #111827;
    --color-text-secondary: #374151;
    --color-muted: #6B7280;
    --color-border: #E5E7EB;
    --color-border-strong: #CBD5E1;

    /* Semantic */
    --color-success: #059669;
    --color-warning: #D97706;
    --color-error: #DC2626;
    --color-info: #2563EB;
}

/* --- Typography --- */
:root {
    --font-heading: 'Inter', 'Helvetica Neue', sans-serif;
    --font-body: 'Inter', 'Helvetica Neue', sans-serif;

    /* Perfect Fourth scale (1.333) from 11pt base */
    --text-display: 34pt;
    --text-h1: 26pt;
    --text-h2: 19pt;
    --text-h3: 15pt;
    --text-body: 11pt;
    --text-small: 9pt;
}

/* --- Spacing Scale (4pt base) --- */
:root {
    --space-xs: 4px;
    --space-s: 8px;
    --space-m: 16px;
    --space-l: 24px;
    --space-xl: 32px;
    --space-xxl: 48px;
    --space-xxxl: 64px;
}

/* --- Print Color Forcing --- */
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
}

/* --- Base Elements --- */
body {
    font-family: var(--font-body);
    font-size: var(--text-body);
    line-height: 1.45;
    color: var(--color-text);
    background: var(--color-bg);
    orphans: 3;
    widows: 3;
}

h1, h2, h3, h4 {
    font-family: var(--font-heading);
    color: var(--color-primary);
    page-break-after: avoid;
    break-after: avoid;
    margin-top: 0;
}

h1 {
    font-size: var(--text-h1);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.01em;
    margin-bottom: var(--space-l);
}

h2 {
    font-size: var(--text-h2);
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: var(--space-m);
}

h3 {
    font-size: var(--text-h3);
    font-weight: 600;
    line-height: 1.2;
    margin-bottom: var(--space-s);
}

h4 {
    font-size: var(--text-body);
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: var(--space-xs);
}

p {
    margin: 0 0 var(--space-m) 0;
    max-width: 38em; /* ~66 chars at 11pt */
}

/* --- Tables --- */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--text-body);
    margin-bottom: var(--space-l);
}

thead th {
    background: var(--color-bg-muted);
    font-weight: 600;
    text-align: left;
    padding: var(--space-s) var(--space-m);
    border-bottom: 1.5pt solid var(--color-border-strong);
    font-size: var(--text-small);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-secondary);
}

td {
    padding: var(--space-s) var(--space-m);
    border-bottom: 0.5pt solid var(--color-border);
    vertical-align: top;
}

tr {
    break-inside: avoid;
}

/* Zebra striping */
tbody tr:nth-child(even) {
    background: var(--color-bg-subtle);
}

/* --- Callout Box --- */
.callout {
    background: var(--color-bg-subtle);
    border-left: 3pt solid var(--color-primary);
    padding: var(--space-m);
    margin: var(--space-l) 0;
    border-radius: 2px;
    break-inside: avoid;
}

.callout-warning {
    border-left-color: var(--color-warning);
}

.callout-error {
    border-left-color: var(--color-error);
}

.callout-success {
    border-left-color: var(--color-success);
}

/* --- Lists --- */
ul, ol {
    padding-left: var(--space-l);
    margin: 0 0 var(--space-m) 0;
}

li {
    margin-bottom: var(--space-xs);
    line-height: 1.45;
}

li + li {
    margin-top: var(--space-xs);
}

/* --- Dividers --- */
hr {
    border: none;
    border-top: 0.5pt solid var(--color-border);
    margin: var(--space-xl) 0;
}

/* --- Page Break Utilities --- */
.page-break {
    page-break-before: always;
    break-before: page;
}

.no-break {
    page-break-inside: avoid;
    break-inside: avoid;
}

.keep-with-next {
    page-break-after: avoid;
    break-after: avoid;
}

/* --- Cover Page --- */
.cover {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    padding: var(--space-xxxl);
}

.cover h1 {
    font-size: var(--text-display);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: var(--color-primary);
}

.cover .subtitle {
    font-size: var(--text-h3);
    color: var(--color-text-secondary);
    margin-top: var(--space-m);
}

/* --- Accent Bar (top of page) --- */
.accent-bar {
    background: var(--color-primary);
    height: 4pt;
    width: 100%;
    margin-bottom: var(--space-l);
}

/* --- Key-Value / Metadata --- */
.meta-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--space-xs) var(--space-l);
    font-size: var(--text-small);
    color: var(--color-muted);
    margin-bottom: var(--space-l);
}

.meta-grid dt {
    font-weight: 600;
    color: var(--color-text-secondary);
}
```

### A4 Override

```css
@page {
    size: A4;
    margin: 20mm 25mm 25mm 25mm;
}
```

### Commercial Print Override

```css
@page {
    bleed: 0.125in;
    marks: crop cross;
}
```
