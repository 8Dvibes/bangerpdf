---
name: bangerpdf
description: >
  Generate print-ready PDFs from HTML or data with Jinja2 templates, three
  print tiers (desktop, digital press, commercial offset CMYK), automated QA,
  and HTML Review Bundles. Use when the user says "build me a bid", "create
  a proposal", "polish for client", "make a PDF", "generate an invoice",
  "ship this as a print-ready document", or any time a business document
  needs to be styled, branded, and delivered as a PDF.
user-invocable: true
allowed-tools: Read Write Edit Bash Grep Glob
argument-hint: "[pack-name] [project-dir]"
---

# bangerpdf

Make banger PDFs from HTML or data.

## When to Use This Skill

Invoke bangerpdf when the user wants to:
- **Generate a PDF** from HTML, Markdown, or structured data
- **Build a multi-document package** (bid, proposal, briefing, report)
- **Polish a document for a client** with professional styling and branding
- **Create a branded invoice, letter, or certificate** from data
- **Run a QA check** on existing PDFs (density, orphans, fonts, compliance)
- **Set up a Review Bundle** for client approval (v1 -> v2 -> approve workflow)
- **Convert for commercial print** (CMYK, crop marks, bleed, PDF/X-4)
- **Apply a brand kit** (logo, colors, fonts) to any document pack

Also invoke when the user says things like:
- "build me a bid for [client]"
- "make this print-ready"
- "polish this for the customer"
- "turn this into a professional PDF"
- "run QA on these PDFs"
- "I need an invoice / proposal / one-pager / certificate"
- "send this to the printer"

## What It Does

bangerpdf is a Python CLI (`bangerpdf` or `banger`) with 10 starter packs, a 13-check QA suite, and a three-tier print pipeline.

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

### 13 QA Checks
Powered by PyMuPDF. Catches: empty pages, orphan signatures, orphan headers, table splits, content overflow, broken images, unresolved Jinja2 vars, dict.items collisions, broken URLs, headline inconsistency, missing fonts, missing bleed, PDF/X non-compliance.

## Quick Reference

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

### Brand Kit
```bash
bangerpdf brand show
bangerpdf brand set primary "#1F4E79"
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

## Cross-References

- **`pdf` skill** (Anthropic vetted skill) -- for reading, extracting, merging, splitting, and filling EXISTING PDFs. Use `pdf` for manipulation, `bangerpdf` for generation.
- **`docx` skill** (Anthropic vetted skill) -- for creating and editing Word documents with tracked changes. Use `docx` for editable .docx files, `bangerpdf` for final-form PDFs.
- **`tools/jj-pdf-toolkit`** -- DEPRECATED. bangerpdf supersedes it and lifts JJ's scripts unchanged as its Layer 1 (convert, embed_assets, proof). The JJ toolkit is preserved in git history but the skill should no longer be used.

## The MGM Schema Contract

The `mgm-strategy-plan` starter pack ships with `data.schema.json` -- a JSON Schema that defines the public API for agentic workflows. Any Cassidy, n8n, or Claude workflow that produces a valid `data.json` matching this schema can call:

```bash
bangerpdf init mgm-strategy-plan ./output
cp workflow-output.json ./output/data.json
cd ./output && bangerpdf build --tier all
```

No human intervention required. The schema IS the contract.

## For More Details

- `reference.md` -- advanced CSS for print, @page rules, margin boxes, WeasyPrint support matrix, PyMuPDF patterns
- `examples.md` -- three end-to-end walkthroughs (fresh bid, agentic MGM, commercial print conversion)
