---
name: bangerpdf/design-memory
description: >
  Save and reuse brand profiles, design preferences, and project templates
  across bangerpdf projects. Enables "build once, reuse forever" workflow.
  Global preferences persist across all projects.
---

# bangerpdf -- Design Memory

You should never have to configure the same brand twice. The first time you build a document for Carhartt, you do the design interview, discover the brand, tweak the colors, iterate on the layout, and arrive at something the user approves. The second time you build for Carhartt, all of that should be instant -- load the saved brand, pick a pack, build.

Design memory makes this possible. It saves brand profiles, design preferences, and style decisions to disk so they persist across projects and sessions.

## The "Lock It In" Concept

Every brand goes through a refinement cycle:

```
Discover -> Build -> Review -> Adjust -> Review -> Approve -> LOCK IT IN
```

"Lock It In" means: this brand profile is done. The colors are right, the fonts are right, the logo is the right file, the vibe is dialed. Save it so the next project with this client starts from perfection instead of from scratch.

**When to offer to save:** After a successful build that the user approves, proactively ask:

> "This looks great. Want me to save this brand profile for [client name] so next time it's instant?"

Never save without asking. The user might be experimenting and not want to persist a half-baked brand.

## Storage Layout

All design memory lives in `~/.config/bangerpdf/`. This directory is created automatically on first use.

```
~/.config/bangerpdf/
  preferences.yaml              # Global defaults (vibe, fonts, etc.)
  brands/
    carhartt/
      brand-kit.yaml            # Full brand identity
      design-brief.yaml         # Interview results from the first project
      assets/
        logo.png                # Saved logo file
        logo.svg                # Vector version if available
      custom-styles.css         # Any CSS overrides specific to this brand
    wilson-mechanical/
      brand-kit.yaml
      design-brief.yaml
      assets/
        logo.svg
      custom-styles.css
    acme-plumbing/
      ...
```

### Saved Brands (`~/.config/bangerpdf/brands/<name>/`)

Each saved brand is a self-contained directory with everything needed to fully configure a new project:

| File | Purpose | Required |
|------|---------|----------|
| `brand-kit.yaml` | Colors, fonts, logo path, brand name | Yes |
| `design-brief.yaml` | The interview results that produced this brand | No (nice to have) |
| `assets/` | Logo, any brand imagery | No (logo is strongly recommended) |
| `custom-styles.css` | CSS overrides for this specific brand | No |

**brand-kit.yaml** is the only required file. Everything else is supplementary context that makes future projects faster and more consistent.

**custom-styles.css** is for edge cases: a brand that needs a specific heading style, a non-standard table treatment, or a CSS workaround for a WeasyPrint rendering quirk. It gets injected after the pack's default styles and before any project-specific overrides.

### Global Preferences (`~/.config/bangerpdf/preferences.yaml`)

Global preferences are defaults that apply to every new project unless overridden. They answer the question: "When nothing else is specified, what should bangerpdf do?"

```yaml
# ~/.config/bangerpdf/preferences.yaml
# Global defaults for all bangerpdf projects.

# Design defaults
default_vibe: "bold"                    # corporate | bold | editorial | minimal
default_tier: "desktop"                 # desktop | digital-press | commercial | all
default_font_heading: "Inter"           # Google Font name
default_font_body: "Inter"              # Google Font name
default_accent: "#0D9488"               # Hex color for accent when no brand is loaded

# Workflow defaults
auto_interview: true                    # Run the design interview for new projects
auto_visual_generation: true            # Generate images for visual vibes (Bold/Editorial)
always_full_bleed_covers: true          # Use full-bleed cover pages by default

# Layout defaults
footer_position: "bottom_fixed"         # bottom_fixed | bottom_relative | none
page_size: "letter"                     # letter | a4
page_numbers: true                      # Show page numbers in footer
page_number_format: "page_of_total"     # page_of_total | page_only | none

# QA defaults
qa_strict: false                        # Run QA in strict mode by default
qa_check_links: false                   # Validate URLs in QA by default
```

**Setting preferences via CLI:**

```bash
# Set a single preference
bangerpdf preferences set default_vibe bold

# View all preferences
bangerpdf preferences show

# Reset to defaults
bangerpdf preferences reset
```

**Precedence:** Global preferences are the broadest defaults. They are overridden by pack defaults, which are overridden by project-specific settings, which are overridden by CLI flags.

## The 4-Layer Merge

bangerpdf resolves configuration through a 4-layer merge, from broadest to most specific. Each layer can override values from the layer below it.

```
Layer 1: Global Preferences (~/.config/bangerpdf/preferences.yaml)
    |
    v
Layer 2: Pack Default (built into the starter pack)
    |
    v
Layer 3: Project brand-kit.yaml (project-specific brand identity)
    |
    v
Layer 4: CLI Overrides (--primary "#1B4332" --tier commercial)
```

### Layer 1: Global Preferences (broadest)

The user's saved defaults. Applied to every project automatically. These handle the "I always want Inter as my font" and "I never want page numbers" use cases.

Source: `~/.config/bangerpdf/preferences.yaml`

### Layer 2: Pack Default

Each starter pack ships with sensible defaults for its document type. The bid-package pack defaults to a bold cover page and formal tone. The invoice pack defaults to minimal styling and B&W.

Source: Built into the pack's `pack.yaml`

