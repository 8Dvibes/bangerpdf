---
name: bangerpdf/weasyprint-cookbook
description: >
  Tested solutions for every common WeasyPrint layout pitfall. Consult this
  when a PDF renders with broken layouts, empty pages, split sections, or
  mispositioned elements. Each recipe includes the broken CSS, what goes wrong,
  and the tested fix.
---

# bangerpdf -- WeasyPrint Cookbook

WeasyPrint is excellent at turning HTML/CSS into PDFs. It is not a browser. It has specific pagination behaviors, layout constraints, and rendering quirks that will bite you if you write CSS as if you are building a web page. Every recipe in this cookbook was discovered the hard way -- in production builds where something looked perfect in Chrome and broke in the PDF.

Consult this file whenever a PDF renders with:
- Empty or mostly-blank pages
- Content split across pages in wrong places
- Background images clipped or missing
- Footers floating in the middle of pages
- Grids and flex layouts collapsing
- Fonts rendering as fallbacks

## Recipe 1: flex-wrap Creates Empty Pages

### Problem
You use `flex-wrap: wrap` on a container with many children (product cards, team members, feature blocks). The PDF renders with empty pages between rows of content.

### What Happens
WeasyPrint treats a `flex-wrap: wrap` container as a single block for pagination purposes. When the wrapped content exceeds one page, WeasyPrint tries to fit the entire container, fails, then creates awkward page breaks inside the flex context. Wrapped rows do not cleanly break across pages -- they leave empty space.

### Broken CSS
```css
/* DO NOT DO THIS for paginated content */
.product-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 14pt;
}

.product-card {
  flex: 0 0 calc(50% - 7pt);
  /* 20 cards in a wrapped flex container = chaos */
}
```

### Fixed CSS
```css
/* Use explicit row containers instead of flex-wrap */
.product-grid {
  /* No display:flex here -- this is just a wrapper */
  margin: 12pt 0;
}

.product-row {
  display: flex;
  gap: 14pt;
  margin-bottom: 14pt;
  page-break-inside: avoid;
}

.product-card {
  flex: 1;
  page-break-inside: avoid;
}
```

### Fixed HTML
```html
<!-- Pair cards into explicit rows in your template -->
<div class="product-grid">
  <div class="product-row">
    <div class="product-card">Card 1</div>
    <div class="product-card">Card 2</div>
  </div>
  <div class="product-row">
    <div class="product-card">Card 3</div>
    <div class="product-card">Card 4</div>
  </div>
</div>
```

### Why It Works
Each `.product-row` is an independent flex container that fits on a single line. WeasyPrint can place page breaks *between* rows but does not need to break *inside* a row. The `page-break-inside: avoid` on the row keeps each pair of cards together.

**Rule of thumb:** If your flex container will wrap, break it into explicit row `<div>` elements in your template or Jinja2 loop. Use `{% if loop.index is divisibleby(2) %}` to close and reopen rows.

---

## Recipe 2: page-break-inside: avoid on Large Containers

### Problem
You put `page-break-inside: avoid` on a section container that spans more than 60% of the page height. WeasyPrint moves the entire section to the next page, leaving a massive blank space on the previous page.

### What Happens
`page-break-inside: avoid` is a suggestion, but WeasyPrint respects it aggressively. If the container exceeds about 60% of the available page height, WeasyPrint will push it to the next page rather than split it. This leaves a half-empty page that looks like a rendering bug.

### Broken CSS
```css
/* DO NOT DO THIS on tall sections */
.scope-section {
  page-break-inside: avoid;
  /* This section has a heading, 3 paragraphs, and a table.
     It's 70% of the page. Result: empty half-page above it. */
}
```

### Fixed CSS
```css
/* Apply avoid-break only to SMALL elements within the section */
.scope-section h2 {
  page-break-after: avoid;  /* Keep heading with first paragraph */
}

.scope-section .callout {
  page-break-inside: avoid;  /* Small callout box -- safe to keep together */
}

.scope-section table tr {
  page-break-inside: avoid;  /* Keep table rows intact */
}

/* Let the section itself break naturally */
.scope-section {
  /* No page-break-inside: avoid here */
}
```

