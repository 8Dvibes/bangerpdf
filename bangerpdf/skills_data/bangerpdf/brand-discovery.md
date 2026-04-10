---
name: bangerpdf/brand-discovery
description: >
  Automated brand research pipeline for bangerpdf. Discovers brand colors, fonts,
  logo, and imagery from a company website. Uses Brand Fetch API when available
  (optional), falls back to web scraping. Populates brand-kit.yaml automatically.
---

# bangerpdf -- Brand Discovery

Brand consistency is the difference between a document that looks like it belongs to the client and one that looks like a template with their name pasted in. This pipeline automates the tedious part -- extracting colors, fonts, and logos from a company's existing web presence -- so you spend your time on layout and content, not eyedroppering hex codes from screenshots.

## When to Use This

Brand discovery is triggered in two ways:

1. **From the design interview** (Question 4) -- the user provides a URL and you run discovery automatically
2. **Directly via CLI** -- `bangerpdf brand discover <url>`

In both cases, the output is the same: a populated `brand-kit.yaml` and (when possible) a downloaded logo in `assets/`.

## The 3-Tier Discovery Pipeline

Brand discovery attempts three strategies in order, from most accurate to most manual. Each tier falls back to the next if it fails or is unavailable.

### Tier 1: Brand Fetch API (Optional, Fastest)

**Prerequisite:** The `BRANDFETCH_API_KEY` environment variable must be set.

Brand Fetch is a commercial API that returns structured brand data: hex colors (with roles like "primary" and "accent"), font names, logo URLs in multiple formats, and banner images. It is the fastest and most accurate path because it returns curated, verified brand data rather than scraped approximations.

**What it returns:**
- Color palette with semantic roles (primary, secondary, accent)
- Font families with weights
- Logo in SVG, PNG, and icon variants
- Banner/cover images
- Brand description and industry tags

**How to use:**
```python
import urllib.request
import json

def try_brandfetch(domain: str) -> dict | None:
    api_key = os.environ.get("BRANDFETCH_API_KEY")
    if not api_key:
        return None

    url = f"https://api.brandfetch.io/v2/brands/{domain}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None
```

**Free tier limits:** Brand Fetch offers a free tier with limited lookups per month. For most bangerpdf usage (a few brands per project), the free tier is sufficient. If the key is not set, this tier is silently skipped.

**Graceful skip:** If the API key is missing, expired, or the lookup fails, discovery falls through to Tier 2 with zero user-visible errors. This is an optional power-up, not a hard dependency.

### Tier 2: Web Scrape (Primary Fallback)

When Brand Fetch is unavailable, scrape the company's homepage directly. This works well for most websites and requires zero API keys.

**What to extract:**

| Data Point | Where to Find It | Extraction Method |
|------------|------------------|-------------------|
| Colors | CSS custom properties, inline styles, computed backgrounds | Parse `--primary`, `--brand`, `--accent` CSS vars; extract `background-color` on header/nav elements; look for `meta[name="theme-color"]` |
| Fonts | `font-family` declarations, Google Fonts links | Parse CSS for `font-family`, check `<link>` tags for Google Fonts URLs, inspect `@font-face` declarations |
| Logo | Favicon, og:image, header `<img>`, SVG in nav | Check `<link rel="icon">`, `<meta property="og:image">`, first `<img>` in `<header>` or `<nav>`, inline `<svg>` elements |
| Brand name | `<title>`, og:site_name, structured data | Parse `<title>`, check `<meta property="og:site_name">`, look for JSON-LD `@type: Organization` |

**Scraping strategy:**

```python
import urllib.request
from html.parser import HTMLParser

def scrape_brand(url: str) -> dict:
    """Scrape homepage for brand signals. Zero external dependencies."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "bangerpdf-brand-discovery/2.0"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    # Parse HTML for brand signals
    colors = extract_colors_from_css(html)
    fonts = extract_fonts_from_css(html)
    logo_url = extract_logo_url(html, url)
    brand_name = extract_brand_name(html)

    return {
        "colors": colors,
        "fonts": fonts,
        "logo_url": logo_url,
        "brand_name": brand_name,
        "source": "web-scrape",
        "source_url": url
    }
```

