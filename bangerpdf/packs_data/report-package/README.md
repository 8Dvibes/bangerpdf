# report-package Starter Pack

Multi-page research or analysis report with cover page, auto-generated table of contents, executive summary, looped content sections with subsections, appendices, and references. Designed for 15+ page reports.

## Documents

1. **Cover** (1 page) -- Title, subtitle, author, date, classification
2. **Table of Contents** (1 page) -- Auto-generated from sections and subsections
3. **Executive Summary** (2 pages) -- Summary callout, report structure overview
4. **Sections** (10+ pages) -- Looped sections with numbered subsections
5. **Appendix** (3 pages) -- Appendices and numbered references list

## Quick Start

```bash
bangerpdf init report-package ./my-report
bangerpdf validate ./my-report
bangerpdf build ./my-report
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `title` | (string) | Report title |
| `author` | (string) | Author or organization |
| `date` | (string) | Report date |
| `exec_summary` | (string) | Executive summary text |
| `sections` | title, content per item | Report body sections |

Optional: `subtitle`, `version`, `classification`, `logo`, `sections[].subsections[]`, `appendices[]`, `references[]`.

## Table of Contents

The TOC is auto-generated from the `sections` array. Each section appears as a numbered entry, and subsections appear indented with `X.Y` numbering. Appendices and references are listed separately.

## Customization

Edit `brand-kit.yaml` to change colors. Default is academic blue-gray (#2D3748 / #4299E1). Body text is justified for a traditional report appearance. The TOC and sections use automatic section numbering via Jinja2 loop indices.
