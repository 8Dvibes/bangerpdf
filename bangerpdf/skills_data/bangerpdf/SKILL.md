---
name: bangerpdf
description: "Generate print-ready PDFs from HTML or data. Bids, proposals, invoices, brochures, reports, one-pagers, certificates. Three print tiers, 17-check QA, brand discovery, design interviews. Use for 'make a PDF', 'build a bid', 'create a proposal'."
user-invocable: true
allowed-tools: Read Write Edit Bash Grep Glob
argument-hint: "[pack-name] [project-dir]"
---

# bangerpdf

Intelligent design partner that interviews you, discovers your brand, and builds banger PDFs.

**CRITICAL BEHAVIOR**: When a user mentions a NEW document project (proposal, bid,
invoice, report, brochure, one-pager, leave-behind, certificate, briefing, quote,
presentation, or any client-facing document), ALWAYS begin with the Design Interview
(Step 1) before proceeding to build. Do NOT skip straight to scaffolding a pack.
The interview ensures the output matches what the user actually wants on the first draft.

Exception: If the user explicitly says "just build it" or provides complete
specifications (recipient, purpose, vibe, brand, and content), skip the interview.

---

## Workflow (Follow This Order)

For EVERY new document project, follow these steps in order:

### Step 1: Design Interview
Before writing any code, run the design interview (see `design-interview.md`).
Ask the 5 questions: Who, What, Vibe, Assets, References.
Output: `design-brief.yaml` in the project directory.

### Step 2: Brand Discovery
If the user provides a company name or URL, auto-discover their brand.
Run `bangerpdf brand discover <url>` or manual research.
See `brand-discovery.md` for the full pipeline.
Check if a saved brand exists: `bangerpdf brand list`

### Step 3: Vibe Selection & Layout
Based on the design brief, select CSS patterns from the vibe system.
See `design-taste.md` -- Vibe System for the 4 vibes and their CSS.
Load matching layout patterns: `bangerpdf patterns list`

### Step 4: Visual Generation
For Bold or Editorial vibes: generate hero images, product photos, lifestyle imagery.
Use `/nano-banana-2` for photorealistic images, `/bananas` for structured infographics.
See `visuals-guide.md` for the full pipeline. This is DEFAULT for visual vibes, not optional.
For Corporate or Minimal vibes: CSS-only visuals are sufficient.

### Step 5: Build
Scaffold: `bangerpdf init <pack> <dir>`
Customize: data.json, brand-kit.yaml, styles.css, templates/
Render: `bangerpdf build`

### Step 6: QA & Page Flow
Run `bangerpdf qa --strict` (17 checks).
Manually verify: no orphaned headings, no split sections, no excessive whitespace.
See `weasyprint-cookbook.md` for common layout fixes.

### Step 7: Iterate
Present PDFs to user. Incorporate feedback. Rebuild.
Each iteration should improve, not regress.

### Step 8: Save & Reuse
Offer to save the brand for reuse: `bangerpdf brand save <name>`
Offer to update global preferences: `bangerpdf preferences set <key> <value>`
See `design-memory.md` for the full save/load system.

---

## When to Use This Skill

Invoke bangerpdf when the user wants to:
- **Generate a PDF** from HTML, Markdown, or structured data
- **Build a multi-document package** (bid, proposal, briefing, report)
- **Polish a document for a client** with professional styling and branding
- **Create a branded invoice, letter, or certificate** from data
- **Design a brochure, one-pager, or leave-behind** for a client presentation
- **Build a quote or bid package** for a project
- **Run a QA check** on existing PDFs (density, orphans, fonts, compliance)
- **Set up a Review Bundle** for client approval (v1 -> v2 -> approve workflow)
- **Convert for commercial print** (CMYK, crop marks, bleed, PDF/X-4)
- **Apply a brand kit** (logo, colors, fonts) to any document pack
- **Start a new document project** from scratch with guided setup
- **Discover and save a brand** for reuse across projects

