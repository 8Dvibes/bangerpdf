# ICC Profiles for bangerpdf

This directory holds ICC color profiles used by the commercial-offset print tier.

## Required profiles

### sRGB_IEC61966-2-1.icc
- Standard sRGB color profile (IEC 61966-2-1:1999)
- Used as the default rendering intent for desktop and digital-press tiers
- Source: freely available from the International Color Consortium (ICC)
- Download: https://www.color.org/srgbprofiles.xalter

### GRACoL2013_CRPC6.icc
- US commercial CMYK standard (CGATS/CRPC6 characterization data)
- Used by the commercial-offset tier for PDF/X-4 output
- Source: Idealliance (formerly GRACoL committee)
- Download: https://www.idealliance.org/specifications/gracol/

## Status

Placeholder `.gitkeep` files are present. Actual ICC binaries will be added
when open-license copies are sourced and validated. WeasyPrint's PDF/X-4
output works without bundled ICC profiles (it embeds a standard CMYK output
intent declaration), but bundling profiles enables explicit color management
for workflows that require it.
