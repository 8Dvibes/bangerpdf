# invoice Starter Pack

Branded 1-2 page invoice with sender/recipient details, line items, tax calculation, and payment terms.

## Documents

1. **Invoice** (2 pages) -- Header with brand, bill-to block, date/due/amount meta bar, line items table, totals, payment terms, notes

## Quick Start

```bash
bangerpdf init invoice ./my-invoice
bangerpdf validate ./my-invoice
bangerpdf build ./my-invoice
```

## Schema

| Key | Required Fields | Purpose |
|-----|----------------|---------|
| `from` | name, address, email | Sender/biller details |
| `to` | name, address | Recipient/client details |
| `invoice_number` | (string) | Invoice identifier |
| `date` | (string) | Invoice date |
| `due_date` | (string) | Payment due date |
| `line_items` | description, qty, rate, amount per item | Billable line items |
| `subtotal` | (number) | Subtotal before tax |
| `total` | (number) | Grand total |
| `payment_terms` | (string) | Payment terms |

Optional: `from.phone`, `from.logo`, `from.website`, `from.tax_id`, `to.email`, `tax_rate`, `tax`, `notes`, `currency`.

## Customization

Edit `brand-kit.yaml` to change colors. Default is clean gray with blue accent (#4a90d9). The `currency` field defaults to `$` if not specified.
