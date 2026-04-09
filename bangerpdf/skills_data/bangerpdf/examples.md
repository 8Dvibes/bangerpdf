# bangerpdf — End-to-End Examples

Three walkthroughs showing the full pipeline.

## Example 1: Fresh Bid Package from Scratch

You're a plumber bidding on a healthcare ASC project. You need a cover letter, full proposal with schedule of values, a leave-behind one-pager, phone scripts, and a thank-you email.

```bash
# 1. Scaffold the bid-package starter
bangerpdf init bid-package ./acme-bid --brand "Acme Plumbing" --primary "#0D1B2A" --logo ./logo.png

# 2. Edit the data
cd ./acme-bid
# Open data.json and fill in:
#   - bidder info (name, license, contact)
#   - project details (client, location, scope)
#   - schedule of values (line items with quantities, rates, amounts)
#   - local comparable data (optional, strengthens the bid)

# 3. Validate your data against the schema
bangerpdf validate

# 4. Build all three tiers
bangerpdf build --tier all
# Output:
#   pdfs/desktop/01_Cover_Letter.pdf ... 05_Thank_You_Email.pdf
#   pdfs/digital-press/01_Cover_Letter.pdf ... (with crop marks)
#   pdfs/commercial/01_Cover_Letter.pdf ... (CMYK + PDF/X-4)

# 5. Run the QA checker
bangerpdf qa pdfs/desktop/ --expected "01_Cover_Letter.pdf=2,02_Bid_Proposal.pdf=7"
# Expected output: all checks clean

# 6. Create a Review Bundle for client approval
bangerpdf review init ./client-review --from .
bangerpdf review build --preview
# Opens the review bundle in your browser

# 7. After client feedback, revise and re-approve
bangerpdf review annotate 02_Bid_Proposal.pdf --page 3 --note "Tighten SOV table"
bangerpdf build   # rebuild with fixes
bangerpdf review revise
bangerpdf review approve
```

## Example 2: MGM Strategy Plan via Agentic Workflow

Your Cassidy/n8n/Claude workflow generates a strategic business plan as structured JSON. bangerpdf converts it to a polished 12-page PDF without any human touching a template.

```bash
# 1. Your agentic workflow writes data.json matching the MGM schema
# (see data.schema.json for the full contract)
cat > /tmp/growers-data.json << 'EOF'
{
  "meta": {"plan_date": "2026-04-09", "planner": "Market Maven Agent", "version": "1.0"},
  "client": {"name": "Growers Solution", "industry": "Agriculture", "stage": "Growth", "arr": 450000},
  "market": {
    "tam": 5000000000,
    "sam": 150000000,
    "som": 7500000,
    "competitors": [
      {"name": "FarmFresh Direct", "strength": "Brand recognition", "weakness": "No tech stack", "threat_level": "medium"},
      {"name": "AgriTech Solutions", "strength": "Full automation", "weakness": "Premium pricing", "threat_level": "high"}
    ],
    "trends": ["Direct-to-consumer growth", "Sustainability premium", "Climate-adaptive varieties"]
  },
  "strategy": {
    "positioning": "Technology-enabled local agriculture with direct consumer relationships",
    "pillars": ["Local-first distribution", "Data-driven crop planning", "Community partnerships"],
    "differentiators": ["Same-day harvest to table", "Transparent pricing", "Seasonal subscription model"],
    "risks": [
      {"name": "Weather dependency", "likelihood": "high", "impact": "high", "mitigation": "Greenhouse expansion + crop insurance"},
      {"name": "Labor shortage", "likelihood": "medium", "impact": "medium", "mitigation": "Automation investment + apprentice program"}
    ]
  },
  "execution": {
    "phases": [
      {"name": "Foundation", "duration_weeks": 8, "deliverables": ["Market research", "Brand identity", "Website"], "owner": "Tyler"},
      {"name": "Launch", "duration_weeks": 12, "deliverables": ["First harvest", "CSA signups", "Farmers market presence"], "owner": "Operations"},
      {"name": "Scale", "duration_weeks": 24, "deliverables": ["Restaurant partnerships", "Online store", "Second location assessment"], "owner": "Growth"}
    ],
    "budget": 125000
  },
  "kpis": [
    {"name": "Monthly Revenue", "target": "$37,500", "baseline": "$0", "measurement_cadence": "monthly"},
    {"name": "CSA Subscribers", "target": "200", "baseline": "0", "measurement_cadence": "weekly"},
    {"name": "Restaurant Partners", "target": "15", "baseline": "0", "measurement_cadence": "monthly"},
    {"name": "Customer Satisfaction", "target": "4.8/5", "baseline": "N/A", "measurement_cadence": "quarterly"}
  ]
}
EOF

# 2. Scaffold and inject the data
bangerpdf init mgm-strategy-plan /tmp/growers-plan
cp /tmp/growers-data.json /tmp/growers-plan/data.json

# 3. Validate + build + QA (three commands, zero human intervention)
cd /tmp/growers-plan
bangerpdf validate && bangerpdf build --tier all && bangerpdf qa pdfs/desktop/ --strict

# 4. Ship it
# The PDFs are ready to email, print, or upload to a client portal.
```

## Example 3: Polish Existing HTML for Commercial Print

You have a brochure designed in the browser. You need it print-ready for a commercial offset press with CMYK colors, crop marks, and bleed.

```bash
# 1. Convert with asset embedding + commercial tier
bangerpdf convert brochure.html --embed-assets --tier commercial

# If you need more control over the brand:
bangerpdf convert brochure.html --embed-assets --tier commercial --icc GRACoL2013

# 2. Run QA for the commercial tier
bangerpdf qa brochure.pdf --bleed-in 0.125 --require-pdfx

# Expected output:
#   If bleed/CMYK/PDF-X are all correct: clean
#   If missing bleed: BLEED_MISSING error
#   If missing PDF/X markers: PDFX_MISSING error

# 3. Generate proofs for the print shop
bangerpdf proof brochure.pdf --dpi 300

# 4. Send brochure.pdf + the 300dpi proofs to your printer
```
