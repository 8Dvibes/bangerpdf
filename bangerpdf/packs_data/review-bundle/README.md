# review-bundle Starter Pack

HTML approval document bundle for client review. Produces self-contained HTML pages (not PDF) with an index, annotation view, and approval tracker. Includes a lightweight CSS-only annotation UI.

## Documents

1. **Index** (1 page) -- Project info grid, document list with status badges, review stats, summary notes
2. **Version** (3 pages) -- Annotation cards split into open and resolved items, color-coded by status
3. **Approval** (2 pages) -- Per-document status, open item count, summary, dual signature blocks

## Quick Start

```bash
bangerpdf init review-bundle ./my-review
bangerpdf validate ./my-review
bangerpdf build ./my-review
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `pack_source` | (string) | Source pack that generated the reviewed docs |
| `project_name` | (string) | Project name |
| `version` | (string) | Document version being reviewed |
| `client_name` | (string) | Client company |
| `reviewer` | (string) | Assigned reviewer |
| `decisions` | doc, note per item | Review notes and annotations |

Optional: `review_date`, `due_date`, `documents[]` (with status), `decisions[].page`, `decisions[].resolved`, `summary_notes`, `approval_status`.

## HTML Output

This pack produces self-contained HTML, not PDF. The templates use a `page-container` wrapper for browser viewing and include `@page` rules as a fallback for printing. Status badges are color-coded: green (approved), yellow (pending), red (revision needed / rejected), blue (approved with changes).

## Annotation UI

The CSS includes a lightweight annotation card system. Each decision renders as a card with document reference, optional page number, note text, and resolved/open status. No JavaScript required for v1.
