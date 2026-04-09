# letter Starter Pack

Formal 1-2 page business letter with branded letterhead, address blocks, subject line, body paragraphs, signature, enclosures, and CC list.

## Documents

1. **Letter** (2 pages) -- Letterhead, date, recipient block, subject, salutation, body, signature, enclosures, CC

## Quick Start

```bash
bangerpdf init letter ./my-letter
bangerpdf validate ./my-letter
bangerpdf build ./my-letter
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `sender` | name, company, address | Sender with optional title, phone, email, logo |
| `recipient` | name, company, address | Recipient with optional title |
| `date` | (string) | Letter date |
| `subject` | (string) | Subject line |
| `salutation` | (string) | Opening greeting |
| `body_paragraphs` | (string[]) | Body text paragraphs |
| `closing` | (string) | Closing phrase |
| `signature_name` | (string) | Printed name |
| `signature_title` | (string) | Title/role under signature |

Optional: `sender.logo`, `sender.phone`, `sender.email`, `recipient.title`, `reference`, `enclosures[]`, `cc[]`.

## Customization

Edit `brand-kit.yaml` to change colors. Default is conservative navy (#2C3E50) with blue accent (#3498DB). Body text is justified for a traditional letter appearance.
