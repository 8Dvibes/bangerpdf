# bid-package Starter Pack

Multi-document construction/trade bid package with five coordinated documents:

1. **Cover Letter** (2 pages) -- Professional introduction with bid summary, differentiators, and growth pitch
2. **Bid Proposal** (7 pages) -- Full schedule of values, allowances, clarifications, exclusions, company background, schedule, payment terms, and acceptance block
3. **Leave-Behind** (1 page) -- Compressed one-pager for in-person meetings with key stats and selling points
4. **Phone Scripts** (4 pages) -- Pre-bid verification call scripts with fill-in-the-blank answer fields
5. **Thank-You Email** (2 pages) -- Post-meeting follow-up template with placeholder guidance

## Quick Start

```bash
# Initialize a new project from this pack
bangerpdf init bid-package ./my-bid

# Edit data.json with your real project data
# Replace logo.png with your company logo

# Validate your data against the schema
bangerpdf validate ./my-bid

# Build all documents
bangerpdf build ./my-bid
```

## Files

| File | Purpose |
|------|---------|
| `pack.yaml` | Pack manifest with document list and expected page counts |
| `data.schema.json` | JSON Schema (draft-07) for validating your data.json |
| `sample-data.json` | Example data for "Example Plumbing, LLC" |
| `brand-kit.yaml` | Default navy/blue color palette with Inter font |
| `styles.css` | CSS using CSS custom properties for all colors |
| `templates/` | Five Jinja2 HTML templates |

## Customization

### Brand Colors

Edit `brand-kit.yaml` to change the color palette. All templates use CSS variables:

- `--primary` -- Dark color for headings, section dividers, headline number background
- `--secondary` -- Medium color for callout borders, tags, links, section accent
- `--accent` -- Lighter accent for hover states and highlights
- `--neutral-dark` through `--neutral-light` -- Text and background grays
- `--warning-bg`, `--warning-text`, `--warning-border` -- Placeholder highlight colors

### Data Structure

The schema requires these top-level keys:

- `meta` -- bid date, validity, version
- `bidder` -- company name, owner, license, contact info
- `project` -- project name, GC info, site details, building specs
- `bid` -- headline amount, tiers, floor
- `schedule_of_values` -- sectioned line-item cost breakdown
- `exclusions` -- items NOT in the bid
- `clarifications` -- bid assumptions and bases
- `allowances` -- contingency allowances included in bid

Optional but recommended: `growth_pitch`, `differentiators`, `phone_scripts`, `schedule_milestones`, `payment_terms`, `about`, `licensure`, `insurance`.

### Adding Your Logo

Place your logo file in the project directory and set `bidder.logo` in data.json to the filename. The letterhead will display it at 165pt width.