### Why It Works
Applying `avoid` to small, atomic elements (headings, callout boxes, table rows) gives WeasyPrint the flexibility to break between those elements while keeping each one intact. The section flows naturally across pages without leaving blank holes.

**Rule of thumb:** Only use `page-break-inside: avoid` on elements shorter than ~60% of the page content area. For everything else, apply it to the children, not the parent.

---

## Recipe 3: Background Images Clipped at Page Break

### Problem
A section has a CSS `background-image`. When the section spans a page break, the background image is clipped at the break -- it shows on the first page but not on the second.

### What Happens
WeasyPrint clips background images at the element boundary. If the element's box starts on page 1 and continues on page 2, the background only renders on the portion of the box that fits on page 1. This is per the CSS spec for paged media, but it is visually broken for full-bleed or decorative backgrounds.

### Broken CSS
```css
/* DO NOT USE background-image on elements that might span pages */
.hero-section {
  background-image: url('assets/hero.png');
  background-size: cover;
  background-position: center;
  padding: 48pt;
  /* If this section is tall enough to span pages, the bg clips. */
}
```

### Fixed CSS + HTML
```css
/* Use an <img> tag with absolute positioning instead */
.hero-section {
  position: relative;
  overflow: hidden;
  page-break-inside: avoid; /* Force it to stay on one page */
}

.hero-section-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-section-content {
  position: relative;
  z-index: 2;
  padding: 48pt;
}
```

```html
<div class="hero-section">
  <img src="assets/hero.png" class="hero-section-bg" alt="">
  <div class="hero-section-content">
    <h1>Section Title</h1>
    <p>Content goes here.</p>
  </div>
</div>
```

### Why It Works
An `<img>` tag is a content element, not a background. WeasyPrint embeds it as an actual image in the PDF. Combined with `page-break-inside: avoid`, the entire section (including the image) stays on one page. For full-bleed cover pages, this is the canonical pattern -- see the Carhartt bid's `hero-cover` class for a production example.

**For full-bleed covers specifically:** Set the containing `<div>` to `width: 8.5in; height: 11in;` with `page: full-bleed;` (a named @page rule with `margin: 0`). The image fills the entire physical page.

---

## Recipe 4: Footer Not at Page Bottom

### Problem
You want a footer at the bottom of every page but CSS `position: fixed` does not work in WeasyPrint. You try `margin-top: auto` or `position: absolute; bottom: 0` and the footer ends up in the wrong place.

### What Happens
WeasyPrint does not support `position: fixed` or `position: sticky`. These are browser-only features for viewport-relative positioning. In paged media, there is no viewport -- there are pages. Absolute positioning works relative to the containing block, but in a paginated context, the containing block's bottom edge might not be where you expect.

### Broken CSS
```css
/* NONE OF THESE WORK in WeasyPrint */
.footer { position: fixed; bottom: 0; }
.footer { position: sticky; bottom: 0; }
.footer { position: absolute; bottom: 0; } /* Only works in specific contexts */
```

### Fixed CSS
```css
/* Use @page margin boxes for true page footers */
@page {
  margin-bottom: 0.8in;

  @bottom-center {
    content: "Wilson Mechanical  |  Confidential";
    font-family: 'Helvetica Neue', sans-serif;
    font-size: 7pt;
    color: #6B7280;
    border-top: 0.5pt solid #E5E7EB;
    padding-top: 6pt;
  }

  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-family: 'Helvetica Neue', sans-serif;
    font-size: 7pt;
    color: #6B7280;
  }
}

/* Suppress footer on full-bleed pages */
@page full-bleed {
  margin: 0;
  @bottom-center { content: none; }
  @bottom-right { content: none; }
}
```

### Why It Works
`@page` margin boxes are the CSS Paged Media mechanism for page headers and footers. They are rendered by WeasyPrint on every page automatically, positioned correctly in the page margin area. They support `counter(page)` and `counter(pages)` for page numbers. Named @page rules let you suppress them selectively (cover pages, full-bleed sections).

