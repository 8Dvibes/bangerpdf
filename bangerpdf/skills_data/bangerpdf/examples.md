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

## Example 4: Visual-Forward Bid Package (Carhartt Custom Merch)

A complete walkthrough of the real Carhartt merch bid session -- from design interview through final delivery. This is the Bold vibe in action with generated imagery, product research, and iterative layout fixes.

### Step 1: Design Interview

```
User: "We need a merch bid for AI Build Lab, Carhartt products"
```

bangerpdf triggers the design interview automatically for a new document project:
1. **WHO** is receiving this? -- AI Build Lab team, for internal branded merch
2. **WHAT** is the purpose? -- Bid package showing product options, pricing, embroidery details
3. **VIBE** -- Bold (full-bleed hero imagery, lifestyle photography, look-book feel)
4. **ASSETS** -- AI Build Lab logo available, Carhartt brand to be auto-discovered
5. **REFERENCES** -- "Make it look like a Carhartt catalog, not a spreadsheet"

### Step 2: Brand Discovery

```bash
bangerpdf brand discover https://carhartt.com
```

Discovered brand elements:
- **Colors:** Carhartt Brown `#B77729`, Gold `#F5A600`, Black `#1A1A1A`, White
- **Fonts:** Helvetica Neue (heading), Helvetica Neue (body)
- **Logo:** Carhartt "C" logo + wordmark extracted
- **Imagery style:** Workwear lifestyle, outdoor/industrial settings

### Step 3: Product Research

Products selected from the Carhartt/SanMar catalog:
- **K87 Workwear Pocket Tee** -- $19.99 (base), available in 20+ colors
- **A18 Acrylic Watch Hat (Beanie)** -- $19.99, available in 15+ colors
- **K121 Midweight Hooded Sweatshirt** -- $54.99, pullover hoodie
- **Sherpa-Lined Mock Neck Vest** -- $89.99, premium piece

### Step 4: Embroidery Pricing

- Per-unit embroidery: ~$5-8 depending on stitch count and location
- Digitization fee: $45 one-time setup per logo
- AI Build Lab logo: estimated 5,000 stitches, left chest placement

### Step 5: Vibe Selection -- Bold

Bold vibe means:
- Full-bleed hero imagery on the cover
- Lifestyle photography throughout (forge, farm, woodwork settings)
- Product grid with large images, not just a table of SKUs
- Dark hero sections with light text overlay
- The document should feel like a brand catalog, not a purchase order

### Step 6: Visual Generation

Generated a product mockup using Nano Banana 2 with the BANANAS 7-layer architecture:

```bash
# AI Build Lab logo on Carhartt K87 -- product mockup
python ~/.claude/skills/nano-banana-2/generate_image.py \
  /tmp/k87-mockup-prompt.json \
  ./assets/k87-logo-mockup.png \
  "4:3" "2K"
```

### Step 7: Asset Download

Downloaded from SanMar CDN and lifestyle sources:
- Product shots: K87, A18, K121, vest (clean white background, multiple angles)
- Lifestyle photos: forge/workshop setting, farm/outdoor setting, woodworking setting
- Section dividers: atmospheric Carhartt-style workwear imagery

```bash
mkdir -p assets
# Product images from SanMar CDN
curl -o assets/k87-desert.png "https://cdn.sanmar.com/..."
curl -o assets/a18-black.png "https://cdn.sanmar.com/..."
# Lifestyle images for section dividers
# (generated via Nano Banana 2 with Carhartt brand colors)
```

### Step 8: Template Customization

Built with Bold vibe patterns:
- **Cover page:** Full-bleed hero with dark overlay, Carhartt Brown accent bar, white title text
- **Product grid:** 2x2 layout per page, large product images with pricing and color swatches
- **Lifestyle sections:** Full-width photography as section dividers between product categories
- **Pricing summary:** Clean table with embroidery costs broken out

```bash
bangerpdf init bid-package ./carhartt-bid --brand "Carhartt Custom" --primary "#B77729"
# Customized templates for look-book layout
```

### Step 9: Build + QA

```bash
bangerpdf build --tier all
bangerpdf qa pdfs/desktop/ --strict
# Result: 5 PDFs, all 17 checks passing
```

### Step 10: Iteration -- First Draft Was "Vanilla"

Tyler's feedback on v1: "This looks like a generic bid. I want a look-book with photography."

Changes made:
- Swapped plain white cover for full-bleed lifestyle hero with gradient overlay
- Added lifestyle photography section dividers between product categories
- Converted the pricing table into a styled product card grid
- Added a premium callout section for the sherpa vest (highest margin item)

### Step 11: Page Flow Fix

The allowances table was splitting across pages, leaving orphaned header rows:

```
PROBLEM: flex-wrap + percentage widths on product cards = cards splitting mid-page
FIX: Replaced flex-wrap grid with explicit row containers (<div class="product-row">)
     Each row is a self-contained unit with page-break-inside: avoid
```

Also fixed:
- Premium vest callout was alone on a page -- merged it into the product grid section
- Consolidated sections to eliminate a nearly-empty page 4

### Step 12: Brand Save

```bash
bangerpdf brand save carhartt-merch
# Saved to ~/.config/bangerpdf/brands/carhartt-merch/
# Contains: brand-kit.yaml, logo files, color palette, font choices
# Reusable for future Carhartt merch bids without re-discovering
```

### Key Commands Summary

```bash
bangerpdf brand discover https://carhartt.com        # Auto-discover brand
bangerpdf init bid-package ./carhartt-bid             # Scaffold pack
bangerpdf build --tier all                            # Build 3 tiers
bangerpdf qa pdfs/desktop/ --strict                   # QA all PDFs
bangerpdf brand save carhartt-merch                   # Save for reuse
bangerpdf brand load carhartt-merch                   # Load saved brand
```

