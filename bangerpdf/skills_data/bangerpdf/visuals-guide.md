# bangerpdf — Generated Visuals Integration Guide

How to use Nano Banana 2 (Gemini image generation) to create custom graphics, charts, and visuals for bangerpdf documents.

## When to Generate vs Use Existing

Not every visual needs AI generation. Pick the right approach for the job.

### Use Nano Banana (AI Generation) When:
- **Infographic-style data visualizations** -- stylized charts with branded backgrounds, icon overlays, and callout numbers that CSS cannot replicate
- **Hero/header images** -- atmospheric backgrounds, abstract patterns, textured section headers
- **Process diagrams with personality** -- illustrated flowcharts, step-by-step timelines with visual metaphors
- **Before/after or comparison visuals** -- photo-realistic mockups, rendered product shots
- **Decorative branded elements** -- custom section dividers, watermark-style background textures, chapter openers

### Use HTML/CSS Instead When:
- **Simple data charts** -- bar charts, pie charts, progress bars, horizontal stacked bars (CSS flexbox/grid handles these cleanly)
- **Tables and matrices** -- WeasyPrint renders tables and grid layouts natively
- **Metric callout cards** -- big numbers, stat boxes, KPI grids (CSS is faster and resolution-independent)
- **Geometric dividers** -- simple lines, gradient bars, colored accent strips

### Use User-Provided Assets When:
- **Logos** -- always use the client's actual logo file, never generate one
- **Headshots/team photos** -- real photographs of real people
- **Screenshots** -- product screenshots, app interfaces, dashboards
- **Existing brand materials** -- previously approved graphics, icons, illustrations

### Decision Tree

```
Is it a logo, headshot, or screenshot?
  YES -> Use the real file. Never generate.
  NO  -> Can CSS flexbox/grid/gradients achieve the same effect?
    YES -> Write it in HTML/CSS. Faster, sharper, no API call.
    NO  -> Does it need photorealism, texture, or complex visual metaphor?
      YES -> Use /nano-banana-2 (Dense Narrative format for max control)
      NO  -> Does it need structured infographic layout with precise text?
        YES -> Use /bananas (7-layer BANANAS architecture)
        NO  -> Use /nano-banana-2 with a simple prompt
```

## The Nano Banana to bangerpdf Pipeline

### Step-by-Step Workflow

#### 1. Create the assets directory in the pack

bangerpdf packs do not ship with an `assets/` directory by default. Create one at the pack root:

```bash
cd /path/to/my-pack
mkdir -p assets
```

#### 2. Read the brand kit to extract colors and fonts

Before generating any visual, load the pack's brand identity:

```bash
cat brand-kit.yaml
```

Extract the hex codes and font family. You will pass these directly into the generation prompt to maintain visual consistency.

#### 3. Write the prompt JSON

Create a prompt JSON file in a temp location. Use the Dense Narrative format for most PDF visuals:

```bash
cat > /tmp/hero-prompt.json << 'PROMPT'
{
  "prompt": "Professional business document header background. Abstract geometric pattern of overlapping translucent navy (#0D1B2A) and blue (#2B5EA7) angular shapes on a clean white (#f8fafc) background. Subtle depth created by layered transparency at 15-25% opacity. Clean, modern, corporate aesthetic. No text, no people, no objects. Horizontal composition suitable for a document header bar. Flat lighting, matte digital finish, crisp vector-quality edges. The pattern should be denser on the left side and fade to near-white on the right, creating a natural reading flow.",
  "negative_prompt": "text, words, letters, people, faces, photos, busy patterns, gradients that look like default PowerPoint, clip art, 3D renders, metallic textures, drop shadows",
  "settings": {
    "resolution": "2K",
    "style": "modern corporate design",
    "lighting": "flat, even, no dramatic shadows",
    "quality": "crisp edges, vector-like precision, print-ready clarity"
  }
}
PROMPT
```

