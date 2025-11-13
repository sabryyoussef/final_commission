# Demo Data for Sales Commission Module

## Overview
This demo data includes realistic sales scenarios to test the commission functionality immediately after installation.

## Demo Products (with Commission Rates)

| Product | Price | Commission Rate |
|---------|-------|----------------|
| Demo Laptop Pro 15" | $1,500.00 | 8.5% |
| Demo Smartphone X | $899.00 | 5.0% |
| Demo Tablet Air | $650.00 | 6.0% |
| Demo 4K Monitor 27" | $450.00 | 4.5% |
| Demo Mechanical Keyboard | $120.00 | 10.0% |
| Demo Wireless Mouse | $45.00 | 12.0% |

## Demo Salespersons

1. **John Smith** (john.smith@demo.com)
2. **Sarah Johnson** (sarah.johnson@demo.com)
3. **Mike Davis** (mike.davis@demo.com)

## Demo Customers

1. **Acme Corporation** (Demo)
2. **TechCorp Solutions** (Demo)
3. **Global Inc** (Demo)

## Demo Invoices (Pre-created)

### Invoice 001 - John Smith
- **Customer:** Acme Corporation
- **Date:** 15 days ago
- **Products:**
  - 3x Demo Laptop Pro 15" @ $1,500 = $4,500 → Commission: $382.50
  - 3x Demo 4K Monitor 27" @ $450 = $1,350 → Commission: $60.75
- **Total Commission:** $443.25

### Invoice 002 - Sarah Johnson
- **Customer:** TechCorp Solutions
- **Date:** 10 days ago
- **Products:**
  - 10x Demo Smartphone X @ $899 = $8,990 → Commission: $449.50
  - 5x Demo Tablet Air @ $650 = $3,250 → Commission: $195.00
- **Total Commission:** $644.50

### Invoice 003 - Mike Davis
- **Customer:** Global Inc
- **Date:** 8 days ago
- **Products:**
  - 20x Demo Mechanical Keyboard @ $120 = $2,400 → Commission: $240.00
  - 20x Demo Wireless Mouse @ $45 = $900 → Commission: $108.00
- **Total Commission:** $348.00

### Invoice 004 - John Smith
- **Customer:** Acme Corporation
- **Date:** 5 days ago
- **Products:**
  - 15x Demo Tablet Air @ $650 = $9,750 → Commission: $585.00
- **Total Commission:** $585.00

### Invoice 005 - Sarah Johnson
- **Customer:** TechCorp Solutions
- **Date:** 3 days ago
- **Products:**
  - 5x Demo Laptop Pro 15" @ $1,500 = $7,500 → Commission: $637.50
  - 5x Demo 4K Monitor 27" @ $450 = $2,250 → Commission: $101.25
  - 5x Demo Mechanical Keyboard @ $120 = $600 → Commission: $60.00
- **Total Commission:** $798.75

### Refund 001 - Mike Davis
- **Customer:** Global Inc
- **Date:** 2 days ago
- **Products:**
  - 3x Demo Mechanical Keyboard @ $120 = $360 → Commission: -$36.00
- **Total Commission:** -$36.00

## Expected Commission Summary (After Sync & Invoice Posting)

| Salesperson | Total Sales | Refunds | Net Sales | Commission |
|-------------|-------------|---------|-----------|------------|
| John Smith | $15,600.00 | $0.00 | $15,600.00 | $1,028.25 |
| Sarah Johnson | $22,590.00 | $0.00 | $22,590.00 | $1,443.25 |
| Mike Davis | $3,300.00 | $360.00 | $2,940.00 | $312.00 |
| **TOTAL** | **$41,490.00** | **$360.00** | **$41,130.00** | **$2,783.50** |

## How to Test

1. **Install the module with demo data:**
   ```bash
   odoo-bin -d your_db -i sales_commision_product --test-enable
   ```

2. **Post the demo invoices:**
   - Go to Accounting → Customers → Invoices
   - Filter for "Demo" invoices
   - Select all invoices and click "Post"

3. **Run Commission Sync:**
   - Go to Sales → Commission → Manual Commission Sync
   - Click "Run Sync Now"
   - Check the success message

4. **View Commission Report:**
   - Go to Sales → Commission → Commission Report
   - You should see pivot table with commissions by salesperson

5. **Generate Financial Report:**
   - Go to Sales → Commission → Commission Financial Report
   - Select date range covering the last 30 days
   - Choose "All Posted Invoices" status
   - Click "Export to Excel" or "Print PDF"

6. **Mark invoices as paid (optional):**
   - Register payments on the invoices
   - Re-run Financial Report with "Paid Only" filter
   - Compare results with "All Posted Invoices"

## Notes

- Demo invoices are created in draft state
- You must **post the invoices** before running commission sync
- Commission lines are only created for **posted invoices**
- The "Paid Only" filter in Financial Report requires invoices to have registered payments
- All demo users have "Salesperson" access rights only
- To manage commissions, use a user with "Sales Commission Manager" rights
