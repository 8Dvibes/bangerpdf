# mgm-strategy-plan Starter Pack

Schema-driven 25-40 page strategic business plan. The `data.schema.json` is the public API -- any agentic workflow (Cassidy, n8n, Claude, custom) that produces valid JSON against it can render a professional strategy document via bangerpdf without further intervention.

## Documents

1. **Executive Summary** (3 pages) -- Cover page, table of contents, company overview, strategic positioning, investment summary
2. **Market Analysis** (5 pages) -- TAM/SAM/SOM sizing, competitive landscape table, market trends, SWOT analysis grid
3. **Strategy Canvas** (4 pages) -- Strategic pillars with initiative details, differentiators, risk matrix with likelihood/impact/mitigation
4. **Execution Roadmap** (5 pages) -- Phase timeline with Gantt-style visual, deliverables per phase, budget allocation breakdown, critical path
5. **KPI Dashboard** (3 pages) -- Scorecard table, detail cards with baseline vs target, measurement framework, escalation protocol

## Quick Start

```bash
# Initialize a new project from this pack
bangerpdf init mgm-strategy-plan ./my-strategy

# Edit data.json with your client's data
bangerpdf validate ./my-strategy

# Build all documents
bangerpdf build ./my-strategy
```

## The Schema (Public API)

The `data.schema.json` declares six required top-level objects:

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `meta` | plan_date, planner, version | Document metadata |
| `client` | name, industry, stage | Client company profile |
| `market` | tam, sam, som, competitors[], trends[] | Market sizing and competitive analysis |
| `strategy` | positioning, pillars[3-5], differentiators[], risks[] | Strategic framework |
| `execution` | phases[], budget | Implementation plan |
| `kpis` | name, target, baseline, measurement_cadence per item | Performance tracking |

### Agentic Workflow Integration

Any workflow that outputs JSON matching the schema can drive this pack:

```python
# Example: Claude workflow outputs data.json
import json, subprocess

data = generate_strategy_plan(client_brief)  # your AI workflow
with open("./my-plan/data.json", "w") as f:
    json.dump(data, f, indent=2)

subprocess.run(["bangerpdf", "validate", "./my-plan"])
subprocess.run(["bangerpdf", "build", "./my-plan"])
```

### Optional Enhancements

These fields are optional but produce richer output:

- `client.mission` -- Displays as a callout in the executive summary
- `client.logo` -- Appears on the cover page
- `market.swot` -- Renders a color-coded SWOT grid in market analysis
- `strategy.pillar_details` -- Expands pillars with descriptions and initiative lists
- `strategy.value_proposition` -- Displays as a highlighted callout
- `execution.budget_breakdown` -- Produces a detailed budget table
- `execution.critical_path` -- Highlights dependencies in the roadmap
- `kpis[].owner` -- Adds accountability column to the KPI scorecard
- `kpis[].data_source` -- Shows where measurement data comes from

## Sample Data

The included `sample-data.json` uses "Growers Solution" -- a Middle Tennessee market garden -- as the example client. It demonstrates all required and optional schema fields with realistic agricultural business data.

## Customization

### Brand Colors

Edit `brand-kit.yaml`. The default palette is:

- `--primary: #1F4E79` -- Deep blue for headings, section dividers, table headers
- `--secondary: #2E75B6` -- Medium blue for accents and borders
- `--accent: #70AD47` -- Green for highlights, KPI targets, pillar card tops
- Plus danger/warning/info colors for the SWOT grid and risk badges

### Risk Badge Colors

Risk levels map to CSS classes automatically:
- `low` -- green (accent)
- `medium` -- amber (warning)
- `high` -- red (danger)
- `critical` -- purple