#### 4. Generate the image to the pack's assets directory

Use the Nano Banana 2 script directly:

```bash
python ~/.claude/skills/nano-banana-2/generate_image.py \
  /tmp/hero-prompt.json \
  /path/to/my-pack/assets/hero-header.png \
  "17:5" \
  "2K"
```

The skill is located at:
```
~/.claude/skills/nano-banana-2/generate_image.py
```

Or from the Founders Lounge repo:
```
~/GitHub/AI-Build-Lab-Founders-Lounge/.claude/skills/nano-banana-2/generate_image.py
```

#### 5. Reference the image in your Jinja2 template

In the HTML template, reference images relative to the pack root:

```html
<!-- Hero header image -->
<div class="hero-section">
  <img src="assets/hero-header.png" alt="Section header" class="hero-img">
</div>

<!-- Or as a CSS background -->
<div class="header-bar" style="background-image: url('assets/hero-header.png');">
  <h1>{{ project.name }}</h1>
</div>
```

#### 6. Build the pack

WeasyPrint resolves relative paths from the pack root directory (`base_url=str(pack.pack_dir)` in the render engine), so `assets/hero-header.png` resolves correctly during build:

```bash
bangerpdf build --tier all
```

For standalone HTML conversion, use `--embed-assets` to base64-inline images:

```bash
bangerpdf convert document.html --embed-assets --tier desktop
```

The `embed_assets.py` module handles both `<img src="...">` tags and CSS `url(...)` references, converting local file paths to base64 data URIs.

#### 7. Verify with QA

Run QA to catch broken images:

```bash
bangerpdf qa pdfs/desktop/ --strict
```

The QA checker flags `BROKEN_IMAGE` if any referenced image failed to embed.

### Pipeline Summary

```
brand-kit.yaml --> extract colors/fonts
                    |
                    v
prompt.json ------> generate_image.py --> assets/visual-name.png
                                              |
                                              v
template.html ---> <img src="assets/visual-name.png">
                    |
                    v
bangerpdf build --> WeasyPrint resolves from pack root --> PDF
                    |
                    v
bangerpdf qa -----> checks for broken images
```

## Prompt Engineering for PDF Visuals

PDF visuals have specific requirements that differ from social media or web graphics. The image will be rendered at a fixed size in a static document with no interactivity.

### Infographic-Style Data Visualization

Best for: executive summaries, market analysis, KPI dashboards.

Key prompt elements:
- Specify exact numbers and text to render (Gemini achieves 97%+ text accuracy)
- Request clean backgrounds that work when placed on a white page
- Ask for flat lighting to avoid visual competition with the document text
- Include explicit whitespace/margin instructions

```json
{
  "prompt": "Clean data visualization infographic panel for a business proposal. White background. Three metric cards arranged horizontally: left card shows '$2.4M' in bold navy (#0D1B2A) with caption 'Annual Revenue' in gray (#64748b), center card shows '156' in blue (#2B5EA7) with caption 'Active Clients', right card shows '99.7%' in blue (#3B7DD8) with caption 'Uptime SLA'. Each card has a subtle light gray (#f1f5f9) rounded rectangle background with 1px border in (#e2e8f0). Below the cards, a simple horizontal bar chart with three bars showing Q1, Q2, Q3 revenue growth. Clean Inter font family throughout. No decorative elements, no icons, no gradients. Professional, minimal, corporate. Suitable for embedding in a printed business document.",
  "negative_prompt": "dark background, neon colors, 3D effects, gradients, icons, clip art, decorative borders, watermarks, stock photo elements",
  "settings": {
    "resolution": "2K",
    "style": "minimal corporate infographic",
    "lighting": "flat, even",
    "quality": "crisp text rendering, print-ready, clean edges"
  }
}
```

### Hero/Header Images

Best for: cover pages, section openers, chapter headers.

