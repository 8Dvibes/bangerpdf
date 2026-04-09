# one-pager Starter Pack

Single-page overview document with bold typography, headline stats, structured body sections, and a call-to-action. Designed to be scannable in under 60 seconds.

## Documents

1. **One Pager** (1 page) -- Hero header, stat bar, 2-column body sections, CTA block

## Quick Start

```bash
bangerpdf init one-pager ./my-one-pager
bangerpdf validate ./my-one-pager
bangerpdf build ./my-one-pager
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `title` | (string) | Primary title |
| `subtitle` | (string) | Tagline or subtitle |
| `headline_stats` | label, value per item (2-5 items) | Prominent statistics |
| `body_sections` | heading, content per item | Content sections (2-col grid) |
| `cta` | text, optional url | Call-to-action block |

Optional: `logo`, `footer_text`.

## Customization

Edit `brand-kit.yaml` to change colors. Default is bold blue (#0D47A1 / #1976D2). Body sections render in a 2-column grid. For best results, use 4 body sections (fills the 2x2 grid evenly).
