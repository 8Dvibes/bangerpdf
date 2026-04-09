"""
bangerpdf.review — Review Bundle workflow subpackage.

A Review Bundle is an HTML approval document (not a PDF) that wraps a
completed render-pack output so a client can:

  1. Click through v1 of every document in the pack
  2. Add inline annotations and decision notes
  3. Receive v2 with diff markers showing what changed
  4. Sign off on approval.html

Modeled on JJ's Xona client review bundles found in ~/Downloads/.

State machine in meta.json: draft -> awaiting-feedback -> revising -> approved.

Implemented in Phase 8 of the build sequence.
"""

from bangerpdf.review.builder import init_review, build_review
from bangerpdf.review.workflow import (
    init_meta,
    get_status,
    get_meta,
    add_annotation,
    revise,
    approve,
)

__all__ = [
    "init_review",
    "build_review",
    "init_meta",
    "get_status",
    "get_meta",
    "add_annotation",
    "revise",
    "approve",
]