Key prompt elements:
- Leave space for text overlay (specify which area should be clear)
- Match the brand palette exactly (pass hex codes)
- Request horizontal compositions that fit the page width
- Ask for subtle, non-competing backgrounds

```json
{
  "prompt": "Abstract professional header background for a construction bid document. Wide horizontal composition. Deep navy (#0D1B2A) gradient on the left third transitioning to clean white on the right two-thirds. Subtle geometric architectural line work -- thin blueprint-style grid lines at 8% opacity overlaid on the navy section. A single diagonal accent line in medium blue (#2B5EA7) crossing from lower-left to upper-right at 20% opacity. The right two-thirds should be nearly pure white (#f8fafc) to allow text overlay. Matte finish, no glossy or metallic effects. Professional, understated, sophisticated.",
  "negative_prompt": "busy patterns, construction photos, tools, hard hats, bright colors, clip art, 3D renders, glossy surfaces, text, logos",
  "settings": {
    "resolution": "2K",
    "style": "modern corporate design",
    "lighting": "flat ambient",
    "quality": "smooth gradients, print-ready, no banding"
  }
}
```

### Process Diagrams

Best for: project timelines, methodology overviews, workflow explanations.

Key prompt elements:
- Number the steps explicitly
- Use directional flow (left-to-right or top-to-bottom)
- Keep text short and specify it exactly
- Request clear connecting lines or arrows between steps

```json
{
  "prompt": "Clean process flow diagram on white background showing 4 project phases connected by a thin blue (#2B5EA7) horizontal arrow line. Phase 1: navy (#0D1B2A) circle with white '1' inside, labeled 'Discovery' below in dark gray (#1f2937). Phase 2: circle with '2', labeled 'Design'. Phase 3: circle with '3', labeled 'Build'. Phase 4: circle with '4', labeled 'Deliver'. Each circle is 60px diameter with 2px border. Below each label, a short descriptor in light gray (#64748b): 'Weeks 1-2', 'Weeks 3-4', 'Weeks 5-8', 'Week 9'. Equal spacing between phases. Clean sans-serif font. No decorative elements. White background. Suitable for a printed business proposal at 300 DPI.",
  "negative_prompt": "3D, isometric, icons, illustrations, busy backgrounds, gradients, shadows, decorative elements, stock imagery",
  "settings": {
    "resolution": "2K",
    "style": "flat diagram, corporate",
    "lighting": "flat",
    "quality": "vector-like precision, sharp text, print-ready"
  }
}
```

### Comparison Visuals

Best for: before/after scenarios, competitive analysis, feature matrices.

```json
{
  "prompt": "Side-by-side comparison graphic for a business document. White background. Left panel labeled 'Before' in red-tinted gray (#92400e) at the top, right panel labeled 'After' in navy (#0D1B2A). A thin vertical divider line (#e2e8f0) separates the two panels. Left panel: disorganized scattered document icons in muted gray tones suggesting chaos. Right panel: neatly organized stacked document icons with blue (#2B5EA7) accent suggesting order and structure. Below each panel, a clean stat: left shows 'Manual: 12 hours/week' in gray, right shows 'Automated: 45 min/week' in blue. Minimal, professional, corporate style. Clean edges, no gradients.",
  "negative_prompt": "photographs, 3D renders, complex illustrations, decorative borders, neon, dark background",
  "settings": {
    "resolution": "2K",
    "style": "flat corporate illustration",
    "lighting": "flat",
    "quality": "clean, minimal, print-ready"
  }
}
```

## Image Specs for PDF Embedding

### Resolution by Tier

| Tier | Target DPI | Minimum DPI | Notes |
|------|-----------|-------------|-------|
| Desktop | 150 | 96 | Screen/email viewing. 150 DPI is sharp on retina. |
| Digital Press | 300 | 200 | Short-run print. 300 DPI is the standard. |
| Commercial Offset | 300 | 300 | No shortcuts here. 300 DPI minimum for offset. |