**Limitation:** Margin box content is limited to strings and counters. You cannot put complex HTML in a margin box. For rich footers with logos or multi-line content, use a repeated element at the bottom of each template section and manage the spacing manually.

---

## Recipe 5: Full-Bleed Pages Mixed with Content Pages

### Problem
Your document has a full-bleed cover page (no margins, image edge-to-edge) followed by content pages with normal margins and footers. The margins from the content pages bleed into the cover page, or vice versa.

### What Happens
Without named @page rules, all pages share the same `@page` definition. If you set `margin: 0` for the cover, content pages lose their margins. If you set margins for content, the cover gets margins that clip the full-bleed image.

### Broken CSS
```css
/* This applies to ALL pages */
@page { margin: 0; }  /* Cover looks great, content pages are margin-less */
/* OR */
@page { margin: 0.6in 0.7in; }  /* Content is fine, cover has white bars */
```

### Fixed CSS
```css
/* Named @page rules for different page types */
@page {
  size: Letter;
  margin: 0;  /* Default: no margin (for unlabeled pages) */
}

@page content-page {
  margin: 0.6in 0.7in 0.8in 0.7in;

  @bottom-right {
    content: counter(page);
    font-family: var(--font-family);
    font-size: 7pt;
    color: #6B7280;
  }
}

@page full-bleed {
  margin: 0;
  @bottom-center { content: none; }
}

/* Assign pages via the `page` CSS property */
.hero-cover { page: full-bleed; }
.content-page { page: content-page; }
.lifestyle-spread { page: full-bleed; }
```

```html
<div class="hero-cover">
  <!-- Full-bleed cover: no margins, image fills 8.5x11 -->
</div>

<div class="content-page">
  <!-- Normal content: margins, page numbers, footer -->
</div>

<div class="lifestyle-spread">
  <!-- Mid-document full-bleed image: no margins again -->
</div>

<div class="content-page">
  <!-- Back to normal content -->
</div>
```

### Why It Works
The `page` CSS property assigns an element to a named @page rule. WeasyPrint switches page styles when the `page` value changes. This lets you interleave full-bleed and margined pages in any order. Each page type has its own margin, footer, and page number configuration.

**This is the canonical pattern for bid packages and look-books.** The Carhartt bid uses exactly this: `@page full-bleed` for the cover and lifestyle sections, `@page content-page` for the proposal body.

---

## Recipe 6: Product Grid Renders Single-Column

### Problem
You built a 2-column product grid using `display: grid` or `flex-wrap`, but in the PDF output every card renders in a single column, stacked vertically.

### What Happens
Several things can cause single-column collapse in WeasyPrint:
1. `flex-wrap: wrap` with cards wider than 50% (including gap)
2. CSS Grid with `auto-fit`/`auto-fill` and `minmax()` -- WeasyPrint may resolve the available width differently than a browser
3. The container is inside an element with constrained width that you did not expect

### Broken CSS
```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200pt, 1fr));
  gap: 14pt;
}
```

### Fixed CSS
```css
/* Explicit column count, no auto-fill */
.product-row {
  display: flex;
  gap: 14pt;
  margin-bottom: 14pt;
  page-break-inside: avoid;
}

.product-card {
  flex: 1;
  min-width: 0;  /* Prevent flex items from overflowing */
  page-break-inside: avoid;
}
```

### Why It Works
Explicit flex with `flex: 1` on two children always produces two equal columns. No ambiguity about available width, no `auto-fill` resolution differences. The `min-width: 0` prevents flex children from refusing to shrink below their content width.

**Rule of thumb:** For paginated content, prefer explicit flex layouts over CSS Grid with dynamic column counts. If you need 2 columns, put exactly 2 children in a flex row. If you need 3 columns, put 3. Do not rely on the rendering engine to decide column count.

---

## Recipe 7: Table Headers Do Not Repeat

### Problem
A long table spans multiple pages, but the header row only appears on the first page. Subsequent pages show data rows with no column labels.

### What Happens
This is actually a feature you need to opt into. WeasyPrint supports repeating table headers, but you must use semantic `<thead>` markup.

