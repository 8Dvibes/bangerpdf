# certificate Starter Pack

Single-page landscape certificate with decorative gold border, prominent recipient name, course details, signatory lines, and unique certificate ID.

## Documents

1. **Certificate** (1 page, landscape) -- Decorative frame, org header, recipient, course, description, signatures, cert ID

## Quick Start

```bash
bangerpdf init certificate ./my-cert
bangerpdf validate ./my-cert
bangerpdf build ./my-cert
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `recipient` | (string) | Certificate recipient name |
| `course_name` | (string) | Course or program name |
| `completion_date` | (string) | Date of completion |
| `description` | (string) | Achievement description |
| `signatories` | name, title per item (1-3) | Signatory lines |
| `cert_id` | (string) | Unique certificate identifier |
| `org_name` | (string) | Issuing organization |

Optional: `org_logo`, `subtitle`.

## Notes

- Uses `@page { size: letter landscape; }` for landscape orientation
- Decorative border with gold corner accents via CSS pseudo-elements
- Uses serif font (Georgia) for a formal, traditional feel
- Edit `brand-kit.yaml` to change the gold/navy palette