When generating with Nano Banana 2, use the `image_size` argument to control resolution:
- `"512px"` -- adequate for small decorative elements at desktop tier
- `"1K"` -- adequate for half-width images at desktop tier
- `"2K"` -- safe default for most PDF visuals across all tiers
- `"4K"` -- use for full-bleed cover images or large infographics destined for print

### Aspect Ratios for Common Placements

| Placement | Aspect Ratio | Use Case |
|-----------|-------------|----------|
| Full-width header | `17:5` | Page-wide header bars, cover page heroes |
| Full-width content | `16:9` | Section infographics, comparison panels |
| Half-width sidebar | `4:3` | Side-by-side layouts, inset graphics |
| Square callout | `1:1` | Metric cards, portrait inserts, icons |
| Tall sidebar | `3:4` | Vertical sidebars, full-page backgrounds |
| Full-page bleed | `17:22` | Cover page backgrounds (letter, portrait) |

Pass the aspect ratio as the third argument to `generate_image.py`:

```bash
python generate_image.py prompt.json output.png "16:9" "2K"
```

### File Format

- **PNG** for graphics, diagrams, infographics, anything with text or sharp edges
- **JPG** for photographic content only (hero images with photorealistic textures)
- Nano Banana 2 outputs PNG by default. Specify the output filename accordingly.

### File Size Limits

Keep individual images under 2MB for reasonable PDF file sizes. Guidelines:

| Image Type | Target Size | Max Size |
|-----------|------------|----------|
| Decorative element | < 200 KB | 500 KB |
| Half-width graphic | < 500 KB | 1 MB |
| Full-width infographic | < 1 MB | 2 MB |
| Full-page cover | < 1.5 MB | 2 MB |

If a generated image exceeds 2MB, compress with ImageMagick:

```bash
# Reduce quality while maintaining dimensions
convert assets/large-image.png -quality 85 assets/large-image.png

# Or resize if the image is larger than needed
convert assets/large-image.png -resize 2400x1350 assets/large-image.png
```

### Naming Convention

Use descriptive kebab-case names that indicate both content and placement:

```
assets/
  hero-header.png           # Cover page header background
  process-flow-4step.png    # 4-step process diagram
  kpi-dashboard-q3.png      # Q3 KPI infographic panel
  comparison-before-after.png
  section-divider-navy.png  # Decorative section divider
  market-tam-sam-som.png    # TAM/SAM/SOM visualization
```

## Styling Consistency

### Match Brand Colors

Read `brand-kit.yaml` before writing any prompt. Pass the exact hex codes into the prompt text.

```python
# In your agent workflow, extract colors from brand-kit.yaml:
import yaml

with open("brand-kit.yaml") as f:
    brand = yaml.safe_load(f)

primary = brand["colors"]["primary"]       # e.g., "#0D1B2A"
secondary = brand["colors"]["secondary"]   # e.g., "#2B5EA7"
accent = brand["colors"]["accent"]         # e.g., "#3B7DD8"
neutral_dark = brand["colors"]["neutral-dark"]
neutral_light = brand["colors"]["neutral-light"]
```

Then inject these into the prompt:

```
"...navy background in ({primary}) with accent lines in ({secondary})
and body text areas in ({neutral_light})..."
```

Never say "blue" or "navy" without the hex code. The model needs exact values to match the document's CSS.

### Match Typography

WeasyPrint auto-embeds Google Fonts. If the brand kit uses Inter, include this in generation prompts:

```
"Clean sans-serif font resembling Inter throughout. Regular weight for
body, bold for headings."
```

Gemini cannot guarantee exact font rendering, but specifying a sans-serif family and weight produces visually compatible output. For critical text, render it in HTML/CSS instead of baking it into the generated image.

### Match Visual Treatment

If the document uses specific design patterns, carry them into generated visuals:

| Document Style | Prompt Instruction |
|---------------|-------------------|
| Rounded corners on cards | "Rounded rectangle containers with 8px corner radius" |
| Subtle drop shadows | "Minimal drop shadow on card elements, 2px offset, 10% opacity" |
| No shadows (flat) | "No drop shadows, flat design, 2D only" |
| Bordered sections | "Thin 1px border in (#e2e8f0) around each panel" |
| Gradient headers | "Linear gradient from (#0D1B2A) to (#2B5EA7) left to right" |

## Fallback Strategy

When Nano Banana is unavailable (API key missing, quota exceeded, network error), every generated visual type has an HTML/CSS fallback.

### Check Availability First

```bash
# Quick test: can we reach the Gemini API?
python -c "
import subprocess, sys
result = subprocess.run(
    ['/opt/homebrew/bin/op', 'read',
     'op://Gigawatt-Secrets/Google Gemini API Credentials/credential'],
    capture_output=True, text=True, timeout=10
)
if result.returncode != 0:
    print('UNAVAILABLE: 1Password cannot retrieve Gemini API key')
    sys.exit(1)
print('OK: Gemini API key available')
"
```

### CSS Fallback: Metric Cards

Instead of a generated infographic, render metric cards directly in HTML:

```html
<div class="metrics-row">
  <div class="metric-card">
    <div class="metric-value">$2.4M</div>
    <div class="metric-label">Annual Revenue</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">156</div>
    <div class="metric-label">Active Clients</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">99.7%</div>
    <div class="metric-label">Uptime SLA</div>
  </div>
</div>
```

```css
.metrics-row {
  display: flex;
  gap: 16pt;
  margin: 12pt 0;
}
.metric-card {
  flex: 1;
  text-align: center;
  padding: 16pt 12pt;
  background: var(--neutral-light);
  border: 0.5pt solid var(--neutral-border);
  border-radius: 6pt;
}
.metric-value {
  font-size: 28pt;
  font-weight: 700;
  color: var(--primary);
  line-height: 1.1;
}
.metric-label {
  font-size: 9pt;
  color: var(--neutral-mid);
  margin-top: 4pt;
}
```

### CSS Fallback: Bar Chart

```html
<div class="bar-chart">
  <div class="bar-row">
    <span class="bar-label">Q1</span>
    <div class="bar-track"><div class="bar-fill" style="width: 65%;"></div></div>
    <span class="bar-value">$650K</span>
  </div>
  <div class="bar-row">
    <span class="bar-label">Q2</span>
    <div class="bar-track"><div class="bar-fill" style="width: 80%;"></div></div>
    <span class="bar-value">$800K</span>
  </div>
  <div class="bar-row">
    <span class="bar-label">Q3</span>
    <div class="bar-track"><div class="bar-fill" style="width: 95%;"></div></div>
    <span class="bar-value">$950K</span>
  </div>
</div>
```

```css
.bar-chart { margin: 12pt 0; }
.bar-row {
  display: flex;
  align-items: center;
  gap: 8pt;
  margin-bottom: 6pt;
}
.bar-label {
  width: 24pt;
  font-size: 9pt;
  color: var(--neutral-mid);
  text-align: right;
}
.bar-track {
  flex: 1;
  height: 14pt;
  background: var(--neutral-light);
  border-radius: 3pt;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--secondary);
  border-radius: 3pt;
}
.bar-value {
  width: 48pt;
  font-size: 9pt;
  font-weight: 600;
  color: var(--neutral-dark);
}
```

### CSS Fallback: Header Background

Replace a generated hero image with a CSS gradient:

```html
<div class="hero-header">
  <h1>{{ project.name }}</h1>
  <p class="subtitle">{{ project.tagline }}</p>
</div>
```

```css
.hero-header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 60%, var(--neutral-light) 100%);
  color: white;
  padding: 48pt 36pt;
  margin: -0.6in -0.7in 24pt -0.7in; /* bleed to page edges */
  width: calc(100% + 1.4in);
}
```