### Broken HTML
```html
<!-- NO thead = no repeating headers -->
<table>
  <tr><th>Item</th><th>Qty</th><th>Amount</th></tr>
  <tr><td>Copper pipe</td><td>500</td><td>$12,000</td></tr>
  <!-- ... 40 more rows ... -->
</table>
```

### Fixed HTML
```html
<table>
  <thead>
    <tr><th>Item</th><th>Qty</th><th>Amount</th></tr>
  </thead>
  <tbody>
    <tr><td>Copper pipe</td><td>500</td><td>$12,000</td></tr>
    <!-- ... 40 more rows ... -->
  </tbody>
</table>
```

### Fixed CSS
```css
thead {
  display: table-header-group;  /* Explicit, though it's the default */
}

thead th {
  background: var(--dark);
  color: white;
  /* ... styling ... */
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}

tr {
  page-break-inside: avoid;  /* Keep rows intact */
}
```

### Why It Works
`<thead>` with `display: table-header-group` tells WeasyPrint to repeat the header row at the top of every page where the table continues. This is standard CSS Paged Media behavior. Without `<thead>`, WeasyPrint has no way to know which rows are headers.

**Bonus:** Add `print-color-adjust: exact` to the `<th>` styles. Without it, the dark background on repeated headers may be stripped by the print color optimization.

---

## Recipe 8: Heading Orphaned from Body

### Problem
A section heading appears at the bottom of a page with no body text following it. The paragraph or list that belongs with the heading is on the next page.

### What Happens
WeasyPrint places the heading at the bottom of the page because it fits. Then a page break occurs, and the body content starts on the next page. This is technically correct pagination but visually broken -- a heading alone at the bottom of a page looks like a mistake.

### Broken CSS
```css
h2 {
  margin: 36pt 0 12pt 0;
  /* No break control -- heading can end up orphaned */
}
```

### Fixed CSS
```css
h1, h2, h3, h4 {
  page-break-after: avoid;
  break-after: avoid;
  /* Both properties for maximum compatibility.
     This tells WeasyPrint: do not place a page break
     immediately after this heading. */
}
```

### Why It Works
`page-break-after: avoid` (and its modern equivalent `break-after: avoid`) tells WeasyPrint that a page break should not occur between this heading and the next element. If the heading is near the bottom of the page and the next element would be on the next page, WeasyPrint moves the heading to the next page too, keeping them together.

**Always apply this to all heading levels.** There is no valid case where a heading should appear alone at the bottom of a page. This should be in your base CSS for every bangerpdf project. The design-taste.md base CSS already includes this.

---

## Recipe 9: Allowances Table Split Across Pages

### Problem
A small table (schedule of values, allowances, pricing summary) gets split across a page break even though it would easily fit on one page if positioned correctly. Half the table is on one page, half on the next.

### What Happens
The table starts partway down the page. There is not enough room for the full table, so WeasyPrint splits it. This is technically correct -- the table does not fit. But visually, a 10-row pricing table split in the middle looks unprofessional.

### Broken CSS
```css
table {
  /* No break control -- table splits wherever the page break falls */
}
```

### Fixed CSS
```css
/* Wrap the table in a no-break container */
.pricing-section {
  page-break-inside: avoid;
  /* ONLY if the table fits on a single page (< ~60% page height) */
}

/* For tables that MUST span pages, keep rows intact */
table {
  width: 100%;
  border-collapse: collapse;
}

tr {
  page-break-inside: avoid;
  break-inside: avoid;
}

/* Keep section-header rows with the next data row */
.sov-section-row {
  page-break-after: avoid;
  break-after: avoid;
}
```

```html
<!-- Wrap small tables in an avoid-break container -->
<div class="pricing-section">
  <h3>Program Allowances</h3>
  <table>
    <!-- 8 rows, fits on one page -->
  </table>
</div>
```

### Why It Works
For short tables (under ~60% of page height), wrapping in a `page-break-inside: avoid` container keeps the entire table on one page. For long tables that must span pages, `tr { break-inside: avoid; }` ensures individual rows are not split (which would cut text in half), and `break-after: avoid` on section header rows keeps them attached to the first data row in their group.

