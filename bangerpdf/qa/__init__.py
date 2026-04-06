"""
bangerpdf.qa — QA checker subpackage.

The QA checker is the highest-leverage component of bangerpdf. It uses
PyMuPDF (`fitz.Document.get_text("dict")`) to extract text blocks with
bounding boxes from rendered PDFs and runs 13 checks to catch the layout
bugs that historically required manual visual review:

  1. Page content density (orphan / overflow detection)
  2. Page count vs schema-declared expected_pages
  3. Orphan section headers at page bottom
  4. Orphan signature blocks
  5. Table rows split across pages
  6. Content overflowing the page
  7. Broken image references (alt-text leak)
  8. Unresolved Jinja2 variables
  9. Broken external URLs
 10. Headline number consistency across documents
 11. Font embedding + subsetting
 12. Bleed area present (digital-press / commercial tiers)
 13. PDF/X + PDF/A compliance

Each check is a function returning CheckResult(level, code, message, page, bbox).
The runner orchestrates all checks and produces a tier-aware terminal dashboard.

Implemented in Phase 3 of the build sequence.
"""

__all__ = []