Also invoke when the user says things like:
- "build me a bid for [client]"
- "create a proposal for [project]"
- "make a PDF of this"
- "generate an invoice for [client]"
- "design a document for [purpose]"
- "create a brochure for [product/service]"
- "make a report on [topic]"
- "I need a proposal for a client"
- "build a quote for [project]"
- "make a one-pager for [topic]"
- "polish this for the client"
- "make it print-ready"
- "ship this as a PDF"
- "start a new document project"
- "set up a bid package"
- "I have a client presentation"
- "create a leave-behind"
- "turn this into a professional PDF"
- "run QA on these PDFs"
- "send this to the printer"
- "I need an invoice / proposal / one-pager / certificate"
- "make this look professional"
- "brand this document"

---

## What It Does

bangerpdf is a Python CLI (`bangerpdf` or `banger`) with 10 starter packs, a 17-check QA suite, a three-tier print pipeline, brand discovery, design interviews, and saved brand memory.

### Three Print Tiers
- **Desktop** -- screen/email optimized (sRGB, no bleed)
- **Digital Press** -- crop marks + 0.125" bleed for short-run printers
- **Commercial Offset** -- RGB to CMYK + PDF/X-4 for commercial print shops

### 10 Starter Packs
- `bid-package` -- cover letter, proposal, leave-behind, phone scripts, thank-you email
- `mgm-strategy-plan` -- 25-40 page strategic plan (schema-driven for agentic workflows)
- `proposal-package` -- single-doc consulting/sales proposal
- `briefing-package` -- 1-2 page executive briefing
- `one-pager` -- single page overview
- `certificate` -- completion/training certificate
- `invoice` -- branded invoice
- `letter` -- formal business letter with letterhead
- `report-package` -- multi-page with table of contents
- `review-bundle` -- HTML approval document (not PDF)

### 17 QA Checks
Powered by PyMuPDF. Catches: empty pages, orphan signatures, orphan headers, table splits, content overflow, broken images, unresolved Jinja2 vars, dict.items collisions, broken URLs, headline inconsistency, missing fonts, missing bleed, PDF/X non-compliance, heading orphans (heading in bottom 15% with no body following), section splits (heading on one page, body on next), excessive whitespace (page >70% whitespace with no full-bleed imagery), single-element pages (page with only one small content element).

---

## Quick Reference

### Design Interview
```bash
bangerpdf design
```

### Brand Discovery & Management
```bash
bangerpdf brand discover <url>       # Auto-research a brand from URL
bangerpdf brand save <name>          # Save current brand profile
bangerpdf brand load <name>          # Load a saved brand profile
bangerpdf brand list                 # List all saved brands
bangerpdf brand show                 # Show current brand-kit
bangerpdf brand set primary "#1F4E79"  # Set a brand property
```

### Global Preferences
```bash
bangerpdf preferences set <key> <value>  # Set a global default
bangerpdf preferences show               # Show all preferences
```

### Gallery & Patterns
```bash
bangerpdf gallery show [vibe]    # Reference examples (corporate/bold/editorial/minimal)
bangerpdf patterns list          # Layout pattern library
```

### Convert HTML to PDF
```bash
bangerpdf convert input.html --embed-assets
bangerpdf convert input.html --embed-assets --tier commercial
```

### Build a Multi-Document Pack
```bash
bangerpdf init bid-package ./my-bid --brand "Acme Corp" --primary "#2B5EA7"
cd ./my-bid
# Edit data.json with project details
bangerpdf build --tier all
bangerpdf qa --strict
```

### Run QA on Existing PDFs
```bash
bangerpdf qa ./pdfs/
bangerpdf qa ./pdfs/ --expected "proposal.pdf=7,summary.pdf=1"
bangerpdf qa ./pdfs/ --headlines "total=$445000,client=Acme"
bangerpdf qa ./pdfs/ --check-links --strict
```

### Review Bundle Workflow
```bash
bangerpdf review init ./client-review --from ./my-bid
bangerpdf review build
# Client reviews v1, provides feedback
bangerpdf review revise
bangerpdf review approve
```