---

## Recipe 10: Images Stretch or Distort

### Problem
Images in the PDF are stretched horizontally, squished vertically, or have different aspect ratios than the original files.

### What Happens
Without `object-fit`, an image fills its container's dimensions exactly, ignoring the original aspect ratio. A 4:3 image in a 16:9 container gets stretched. This is the same as on the web, but it is more noticeable in a PDF because you cannot scroll past it.

### Broken CSS
```css
.product-card img {
  width: 100%;
  height: 160pt;
  /* No object-fit = image stretches to fill both dimensions */
}
```

### Fixed CSS
```css
.product-card img {
  width: 100%;
  height: 160pt;
  object-fit: cover;        /* Crop to fill, maintain aspect ratio */
  object-position: center;  /* Center the crop */
  display: block;           /* Remove inline spacing */
}
```

### Why It Works
`object-fit: cover` scales the image to fill the container while maintaining aspect ratio, cropping any overflow. `object-position: center` centers the crop so the most important part of the image is visible. For product photography, you may want `object-position: top` to show the product rather than the background.

**Alternatives:**
- `object-fit: contain` -- fits the entire image inside the container, adds letterboxing
- `object-fit: scale-down` -- like `contain` but never upscales beyond natural size
- For logos specifically, use `object-fit: contain` to avoid cropping any part of the mark

---

## Recipe 11: CSS Grid Does Not Paginate

### Problem
A CSS Grid layout works perfectly in the browser but does not paginate correctly in WeasyPrint. Items overlap, disappear, or pile up on a single page.

### What Happens
WeasyPrint added CSS Grid support in version 67, and it has improved significantly. However, complex grid layouts with `grid-area`, `grid-template-areas`, or spanning items can still produce unexpected results when the grid exceeds one page. The issue is that Grid calculates a single layout for the entire grid, then tries to split it across pages -- and the split points may not align with row boundaries.

### Broken CSS
```css
.dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto auto;
  gap: 16pt;
  /* 8 items, some spanning 2 columns -- pagination unpredictable */
}
```

### Fixed CSS
```css
/* For multi-page layouts, use flexbox rows instead of grid */
.dashboard-row {
  display: flex;
  gap: 16pt;
  margin-bottom: 16pt;
  page-break-inside: avoid;
}

.dashboard-card {
  flex: 1;
  page-break-inside: avoid;
}

.dashboard-card-full {
  flex: 0 0 100%;
  page-break-inside: avoid;
}
```

### Why It Works
Flexbox rows are simpler paginated units than Grid areas. Each row is an independent block that WeasyPrint can place or split individually. For single-page layouts (dashboards, one-pagers), Grid is fine. For multi-page documents, prefer flexbox rows.

**When Grid IS safe:**
- The entire grid fits on one page
- Simple 2-column grids with no spanning items
- `grid-template-columns: auto 1fr` for key-value metadata layouts (these never span pages)

---

## Recipe 12: Font Not Rendering

### Problem
Your PDF shows a fallback font (Times New Roman, system serif) instead of the Google Font you specified in CSS.

### What Happens
WeasyPrint auto-downloads Google Fonts referenced in `font-family` declarations, but this can fail if:
1. The font name is misspelled
2. The machine has no internet access during build
3. A local font with a similar name shadows the Google Font
4. You used a `@font-face` declaration with a relative URL that does not resolve

### Broken CSS
```css
/* Misspelled font name -- WeasyPrint silently falls back */
body { font-family: 'Helveitca Neue', sans-serif; }  /* Typo! */

/* Relative @font-face URL that doesn't resolve */
@font-face {
  font-family: 'CustomBrand';
  src: url('fonts/custom-brand.woff2');  /* Relative to what? */
}
```