### CSS Fallback: Process Flow

```html
<div class="process-flow">
  {% for phase in execution.phases %}
  <div class="process-step">
    <div class="step-number">{{ loop.index }}</div>
    <div class="step-name">{{ phase.name }}</div>
    <div class="step-duration">{{ phase.duration_weeks }} weeks</div>
  </div>
  {% if not loop.last %}<div class="step-arrow">&#8594;</div>{% endif %}
  {% endfor %}
</div>
```

```css
.process-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8pt;
  margin: 16pt 0;
}
.process-step { text-align: center; }
.step-number {
  width: 28pt;
  height: 28pt;
  line-height: 28pt;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-weight: 700;
  font-size: 12pt;
  margin: 0 auto 4pt;
}
.step-name {
  font-size: 10pt;
  font-weight: 600;
  color: var(--neutral-dark);
}
.step-duration {
  font-size: 8pt;
  color: var(--neutral-mid);
}
.step-arrow {
  font-size: 16pt;
  color: var(--secondary);
  padding-bottom: 16pt;
}
```

### CSS Fallback: Section Divider

```css
.section-divider {
  height: 3pt;
  background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 40%, transparent 100%);
  margin: 18pt 0;
  border: none;
}
```

### Fallback Capability Matrix

| Visual Type | AI Generation | CSS Fallback | Quality Delta |
|------------|--------------|-------------|--------------|
| Metric cards | Optional | Full | CSS is actually better (crisper text) |
| Bar/progress charts | Optional | Full | CSS is equivalent |
| Pie/donut charts | Recommended | Partial (CSS conic-gradient) | AI adds polish |
| Process flows | Optional | Full | CSS handles 3-6 steps well |
| Header backgrounds | Recommended | Full (gradients) | AI adds texture/depth |
| Infographic panels | Recommended | Partial (layout only) | AI adds visual richness |
| Comparison visuals | Recommended | Partial | AI handles metaphor better |
| Section dividers | Optional | Full | CSS gradients work great |
| Photo-realistic imagery | Required | None | No CSS substitute exists |

## Choosing Between /nano-banana-2 and /bananas

Both skills generate images via Google Gemini, but they serve different purposes.

### /nano-banana-2

- **Format:** Dense Narrative or Structured JSON prompt
- **Best for:** Individual graphics, hero images, backgrounds, diagrams
- **Generates directly:** Prompt JSON in, PNG/JPG out
- **Use for bangerpdf:** This is the primary tool for PDF visuals

### /bananas

- **Format:** BANANAS 7-Layer Prompt Architecture
- **Best for:** Complex infographics with precise text, data callouts, brand identity integration
- **Output:** A polished prompt ready for Google AI Studio or direct API call
- **Use for bangerpdf:** When the visual needs precise text rendering, specific typography hierarchy, and structured data presentation -- especially data-dense infographics

For most bangerpdf work, `/nano-banana-2` with Dense Narrative format is sufficient. Reach for `/bananas` when you need the full 7-layer treatment for a complex, text-heavy infographic.

## Default Visual Generation by Vibe

Each vibe has different expectations for visual content. Follow these defaults unless the user explicitly overrides.

### Bold Vibe
Visual generation is the **DEFAULT**. Do NOT ask permission -- just generate.

Minimum visual set:
- **1 hero/cover image** -- full-bleed background for the cover page
- **Product photography or lifestyle imagery** -- at least 2-3 images showing the product/service in context
- **1 section divider image** -- atmospheric or branded, placed between major content sections

Use Nano Banana 2 for hero images and lifestyle scenes. Download real product photography from manufacturer CDNs when available (SanMar, SS Activewear, etc.).

### Editorial Vibe
Generate **1-2 selective, high-quality images**. Fewer but more refined.

