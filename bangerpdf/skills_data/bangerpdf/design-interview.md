---
name: bangerpdf/design-interview
description: >
  Structured design interview for new bangerpdf document projects. Run this
  BEFORE building any document. Asks 5 questions to determine audience, purpose,
  visual style, brand assets, and design references. Outputs design-brief.yaml.
---

# bangerpdf -- Design Interview

Most people cannot tell you what they want a document to look like. They know when something looks wrong, but they cannot articulate "full-bleed editorial look-book with lifestyle photography and a warm color palette." That gap between vision and vocabulary is where bad PDFs come from.

This interview bridges that gap. Five questions, asked in order, that translate a user's fuzzy intent into a concrete design brief. The output is `design-brief.yaml` -- a structured file that the rest of the bangerpdf pipeline consumes to make every downstream decision (pack selection, brand colors, typography, layout style, visual generation strategy).

**Rule: For NEW document projects, ALWAYS begin with the Design Interview.** The only exceptions are listed at the bottom of this file.

## How This Fits the Workflow

The SKILL.md workflow references this as Step 1:

```
Step 1: Design Interview  <-- YOU ARE HERE
Step 2: Brand Discovery
Step 3: Vibe Selection
Step 4: Layout + Template
Step 5: Visual Generation
Step 6: Build
Step 7: QA
Step 8: Save Brand
```

The interview feeds directly into Steps 2-3. Question 4 can trigger the `brand-discovery.md` pipeline. Question 3 determines the vibe, which controls CSS patterns, font pairings, and visual generation defaults.

## The 5 Questions

Ask these in order. Each question builds on the previous answer.

### Question 1: WHO

**Ask:** "Who receives this document? Tell me about the recipient."

**What you need to extract:**
- **Client/recipient name** -- the actual person or company who reads this
- **Their industry** -- construction, healthcare, tech, nonprofit, etc.
- **Formality level** -- are they a Fortune 500 board or a local contractor?
- **Relationship** -- cold outreach, existing client, internal team?

**Why it matters:** A bid for a hospital system looks nothing like a proposal for a local landscaper. The recipient's expectations dictate every design choice. A healthcare client expects clinical precision and conservative color. A creative agency expects bold typography and editorial flair. Get this wrong and the document fails before the reader hits page 2.

**Guidance for the agent:**
- If the user says "my client," ask for specifics. "Client" means nothing without context.
- Industry is the single strongest predictor of appropriate design. A construction bid should feel solid and workmanlike, not flashy.
- Formality level determines font choice, color palette restraint, and whether you use lifestyle photography or clean diagrams.

**Example responses and what they imply:**
- "It's for Carhartt's corporate purchasing team" -> Bold vibe, workwear imagery, warm earthy tones, professional but not stuffy
- "A hospital board evaluating construction bids" -> Corporate vibe, conservative, data-forward, zero decorative elements
- "My friend who runs a coffee shop" -> Minimal or Editorial vibe, relaxed, friendly typography

### Question 2: WHAT

**Ask:** "What is this document's job? What should the reader DO after reading it?"

**What you need to extract:**
- **Primary purpose** -- one of these four:
  - **Sell / Persuade** -- proposals, bids, pitch decks, sales one-pagers
  - **Inform / Report** -- annual reports, briefings, white papers, research
  - **Celebrate / Recognize** -- certificates, awards, event programs
  - **Request / Propose** -- RFPs, grant applications, internal requests
- **Call to action** -- what specific action should the reader take?
- **Document scope** -- single page, 5-page proposal, 20-page report?

**Why it matters:** Purpose determines structure. A bid package needs a hero amount, schedule of values, and signature block. A report needs table of contents, data visualizations, and citations. A certificate needs centered layout, generous margins, and the recipient's name as the largest element on the page.

**Guidance for the agent:**
- If the user says "I need a PDF," that is not enough. Push for the job-to-be-done.
- The call to action determines the final page layout. "Sign and return" means a signature block. "Schedule a meeting" means contact info and a CTA.
- Document scope determines pack selection. 1 page = one-pager pack. 3-5 pages = proposal-package. 5+ with multiple docs = bid-package.

### Question 3: VIBE

**Ask:** "Which of these best describes the look you want? Pick one, or describe your own."

**Present these options:**