### Skills Management
```bash
bangerpdf skills list
bangerpdf skills install
bangerpdf skills install --force
```

### Diagnostics
```bash
bangerpdf doctor
bangerpdf --version
```

---

## Skill Files

This skill is composed of 9 files. Read the relevant ones before starting work:

| File | Purpose |
|------|---------|
| `SKILL.md` | This file. Entry point and workflow. |
| `design-interview.md` | Structured 5-question interview for new projects |
| `brand-discovery.md` | Automated brand research (web scrape + optional Brand Fetch) |
| `design-taste.md` | Layout, color, typography, anti-slop rules, vibe system |
| `visuals-guide.md` | Nano Banana integration, BANANAS prompting, image generation |
| `design-memory.md` | Save/load brands, global preferences, project templates |
| `weasyprint-cookbook.md` | Layout pitfalls and tested CSS fixes |
| `reference.md` | Advanced CSS, WeasyPrint support matrix, QA patterns |
| `examples.md` | End-to-end walkthroughs including visual-forward builds |

---

## Design Quality

Every PDF must pass the design taste check. Before writing any HTML/CSS:

1. **Read `design-taste.md`** -- establishes spacing scale, color rules, type hierarchy, anti-slop checklist, vibe system
2. **Choose document type pattern** -- proposals, reports, invoices, one-pagers each have conventions
3. **Set up CSS custom properties** -- spacing scale, type scale, color palette BEFORE writing content
4. **Run the vibe check** -- squint test, element-earns-its-place test, consistency check

Key rules (full details in design-taste.md):
- Maximum 2 fonts, 3-5 colors, 8pt spacing multiples
- 60-30-10 color ratio: 60% background, 30% secondary, 10% accent
- Perfect Fourth type scale (1.333): 11pt body -> 15pt H3 -> 19pt H2 -> 25pt H1
- 40%+ whitespace on every page
- Every element must earn its place -- if you can't justify it, remove it

---

## Visual Generation (Nano Banana)

For custom graphics, charts, and visuals -- use Nano Banana integration. See `visuals-guide.md` for full pipeline.

Quick workflow:
1. Analyze what visual is needed (infographic, hero image, chart, decorative element)
2. Use `/nano-banana-2` to generate image -> save to pack's `assets/` directory
3. Reference in template: `<img src="assets/visual-name.png">`
4. `bangerpdf build` auto-embeds via base64

When NOT to generate:
- Simple bar/line/pie charts -> use HTML/CSS tables or SVG
- Logos and brand marks -> use user-provided assets
- Text-heavy content -> keep as HTML, don't bake into images

When TO generate:
- Stylized infographics with brand personality
- Hero/header images with abstract patterns
- Process diagrams and visual flowcharts
- Photorealistic product/lifestyle imagery
- Bold and Editorial vibe builds (default behavior for these vibes)

---

## The MGM Schema Contract

The `mgm-strategy-plan` starter pack ships with `data.schema.json` -- a JSON Schema that defines the public API for agentic workflows. Any Cassidy, n8n, or Claude workflow that produces a valid `data.json` matching this schema can call:

```bash
bangerpdf init mgm-strategy-plan ./output
cp workflow-output.json ./output/data.json
cd ./output && bangerpdf build --tier all
```

No human intervention required. The schema IS the contract.

---

## Cross-References

- **`pdf` skill** (Anthropic vetted skill) -- for reading, extracting, merging, splitting, and filling EXISTING PDFs. Use `pdf` for manipulation, `bangerpdf` for generation.
- **`docx` skill** (Anthropic vetted skill) -- for creating and editing Word documents with tracked changes. Use `docx` for editable .docx files, `bangerpdf` for final-form PDFs.
- **`tools/jj-pdf-toolkit`** -- DEPRECATED. bangerpdf supersedes it and lifts JJ's scripts unchanged as its Layer 1 (convert, embed_assets, proof). The JJ toolkit is preserved in git history but the skill should no longer be used.