- One hero image (subtle, editorial treatment -- desaturated, tight crop)
- One optional interior image per spread
- All generated images should be muted in color, high contrast, and feel "curated" rather than "stock"
- When in doubt, skip the image. Whitespace is the visual element.

### Corporate Vibe
**CSS-only visuals** by default. Build charts via HTML tables, metric cards via flexbox, accent bars via CSS.

- Only generate images if the user specifically requests them
- Prefer data visualizations rendered in HTML/CSS (crisper text, resolution-independent)
- If an infographic is truly needed, use the BANANAS 7-layer architecture for maximum precision

### Minimal Vibe
**No generated images.** Whitespace IS the visual element.

- Zero image generation unless the user insists
- If they insist, limit to one hero image maximum
- All other visual elements must be CSS-only (thin rules, accent color on one element)

## BANANAS 7-Layer Prompt Integration

When generating complex visuals (infographics, data panels, styled charts, product mockups), use the BANANAS 7-layer prompt architecture for maximum control over output quality.

### The 7 Layers

1. **Context/Purpose** -- Who sees this document? What is it about? What feeling should the visual evoke?
2. **Image Type** -- Infographic, hero background, product mockup, data visualization, section divider, comparison panel
3. **Subject/Content** -- Exact text strings, numbers, data points, product names. Be literal -- Gemini renders text you specify.
4. **Composition** -- Aspect ratio, layout structure (centered, left-heavy, grid), reading flow direction
5. **Action/Flow** -- How the viewer's eye moves through the image. Left-to-right for timelines, top-to-bottom for hierarchies, Z-pattern for dashboards.
6. **Location/Setting** -- Background color/texture, atmospheric elements, environmental context
7. **Style/Technical** -- Colors (from brand-kit.yaml hex codes), typography style, resolution, matte vs glossy, flat vs dimensional

### Concrete Example: Product Mockup

Generating an AI Build Lab logo embroidered on a Carhartt K87 pocket tee:

```json
{
  "prompt": "Product mockup photograph of a Carhartt K87 Workwear Pocket T-Shirt in desert color (#DEB887). The shirt is laid flat on a clean white background. On the left chest pocket, a small embroidered logo reading 'AI Build Lab' in navy thread (#1A1A2E) with a subtle circuit-board pattern below the text in gold thread (#F5A600). The embroidery is 2.5 inches wide, realistic thread texture visible at close inspection. Clean product photography lighting, slight shadow beneath the shirt, no wrinkles, no background distractions. Shot from directly above (flat lay). The Carhartt logo tag is visible on the pocket.",
  "negative_prompt": "wrinkled, messy, dark background, people wearing the shirt, mannequin, clip art, illustration, cartoon, text overlay, watermark",
  "settings": {
    "resolution": "2K",
    "style": "product photography, flat lay, e-commerce",
    "lighting": "soft studio lighting, slight shadow, white background",
    "quality": "crisp detail, print-ready, realistic fabric texture"
  }
}
```

Pass brand colors from `brand-kit.yaml` directly into the prompt as hex codes. Never say "blue" without the hex value.

### When to Use BANANAS vs Simple Prompts

| Visual Complexity | Approach |
|-------------------|----------|
| Simple background/texture | Nano Banana 2 with a 2-3 sentence prompt |
| Hero image with specific composition | Nano Banana 2 with Dense Narrative (5-8 sentences) |
| Infographic with text + data + branding | BANANAS 7-layer architecture |
| Product mockup with brand placement | BANANAS 7-layer architecture |
| Multi-panel comparison | BANANAS 7-layer architecture |

## Seed Image Patterns

When the user provides reference images (existing logo, product photo, design inspiration), use them as inputs to guide generation.

### Passing Reference Images

Nano Banana 2 supports an `image_input` parameter for reference-image-driven generation:

```bash
python ~/.claude/skills/nano-banana-2/generate_image.py \
  /tmp/mockup-prompt.json \
  ./assets/logo-on-shirt.png \
  "4:3" "2K" \
  --image-input ./assets/company-logo.png
```