**Color extraction priorities (highest confidence first):**

1. CSS custom properties named `--primary`, `--brand-color`, `--accent`, etc.
2. `<meta name="theme-color" content="#hex">` in `<head>`
3. Background color of the first `<header>` or `<nav>` element
4. Most-used non-white, non-black color in the page's CSS
5. Colors from the favicon (sample dominant colors)

**Font extraction priorities:**

1. Google Fonts `<link>` URLs -- parse the `family=` parameter
2. `@font-face` declarations with `src:` URLs
3. `font-family` on `body`, `h1`, or root element
4. Fall back to system font stack detection (Inter, Helvetica, etc.)

**Logo extraction priorities:**

1. `<link rel="icon" type="image/svg+xml">` -- SVG favicon is ideal
2. `<meta property="og:image">` -- usually high-res, brand-approved
3. First `<img>` inside `<header>` or `<nav>` with "logo" in src/alt/class
4. Inline `<svg>` in the header area
5. `/favicon.ico` as absolute last resort (low quality, but better than nothing)

**Using firecrawl when available:**

If firecrawl is installed (check for `FIRECRAWL_API_KEY` env var or local instance), use it instead of raw urllib. Firecrawl handles JavaScript-rendered pages, anti-bot protections, and returns cleaner HTML. The extraction logic stays the same.

```bash
# firecrawl gives cleaner HTML for JS-heavy sites
firecrawl scrape --url "https://example.com" --formats html
```

### Tier 3: Manual Research (Always Available)

When both API and scraping fail (private sites, login walls, no website), fall back to manual web search.

**Search queries to run:**
- `"[brand name]" brand guidelines`
- `"[brand name]" logo PNG SVG`
- `"[brand name]" brand colors hex`
- `"[brand name]" style guide`
- `site:brandfolder.com "[brand name]"` -- some companies host public brand portals

**Where to look:**
- Company LinkedIn page (often has logo and brand colors in banner)
- Press kit pages (`/press`, `/media`, `/brand`)
- Social media profiles (Instagram, Twitter headers)
- Glassdoor/Indeed company pages

**What to collect:**
- Download the highest-resolution logo available (SVG > PNG > JPG)
- Note 2-3 dominant colors from their web presence
- Identify font family from any available materials

This tier requires human judgment. The agent should present what it found and ask the user to confirm.

## CLI Usage

```bash
# Discover brand from a URL
bangerpdf brand discover https://carhartt.com

# Output:
#   Discovered brand: Carhartt
#   Colors: primary=#B77729, accent=#F5A600, dark=#1A1A1A
#   Fonts: Helvetica Neue (heading), Helvetica Neue (body)
#   Logo: Downloaded to assets/logo.png (SVG not available)
#   Brand kit written to brand-kit.yaml

# Discover and immediately save for reuse
bangerpdf brand discover https://carhartt.com --save carhartt

# Use a specific discovery tier
bangerpdf brand discover https://carhartt.com --tier scrape  # skip Brand Fetch
```

## Output: brand-kit.yaml

Discovery populates the standard brand-kit.yaml format used by all bangerpdf packs:

```yaml
# brand-kit.yaml -- Auto-discovered by bangerpdf brand discovery
# Source: https://carhartt.com
# Method: web-scrape (Brand Fetch API not configured)
# Discovered: 2026-04-10

brand_name: "Carhartt"
source_url: "https://carhartt.com"

colors:
  primary: "#B77729"
  accent: "#F5A600"
  neutral-dark: "#1A1A1A"
  neutral-mid: "#5C5C5C"
  neutral-light: "#F5F1EB"
  neutral-border: "#D4C5B0"
  background: "#FDFAF5"

fonts:
  heading: "Helvetica Neue"
  heading_weight: "700"
  body: "Helvetica Neue"
  body_weight: "400"

logo:
  path: "assets/logo.png"
  format: "png"
  # SVG preferred for print. If only raster available, note minimum size.
  min_width_px: 800

discovery:
  method: "web-scrape"       # brandfetch | web-scrape | manual
  confidence: "medium"        # high (brandfetch) | medium (scrape) | low (manual)
  timestamp: "2026-04-10T14:30:00Z"
  notes: "Colors extracted from CSS custom properties. Logo from og:image."
```

