# briefing-package Starter Pack

1-2 page executive briefing document designed for senior leadership. Concise, scannable format with situation context, key findings (color-coded by severity), recommendations, and a next-actions table with owners and deadlines.

## Documents

1. **Briefing** (2 pages) -- TL;DR box, context, findings with severity badges, recommendations, action table

## Quick Start

```bash
bangerpdf init briefing-package ./my-briefing
bangerpdf validate ./my-briefing
bangerpdf build ./my-briefing
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `title` | (string) | Briefing title |
| `audience` | (string) | Target audience |
| `date` | (string) | Briefing date |
| `tldr` | (string) | Bottom-line executive summary |
| `context` | (string) | Situation background |
| `findings` | title, detail per item | Key findings with optional severity |
| `recommendations` | (string[]) | Recommended actions |
| `next_actions` | action, owner, due per item | Accountable action items |

Optional: `author`, `classification`, `appendix_notes`, `findings[].severity` (info/warning/critical).

## Customization

Edit `brand-kit.yaml` to change colors. Default palette is minimal dark gray with blue accent. Finding cards are color-coded: blue (info), amber (warning), red (critical).