### Common Seed Image Patterns

| Pattern | User Provides | Generation Output |
|---------|--------------|-------------------|
| Logo placement mockup | Company logo PNG/SVG | Logo embroidered/printed on product |
| Style transfer | Design inspiration screenshot | New image matching that visual style |
| Brand-consistent hero | Brand guide or existing collateral | Hero image using same color/typography feel |
| Product variation | One product photo | Same product in different colors/angles |

### Best Practices for Reference Images

- **Logo files:** Provide the highest resolution available. SVG is ideal, PNG with transparency is good. JPG with white background works but may bleed edges.
- **Style references:** Crop to the specific element you want to transfer (the color palette, the layout style, the photographic treatment -- not the whole page).
- **Product photos:** Use clean product-only shots (no lifestyle context) when generating mockups. The model needs to isolate the product from the background.
- **Design inspo:** Multiple reference images are better than one. Provide 2-3 showing different aspects of the target style.

## Complete Example: Bid Package with Generated Visuals

```bash
# 1. Scaffold the pack
bangerpdf init bid-package ./wilson-bid --brand "Wilson Electric" --primary "#1B4332"
cd ./wilson-bid

# 2. Create assets directory
mkdir -p assets

# 3. Read brand colors
cat brand-kit.yaml
# -> primary: "#1B4332", secondary/accent as configured

# 4. Generate a cover page header
cat > /tmp/cover-prompt.json << 'PROMPT'
{
  "prompt": "Professional cover page header background for an electrical contractor bid document. Wide horizontal composition. Deep forest green (#1B4332) on the left 40% with subtle electrical circuit trace patterns at 10% opacity. Clean transition to white (#f8fafc) on the right 60%. Thin accent line in medium green along the transition boundary. Matte finish, corporate, sophisticated. No text, no people, no photos of electrical work. Abstract and clean.",
  "negative_prompt": "text, logos, people, tools, wires, bright colors, neon, 3D, busy patterns",
  "settings": {
    "resolution": "2K",
    "style": "modern corporate design",
    "lighting": "flat ambient",
    "quality": "smooth gradients, print-ready"
  }
}
PROMPT

python ~/.claude/skills/nano-banana-2/generate_image.py \
  /tmp/cover-prompt.json \
  ./assets/cover-header.png \
  "17:5" "2K"

# 5. Generate a project timeline visual
cat > /tmp/timeline-prompt.json << 'PROMPT'
{
  "prompt": "Clean horizontal project timeline for a construction bid. White background. Four phases from left to right connected by a thin green (#1B4332) line: Phase 1 'Rough-In' (Weeks 1-3), Phase 2 'Wiring' (Weeks 4-6), Phase 3 'Fixtures' (Weeks 7-8), Phase 4 'Final Test' (Week 9). Each phase is a circle with the phase number inside, labeled below. Current progress marker at Phase 1. Professional, minimal, suitable for a printed business proposal. Sans-serif font, clean edges.",
  "negative_prompt": "3D, isometric, decorative, busy, photos, clip art",
  "settings": {
    "resolution": "2K",
    "style": "flat corporate diagram",
    "lighting": "flat",
    "quality": "crisp text, vector-like edges"
  }
}
PROMPT

python ~/.claude/skills/nano-banana-2/generate_image.py \
  /tmp/timeline-prompt.json \
  ./assets/project-timeline.png \
  "16:9" "2K"

# 6. Reference in templates
# In templates/01_cover_letter.html:
#   <img src="assets/cover-header.png" class="cover-hero">
#
# In templates/02_proposal.html:
#   <img src="assets/project-timeline.png" class="timeline-img">

# 7. Build and verify
bangerpdf build --tier all
bangerpdf qa pdfs/desktop/ --strict

# 8. Clean up temp files
rm -f /tmp/cover-prompt.json /tmp/timeline-prompt.json
```
