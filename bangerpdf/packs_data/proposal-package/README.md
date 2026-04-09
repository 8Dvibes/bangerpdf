# proposal-package Starter Pack

Multi-document consulting or sales proposal with cover letter, detailed proposal body, and signature/acceptance page. Approximately 10 pages.

## Documents

1. **Cover Letter** (1 page) -- Branded cover page with project name, client, and metadata
2. **Proposal** (7 pages) -- Executive summary, scope, approach, team, deliverables, timeline, pricing tiers, payment schedule, terms
3. **Signature** (2 pages) -- Tier selection checkboxes, dual signature blocks with date lines

## Quick Start

```bash
bangerpdf init proposal-package ./my-proposal
bangerpdf validate ./my-proposal
bangerpdf build ./my-proposal
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `client` | name, contact_name | Client details |
| `scope` | (string) | Scope of work |
| `approach` | (string) | Methodology description |
| `deliverables` | name, description per item | Project deliverables |
| `pricing` | total, total_label | Investment with optional tiers |
| `timeline` | phase, duration, description per item | Project phases |
| `terms` | (string[]) | Terms and conditions |
| `signature` | sender_name, sender_title, client_name, client_title | Signature block |

Optional: `meta`, `sender`, `project_name`, `executive_summary`, `out_of_scope[]`, `team[]`, `why_us[]`, `pricing.tiers[]`, `pricing.payment_schedule[]`, `deliverables[].format`.

## Customization

Edit `brand-kit.yaml` to change colors. Default is professional blue (#1a365d / #2b6cb0). Pricing tiers render as side-by-side cards with a "Recommended" badge.