| Vibe | Description |
|------|-------------|
| **Corporate** | Clean, authoritative, blue-gray palette, Inter/Helvetica, data-forward. Think: McKinsey deck, annual report, compliance document. Maximum professionalism, minimal decoration. |
| **Bold** | Full-bleed imagery, lifestyle photos, strong color blocks, magazine feel. Think: Nike brand book, Carhartt catalog, outdoor brand lookbook. Visual-first, emotional impact. |
| **Editorial** | Serif headings, generous whitespace, refined typography, thought-leadership feel. Think: Harvard Business Review, premium consulting report, architect portfolio. Elegant restraint. |
| **Minimal** | Maximum whitespace, single accent color, ultra-clean, modernist. Think: Apple product sheet, Scandinavian design, freelancer invoice. Less is more, aggressively. |
| **Custom** | "Describe what you're envisioning and I'll translate it into design choices." |

**What you need to extract:**
- The selected vibe (or enough description to map to one)
- Any specific references ("like Apple but warmer," "industrial but not boring")
- Color preferences if they have any ("our brand is green," "I hate blue")

**Why it matters:** The vibe determines every CSS decision downstream:
- **Corporate** -> Inter/Helvetica, blue-gray palette, 12-column grid, data tables, minimal imagery
- **Bold** -> Strong sans-serif, warm/saturated palette, full-bleed covers, lifestyle photography, named @page rules for bleed pages
- **Editorial** -> Playfair Display/Source Sans Pro, muted palette, single column, generous margins, pull quotes
- **Minimal** -> DM Sans/Inter, single accent + neutrals, maximum whitespace, no decorative elements

**Guidance for the agent:**
- Most users will not pick "Editorial" by name. They will say things like "classy" or "high-end" or "like a magazine." Map their language to the right vibe.
- If they pick "Custom," ask for a URL or screenshot of something they like. This feeds into Question 5.
- Never let a user skip this question. The vibe is the backbone of every design decision.

### Question 4: ASSETS

**Ask:** "Do you have brand materials -- a logo, brand colors, fonts? Or give me a website URL and I'll auto-discover your brand."

**What you need to extract:**
- **Logo file** -- path to SVG, PNG, or PDF of the logo
- **Brand colors** -- specific hex codes, or "use whatever's on our website"
- **Brand fonts** -- if they know them, great; if not, we'll discover or choose
- **Existing brand guidelines** -- PDF or URL to a style guide
- **Website URL** -- for automated brand discovery

**Why it matters:** Brand consistency is non-negotiable. If the client's website is forest green and the proposal shows up in cobalt blue, you have lost credibility before page 1.

**Proactive offer:** Always say this:

> "Give me a website URL and I'll auto-discover your brand colors, fonts, and logo. Takes about 30 seconds."

If they provide a URL, trigger the `brand-discovery.md` pipeline. That skill handles Brand Fetch API, web scraping, and manual research to populate `brand-kit.yaml` automatically.

**Guidance for the agent:**
- If they have no brand materials and no website, that is fine. Pick a palette that matches the vibe from Question 3 and the industry from Question 1.
- If they provide a logo file, verify it is high enough resolution for print (vector SVG preferred, PNG at 600px+ width minimum).
- If they say "just use our colors" without providing them, ask for the URL. Do not guess.

### Question 5: REFERENCES

**Ask:** "Are there any documents or designs you love? A URL, a screenshot, or even 'something like what Apple does' helps me dial in the style."

**What you need to extract:**
- **URLs** -- websites, PDFs, design portfolios
- **Screenshots** -- photos of documents they admire
- **Verbal descriptions** -- "clean like Stripe's docs" or "bold like a Nike ad"
- **Anti-references** -- "NOT like a boring government form"

**Why it matters:** References eliminate ambiguity. "Modern and clean" means wildly different things to different people. A reference image pins it down to a specific execution. Anti-references are equally valuable -- knowing what they hate prevents the most painful revision cycles.

**Proactive offer:**

> "If you have a URL or screenshot, I can analyze it and extract the design patterns -- layout grid, typography, color usage, spacing rhythm."

**Guidance for the agent:**
- If they provide a URL, fetch it and analyze: What is the dominant color? How much whitespace? Serif or sans-serif? How dense is the content? What is the visual hierarchy?
- If they provide a screenshot, describe what you see and confirm your read with the user.
- If they say "I don't know, just make it look good," that is what the vibe system is for. Default to the vibe from Question 3 and move on.
- This question is optional. If Questions 1-4 gave you enough, do not force it.

## Output: design-brief.yaml

After the interview, generate this file in the project root:

```yaml
# design-brief.yaml -- Generated by bangerpdf design interview
# This file drives all downstream design decisions.

recipient:
  name: "Atria Senior Living"
  industry: "Healthcare / Senior Living"
  formality: "high"
  relationship: "new-client"

purpose:
  type: "sell"  # sell | inform | celebrate | request
  action: "Award the contract to Wilson Mechanical"
  scope: "multi-document"  # single-page | multi-page | multi-document
  estimated_pages: 15

vibe: "bold"  # corporate | bold | editorial | minimal | custom
vibe_notes: "Lifestyle imagery of workwear in action, warm earth tones, magazine feel"

brand:
  discovered_from: "https://carhartt.com"
  logo_path: "assets/logo.png"
  primary: "#B77729"
  accent: "#F5A600"
  neutral_dark: "#1A1A1A"
  neutral_light: "#F5F1EB"
  fonts:
    heading: "Helvetica Neue"
    body: "Helvetica Neue"

references:
  - type: "url"
    value: "https://carhartt.com/company-gear"
    notes: "Full-bleed hero photography, minimal text overlay, warm palette"
  - type: "verbal"
    value: "Like a Patagonia catalog but for construction"

pack_recommendation: "bid-package"
tier_recommendation: "desktop"
visual_generation: true  # Whether to generate images with Nano Banana
```

### Schema Rules

- `recipient.formality` -- one of: `low`, `medium`, `high`
- `recipient.relationship` -- one of: `new-client`, `existing-client`, `internal`, `cold-outreach`
- `purpose.type` -- one of: `sell`, `inform`, `celebrate`, `request`
- `purpose.scope` -- one of: `single-page`, `multi-page`, `multi-document`
- `vibe` -- one of: `corporate`, `bold`, `editorial`, `minimal`, `custom`
- `visual_generation` -- boolean, defaults to `true` for Bold/Editorial, `false` for Corporate/Minimal

### Mapping Vibe to Pack and Tier Defaults

| Vibe | Default Pack | Default Tier | Visual Generation |
|------|-------------|-------------|-------------------|
| Corporate | proposal-package or report-package | desktop | No (CSS-only) |
| Bold | bid-package | all (desktop + digital-press) | Yes |
| Editorial | report-package or briefing-package | desktop | Optional |
| Minimal | one-pager or invoice | desktop | No (CSS-only) |

These are defaults. The user can override any of them.

## When to SKIP the Interview

Skip or abbreviate the interview when:

1. **User says "just build it"** -- they have a clear vision and do not want to be interviewed. Respect this. Ask only: "Quick -- what vibe? Corporate, Bold, Editorial, or Minimal?" Then proceed.

2. **User provides complete specs** -- they hand you a design-brief.yaml, a brand-kit.yaml, or enough detail that the 5 questions are already answered. Confirm your understanding and proceed.

3. **Saved brand exists** -- the user says "use the Carhartt brand I saved last time." Load it from `~/.config/bangerpdf/brands/carhartt/` via the `design-memory.md` system and skip to build.

4. **Simple conversion** -- they just want an HTML file turned into a PDF. No design decisions needed. Run `bangerpdf convert` directly.

5. **Iteration on existing project** -- they are revising a document that already has a design-brief.yaml. Read the existing brief and ask only what changed.

Even in skip scenarios, always read the existing brand-kit.yaml and design-taste.md before building. The interview can be skipped; the design system cannot.

## Interview Tips for the Agent

**Pacing:** Ask one question at a time. Do not dump all 5 questions in a wall of text. Wait for the answer before moving on.

**Adaptive depth:** If the user is a designer who says "Editorial vibe, Playfair Display headings, #2C3E50 primary, single-column with pull quotes," you do not need to explain what Editorial means. Match their level of sophistication.

**Default to action:** If the user is vague, make a recommendation and confirm:

> "Based on what you've told me -- healthcare client, formal relationship, bid document -- I'd recommend the Corporate vibe with a blue-gray palette. Want me to go with that, or would you prefer something warmer?"

**Never stall:** If a question gets a "I don't know" response, pick the most reasonable default and move on. You can always iterate after the first build. Getting something in front of the user is worth more than perfect planning.

**Save the brief:** After generating design-brief.yaml, offer to save the brand for reuse:

> "Want me to save this brand profile so next time you build for [client], it's instant?"

This feeds into the `design-memory.md` system.

## Cross-References

- `SKILL.md` -- the master workflow that calls this as Step 1
- `brand-discovery.md` -- triggered by Question 4 when the user provides a URL
- `design-taste.md` -- the design system that constrains all styling decisions
- `design-memory.md` -- saves interview results and brand profiles for reuse
- `weasyprint-cookbook.md` -- consult when building the CSS after the interview