### Layer 3: Project brand-kit.yaml

The project-specific brand identity. Usually populated by brand discovery or loaded from a saved brand profile. This is where the client's exact hex codes, font choices, and logo live.

Source: `brand-kit.yaml` in the project root

### Layer 4: CLI Overrides (most specific)

Flags passed directly to `bangerpdf build` or `bangerpdf convert`. These win over everything.

Source: Command-line arguments

**Conflict resolution:** Later layers always win. If the global preference says `default_vibe: corporate` but the project's brand-kit.yaml implies a bold vibe, the project wins. If the CLI says `--primary "#FF0000"`, that overrides the brand-kit's primary color.

### Example Merge

```
Global preferences:     default_vibe=corporate, default_font_heading=Inter
Pack default (bid):     full_bleed_cover=true
Project brand-kit:      primary=#B77729, accent=#F5A600, heading=Helvetica Neue
CLI:                    --tier all

Result:
  vibe = corporate (global, not overridden)
  font_heading = Helvetica Neue (project overrides global)
  full_bleed_cover = true (pack default, not overridden)
  primary = #B77729 (project)
  tier = all (CLI overrides everything)
```

## CLI Commands

### Saving a Brand

```bash
# Save the current project's brand as a reusable profile
bangerpdf brand save carhartt

# What happens:
#   1. Copies brand-kit.yaml to ~/.config/bangerpdf/brands/carhartt/
#   2. Copies design-brief.yaml if it exists
#   3. Copies assets/ directory (logo, images)
#   4. Copies any custom-styles.css

# Save with a description
bangerpdf brand save carhartt --description "Carhartt Company Gear program, warm earthy palette"
```

### Loading a Brand

```bash
# Load a saved brand into a new project
bangerpdf brand load carhartt

# What happens:
#   1. Copies brand-kit.yaml from saved profile to project root
#   2. Copies assets/ (logo, images) to project assets/
#   3. Applies custom-styles.css if present
#   4. Prints a summary of what was loaded

# Load into a specific directory
bangerpdf brand load carhartt --target ./new-project

# Load brand + init a pack in one command
bangerpdf init bid-package ./new-bid --brand-profile carhartt
```

### Listing Saved Brands

```bash
# List all saved brands
bangerpdf brand list

# Output:
#   carhartt          Bold, warm earth tones        (saved 2026-04-10)
#   wilson-mechanical Corporate, navy blue           (saved 2026-04-08)
#   acme-plumbing     Minimal, green accent          (saved 2026-04-05)
```

### Deleting a Brand

```bash
# Delete a saved brand
bangerpdf brand delete acme-plumbing

# Confirmation prompt:
#   Delete saved brand "acme-plumbing"? This cannot be undone. (y/N)
```

### Preferences

```bash
# View all preferences
bangerpdf preferences show

# Set a preference
bangerpdf preferences set default_vibe editorial
bangerpdf preferences set auto_interview false
bangerpdf preferences set default_font_heading "Playfair Display"

# Reset all preferences to defaults
bangerpdf preferences reset
```

## When to Offer to Save

Proactively offer to save a brand profile in these scenarios:

1. **After a successful build the user approves** -- "Want to save this brand for reuse?"
2. **After brand discovery completes** -- "I discovered Carhartt's brand. Save it for future projects?"
3. **After significant CSS customization** -- "You've made some great style tweaks here. Save these as part of the Carhartt brand?"

Never save automatically. Always ask. The user may be experimenting, doing a one-off project, or not ready to commit to the current palette.

## When to Offer to Load

Proactively offer to load a saved brand when:

1. **User mentions a client name that matches a saved brand** -- "I have Carhartt's brand on file. Want me to load it?"
2. **User starts a new project without specifying brand details** -- "You have 3 saved brands. Want to start from one of them?"
3. **Design interview Question 4** -- "Before we discover the brand from scratch, I should mention you have a saved profile for Wilson Mechanical. Load that instead?"

## Updating a Saved Brand

Brands evolve. A company might rebrand, update their colors, or switch fonts. To update a saved profile:

```bash
# Make changes in the current project, then re-save
# This overwrites the existing saved profile
bangerpdf brand save carhartt

# Confirmation:
#   Brand "carhartt" already exists. Overwrite? (y/N)
```

There is no merge or diff for saved brands. Overwrite is the model. If the user wants to keep the old version, they should save under a new name (`carhartt-v2`) before overwriting.

## Portability

The `~/.config/bangerpdf/` directory is machine-local. It does not sync across devices by default. To share brand profiles across machines:

1. **Git:** Track `~/.config/bangerpdf/brands/` in a dotfiles repo
2. **rsync:** Sync the directory to other machines manually
3. **Export:** `bangerpdf brand export carhartt > carhartt-brand.tar.gz` (planned, not yet implemented)

For team workflows, save brand profiles in the project repo's `brands/` directory and load with a relative path. This keeps brand assets version-controlled alongside the documents that use them.

## Cross-References

- `design-interview.md` -- generates the design-brief.yaml that gets saved with the brand
- `brand-discovery.md` -- populates the brand-kit.yaml that gets saved
- `design-taste.md` -- provides default palettes and font pairings for Layer 1 preferences
- `SKILL.md` -- the master workflow (Step 8: Save Brand)
- `weasyprint-cookbook.md` -- custom-styles.css may contain WeasyPrint-specific workarounds