### Confidence Levels

| Method | Confidence | What it means |
|--------|-----------|---------------|
| Brand Fetch API | High | Curated, verified brand data. Colors have semantic roles. Fonts are exact. |
| Web Scrape | Medium | Extracted from live site. Colors are accurate but roles may be guessed. Fonts may be a stack, not a specific face. |
| Manual Research | Low | Assembled from public sources. Should be confirmed with the client before building. |

Always include `discovery.confidence` in the output so downstream steps know how much to trust the values. Low-confidence brand kits should trigger a confirmation prompt before building.

## Integration with the Design Interview

When the user answers Question 4 in the design interview with a URL:

1. Run the discovery pipeline against the URL
2. Show the user what was found: "I discovered these brand colors from carhartt.com: primary #B77729, accent #F5A600. Does this look right?"
3. If confirmed, write brand-kit.yaml
4. If they correct something ("Our primary is actually #C28030"), update and write
5. Continue the interview with Question 5

The interview does not pause for discovery. Run it asynchronously if possible and present results when the user reaches a natural break point.

## Handling Edge Cases

### No Website
The user has no website. This is common for small businesses, freelancers, and new companies.

**Response:** "No problem. I'll set up a clean palette based on your industry and vibe. You can always customize the colors later."

Use the vibe defaults from `design-taste.md` and the industry heuristics below:

| Industry | Suggested Palette | Reasoning |
|----------|------------------|-----------|
| Construction / Trades | Warm neutrals, navy, amber | Solid, trustworthy, workwear-adjacent |
| Healthcare | Blue-gray, white, teal accents | Clinical, calming, professional |
| Technology / SaaS | Blue, dark backgrounds, bright accents | Modern, digital-native |
| Legal / Finance | Navy, charcoal, minimal accent | Conservative, authoritative |
| Creative / Design | Black + one bold accent | Let the work speak, not the branding |
| Food / Hospitality | Warm earth tones, cream backgrounds | Inviting, approachable |
| Nonprofit | Green or blue, warm neutrals | Mission-driven, trustworthy |

### JavaScript-Heavy Site
The site renders entirely in JavaScript and urllib gets an empty `<body>`.

**Response:** Use firecrawl if available. If not, try the manual research tier. As a last resort, ask the user to screenshot the homepage and analyze the visual design from the image.

### Multiple Brands
The document involves two companies (co-branded bid, partnership proposal).

**Response:** Run discovery on both URLs. Set one as primary (the sender's brand) and the other as secondary. The primary brand controls the overall palette; the secondary brand appears in the header and co-branding elements.

```yaml
# brand-kit.yaml for co-branded document
brand_name: "Wilson Mechanical x Carhartt"
colors:
  primary: "#0D1B2A"      # Wilson's brand (sender)
  accent: "#B77729"        # Carhartt's brand (partner)
  # ... rest of palette derived from primary brand
```

### Brand Fetch Returns Incomplete Data
The API returns colors but no fonts, or a logo but no colors.

**Response:** Merge with web scrape results. Brand Fetch data takes priority where available; scrape fills the gaps.

## Downloaded Assets

When discovery downloads a logo or other assets:

- **Save to:** `assets/` directory in the project root
- **Filename:** `logo.png`, `logo.svg`, or `logo-[brand].png` for co-branded
- **Format preference:** SVG > PNG > JPG. Vector formats scale perfectly for print.
- **Minimum size:** For raster logos, warn if width < 400px. Suggest the user provide a higher-resolution version.

Do not download or cache assets outside the project directory. Each project gets its own copy in `assets/` so the project remains self-contained and portable.

## Cross-References

- `design-interview.md` -- triggers this pipeline from Question 4
- `design-memory.md` -- `brand save` persists discovered brands for reuse
- `design-taste.md` -- fallback palettes and font pairings when discovery yields incomplete results
- `SKILL.md` -- the master workflow (Step 2: Brand Discovery)