### Fixed CSS
```css
/* Correct spelling, explicit fallback chain */
body {
  font-family: 'Helvetica Neue', 'Inter', Helvetica, Arial, sans-serif;
}

/* For custom fonts, use absolute file:// URL or base64 */
@font-face {
  font-family: 'CustomBrand';
  src: url('file:///Users/tyfisk/project/fonts/custom-brand.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}

/* OR embed as base64 (guaranteed to work, increases CSS file size) */
@font-face {
  font-family: 'CustomBrand';
  src: url(data:font/woff2;base64,d09GMgABAAAA...) format('woff2');
  font-weight: 400;
  font-style: normal;
}
```

### Why It Works
Absolute `file://` URLs remove path resolution ambiguity. Base64 embedding eliminates the network dependency entirely -- the font is inline in the CSS, so there is nothing to download or resolve. For Google Fonts, verify the exact name at fonts.google.com (e.g., "Inter" not "inter", "Playfair Display" not "Playfair").

**Quick diagnostic:** Run `bangerpdf doctor` to check for missing fonts. Or build a single-page test:
```html
<html><body style="font-family: 'Your Font Name'">
  <h1>Font test: ABCabc 123</h1>
  <p>If this renders in the wrong font, the name is wrong or the font is not available.</p>
</body></html>
```

---

## Recipe 13: Print Color Forcing Lost on Repeated Elements

### Problem
Background colors and borders render correctly on the first page but disappear on subsequent pages, especially on repeated table headers and styled row backgrounds.

### What Happens
Some PDF viewers and WeasyPrint's own rendering can strip background colors on repeated elements (like `<thead>` rows that repeat on every page) if `print-color-adjust` is not set on the specific element. The browser-era `color-adjust` and `-webkit-print-color-adjust` properties must be set explicitly on elements with backgrounds that should survive pagination.

### Broken CSS
```css
/* Global declaration is not enough for repeated elements */
* { print-color-adjust: exact; }

thead th {
  background: #1A1A1A;
  color: white;
  /* Background may disappear on pages 2+ */
}
```

### Fixed CSS
```css
/* Set it on BOTH the global and the specific elements */
* {
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
  color-adjust: exact !important;
}

thead th {
  background: #1A1A1A;
  color: white;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}

.sov-section-row td {
  background: var(--cream);
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}

.sov-total td {
  background: var(--dark);
  color: white;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}
```

### Why It Works
Belt and suspenders. The global `*` selector should catch everything, but WeasyPrint can sometimes miss repeated elements in paginated contexts. Adding `print-color-adjust` directly on elements with background colors guarantees they persist across page breaks. This is exactly what the Carhartt bid's `styles.css` does for schedule-of-values rows -- see the `.sov-section-row` and `.sov-total` classes.

---

## Quick Reference Table

| Problem | Recipe | Key Fix |
|---------|--------|---------|
| Empty pages from flex-wrap | Recipe 1 | Explicit row containers |
| Giant blank spaces | Recipe 2 | Only `avoid` on small elements |
| Background image clipped | Recipe 3 | Use `<img>` with absolute positioning |
| Footer not at bottom | Recipe 4 | `@page` margin boxes |
| Full-bleed mixed with normal | Recipe 5 | Named `@page` rules + `page` property |
| Grid collapses to one column | Recipe 6 | Explicit flex rows, no auto-fill |
| Table headers don't repeat | Recipe 7 | `<thead>` with `table-header-group` |
| Heading orphaned at page bottom | Recipe 8 | `page-break-after: avoid` on headings |
| Table split in ugly place | Recipe 9 | Wrap in `avoid` container or `tr avoid` |
| Images stretched/distorted | Recipe 10 | `object-fit: cover` |
| Grid layout breaks on page 2+ | Recipe 11 | Prefer flexbox for multi-page |
| Wrong font in PDF | Recipe 12 | Check spelling, use absolute paths |
| Colors disappear on page 2+ | Recipe 13 | `print-color-adjust` on each styled element |

## Cross-References

- `design-taste.md` -- base CSS that already includes many of these fixes (heading break control, orphans/widows, color forcing)
- `reference.md` -- WeasyPrint feature matrix and @page rule syntax
- `SKILL.md` -- the master workflow consults this during Step 6 (Build) when layout issues arise
- `examples.md` -- the Carhartt walkthrough demonstrates Recipes 1, 3, 5, 7, and 13 in production
