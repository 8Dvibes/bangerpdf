# bangerpdf

> Make banger PDFs from HTML or data.

A unified Python CLI + Claude Code skill for generating print-ready PDFs across three output tiers — desktop, digital press, and commercial offset CMYK — with built-in QA, HTML Review Bundles, and ten starter packs covering bids, proposals, briefings, reports, one-pagers, certificates, invoices, letters, and more.

Built by [AI Build Lab](https://aibuildlab.com), inspired by John Jefferies' HTML-to-PDF toolkit and the Fishback Plumbing bid pipeline.

## What's in the box

- **Three-tier print pipeline** — desktop / digital press (crop marks + bleed) / commercial offset (RGB→CMYK + PDF/X-4), all using WeasyPrint 67+ native CMYK support. No Ghostscript dependency.
- **Brand kit system** — `brand-kit.yaml` defines primary/accent/font/logo once, every starter pack reads it.
- **Ten starter packs** — `bid-package`, `mgm-strategy-plan` (schema-driven for any agentic workflow), `proposal-package`, `briefing-package`, `one-pager`, `certificate`, `invoice`, `letter`, `report-package`, `review-bundle`.
- **Built-in QA checker** — 13 checks powered by PyMuPDF: density, page count, orphan headers, orphan signatures, table splits, content overflow, broken images, unresolved Jinja2 variables, broken URLs, headline consistency, font embedding, bleed area, PDF/X compliance.
- **HTML Review Bundles** — v1 → v2 → approval workflow modeled on real client work. Inline annotations, diff markers, self-contained HTML you can email or upload anywhere.
- **Claude Code skill** — outcome-triggered, fires on "build me a bid", "make this print-ready", "polish for client", etc. Bundled inside the package via `bangerpdf skills install`.

## Install

```bash
pip install bangerpdf
```

If you hit `externally-managed-environment` (Homebrew Python on macOS):

```bash
pip install bangerpdf --break-system-packages
```

Or use a virtual environment:

```bash
python3 -m venv ~/.bangerpdf-venv && ~/.bangerpdf-venv/bin/pip install bangerpdf
```

## Quick start

```bash
# Verify everything installed cleanly
bangerpdf doctor

# Convert any HTML file to a print-ready PDF
bangerpdf convert brochure.html --embed-assets

# Scaffold a bid package from the starter
bangerpdf init bid-package ./acme-bid

# Build all three tiers
cd ./acme-bid
bangerpdf build --tier all

# Run the QA checker
bangerpdf qa

# Wrap it as a Review Bundle for client approval
bangerpdf review init . --from .
bangerpdf review build
```

## Talk to Claude Code

After running `bangerpdf skills install`, your AI agent can do this on its own:

> "Build me a bid package for Acme Plumbing. Headline number is $445,000. Use Inter for typography and the Fishback navy/blue palette."

Or:

> "Take this markdown report and turn it into a print-ready PDF with our brand. Run the QA checker and fix anything it flags."

## CLI reference

```
bangerpdf convert <input.html> [--embed-assets] [--size letter|a4] [--output-dir DIR]
bangerpdf proof <input.pdf> [--dpi 300]
bangerpdf init <pack> <project-dir> [--brand NAME] [--primary HEX] [--logo PATH]
bangerpdf build [--tier desktop|digital-press|commercial|all] [--watch]
bangerpdf qa [--strict] [--diff] [--json]
bangerpdf review init <dir> --from <pack-dir>
bangerpdf review build|revise|approve|annotate
bangerpdf brand show|set
bangerpdf list-packs
bangerpdf skills install|uninstall|path
bangerpdf doctor
bangerpdf --version
```

Run `bangerpdf <command> --help` for full options.

## Lineage

bangerpdf unifies three earlier pipelines:

- **JJ's pdf-toolkit** ([commit ae5cbf73d](https://github.com/8Dvibes/AI-Build-Lab-Founders-Lounge), Mar 2 2026) — battle-tested HTML→PDF conversion, lifted unchanged as `bangerpdf.convert`, `bangerpdf.embed_assets`, `bangerpdf.proof`.
- **Fishback Plumbing bid pipeline** (Mar 21 – Apr 3 2026) — data-driven multi-document rendering pattern, generalized into `bangerpdf.render`.
- **The bug experience that started it all** — Joe Fishback's bid had 6 layout issues that needed manual fixing. The QA checker exists so that never has to happen again.

If you're a DocGen alum, this tool is for you. It's the file-creation-and-styling layer your agentic workflows have been missing.

## License

MIT. See [LICENSE](LICENSE).

bangerpdf depends on PyMuPDF, which is AGPL3. PyMuPDF is used as a library; running bangerpdf as a local CLI does not trigger AGPL distribution obligations. If you embed bangerpdf in a hosted service, consult PyMuPDF's licensing.

## Support

- Issues: https://github.com/8Dvibes/bangerpdf/issues
- Star the repo if it's useful
- Tag [@tyfisk](https://x.com/tyfisk) on X if you ship something with it
