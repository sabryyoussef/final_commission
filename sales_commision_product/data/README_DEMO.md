# Demo Data for Sales Commission Module

## Overview
This comprehensive demo data includes realistic sales scenarios to test all commission filtering functionality, including posted-but-unpaid invoices, paid invoices, refunds, and mixed scenarios.

## Demo Products (with Commission Rates)

| Product | Price | Commission Rate | Use Case |
|---------|-------|----------------|----------|
| Demo Laptop Pro 15" | $1,500.00 | 8.5% | High-value items |
| Demo Smartphone X | $899.00 | 5.0% | Medium-value electronics |
| Demo Tablet Air | $650.00 | 6.0% | Popular accessories |
| Demo 4K Monitor 27" | $450.00 | 4.5% | Computer peripherals |
| Demo Mechanical Keyboard | $120.00 | 10.0% | Small high-margin items |
| Demo Wireless Mouse | $45.00 | 12.0% | Low-cost high-margin items |
| Demo Service (No Commission) | $200.00 | 0.0% | Testing zero-commission products |

## Demo Salespersons

1. **John Smith** (john.smith@demo.com) - Mixed paid/unpaid orders
2. **Sarah Johnson** (sarah.johnson@demo.com) - Large orders, both statuses
3. **Mike Davis** (mike.davis@demo.com) - Includes refunds and recent orders

## Demo Customers

1. **Acme Corporation** - Enterprise customer
2. **TechCorp Solutions** - Medium business
3. **Global Inc** - Large corporation
4. **StartupXYZ** - Growing startup
5. **Enterprise Solutions Ltd** - Government contracts

## Demo Invoice Scenarios

### Scenario 1: John's PAID Invoice (15 days ago)
- **Customer:** Acme Corporation
- **Status:** PAID
- **Products:**
  - 3x Demo Laptop Pro 15" @ $1,500 = $4,500 → Commission: $382.50 (8.5%)
  - 3x Demo 4K Monitor 27" @ $450 = $1,350 → Commission: $60.75 (4.5%)
- **Total Commission:** $443.25 (Actual Earnings)

### Scenario 2: Sarah's UNPAID Invoice (10 days ago)
- **Customer:** TechCorp Solutions
- **Status:** POSTED (Not Paid)
- **Products:**
  - 10x Demo Smartphone X @ $899 = $8,990 → Commission: $449.50 (5.0%)
  - 5x Demo Tablet Air @ $650 = $3,250 → Commission: $195.00 (6.0%)
- **Total Commission:** $644.50 (Forecast Earnings)

### Scenario 3: Mike's PAID Invoice (8 days ago)
- **Customer:** Global Inc
- **Status:** PAID
- **Products:**
  - 20x Demo Mechanical Keyboard @ $120 = $2,400 → Commission: $240.00 (10.0%)
  - 20x Demo Wireless Mouse @ $45 = $900 → Commission: $108.00 (12.0%)
- **Total Commission:** $348.00 (Actual Earnings)

### Scenario 4: John's UNPAID Large Order (5 days ago)
- **Customer:** StartupXYZ
- **Status:** POSTED (Not Paid)
- **Products:**
  - 15x Demo Tablet Air @ $650 = $9,750 → Commission: $585.00 (6.0%)
- **Total Commission:** $585.00 (Forecast Earnings)

### Scenario 5: Sarah's Recent PAID Order (3 days ago)
- **Customer:** Enterprise Solutions Ltd
- **Status:** PAID
- **Products:**
  - 5x Demo Laptop Pro 15" @ $1,500 = $7,500 → Commission: $637.50 (8.5%)
  - 5x Demo 4K Monitor 27" @ $450 = $2,250 → Commission: $101.25 (4.5%)
  - 5x Demo Mechanical Keyboard @ $120 = $600 → Commission: $60.00 (10.0%)
- **Total Commission:** $798.75 (Actual Earnings)

### Scenario 6: Mike's Recent UNPAID Order (1 day ago)
- **Customer:** Acme Corporation
- **Status:** POSTED (Not Paid)
- **Products:**
  - 8x Demo Smartphone X @ $899 = $7,192 → Commission: $359.60 (5.0%)
  - 2x Demo Tablet Air @ $650 = $1,300 → Commission: $78.00 (6.0%)
- **Total Commission:** $437.60 (Forecast Earnings)

### Scenario 7: John's PARTIALLY PAID Invoice (2 days ago)
- **Customer:** TechCorp Solutions
- **Status:** PARTIAL (50% Paid)
- **Products:**
  - 2x Demo Laptop Pro 15" @ $1,500 = $3,000 → Commission: $255.00 (8.5%)
- **Total Commission:** $255.00 (Partial Earnings - filters as "not fully paid")

### Scenario 8: Mike's REFUND (2 days ago)
- **Customer:** Global Inc
- **Status:** POSTED REFUND
- **Products:**
  - 3x Demo Mechanical Keyboard @ $120 = $360 → Commission: -$36.00 (10.0%)
- **Total Commission:** -$36.00 (Reduces Actual Earnings)

### Scenario 9: Mixed Commission Invoice (1 day ago)
- **Customer:** StartupXYZ
- **Salesperson:** Sarah Johnson
- **Status:** PAID
- **Products:**
  - 5x Demo Service (No Commission) @ $200 = $1,000 → Commission: $0.00 (0.0%)
  - 1x Demo Laptop Pro 15" @ $1,500 = $1,500 → Commission: $127.50 (8.5%)
- **Total Commission:** $127.50 (Shows mixed commission scenario)

## Expected Commission Summary by Filter

### "Paid Only" Filter (Actual Earnings)
| Salesperson | Paid Sales | Refunds | Net Earnings | Paid Commission |
|-------------|------------|---------|--------------|----------------|
| John Smith | $8,850.00 | $0.00 | $8,850.00 | $698.25 |
| Sarah Johnson | $12,350.00 | $0.00 | $12,350.00 | $1,426.00 |
| Mike Davis | $3,300.00 | $360.00 | $2,940.00 | $312.00 |
| **TOTAL** | **$24,500.00** | **$360.00** | **$24,140.00** | **$2,436.25** |

### "Posted Only (Not Paid)" Filter (Forecast Earnings)
| Salesperson | Unpaid Sales | Forecast Commission |
|-------------|--------------|-------------------|
| John Smith | $12,750.00 | $840.00 |
| Sarah Johnson | $12,240.00 | $644.50 |
| Mike Davis | $8,492.00 | $437.60 |
| **TOTAL** | **$33,482.00** | **$1,922.10** |

### "All Posted Invoices" Filter (Total Pipeline)
| Salesperson | Total Sales | Total Returns | Net Sales | Total Commission |
|-------------|-------------|---------------|-----------|-----------------|
| John Smith | $21,600.00 | $0.00 | $21,600.00 | $1,538.25 |
| Sarah Johnson | $24,590.00 | $0.00 | $24,590.00 | $2,070.50 |
| Mike Davis | $11,792.00 | $360.00 | $11,432.00 | $749.60 |
| **TOTAL** | **$57,982.00** | **$360.00** | **$57,622.00** | **$4,358.35** |

## Installation & Setup

### Automatic Demo Data (Recommended)
1. **Install module with demo data:**
   ```bash
   odoo-bin -d your_db -i sales_commision_product --load-language en_US
   ```

2. **Create demo invoices:**
   ```bash
   # In Odoo shell
   odoo-bin shell -c /path/to/odoo.conf -d your_database
   >>> exec(open('/workspaces/final_commission/create_demo_invoices.py').read())
   ```

3. **Access commission reports:**
   - Go to Sales → Reporting → Commission Financial Report
   - Test different status filters and date ranges

### Manual Demo Data Setup
1. **Create products** with commission rates using the demo data above
2. **Create salespersons** and assign to Sales/User group
3. **Create customers** with proper accounting setup
4. **Create invoices** manually using the scenarios above
5. **Post invoices** and register payments as needed
6. **Run commission sync** via Sales → Reporting → Generate Commission Data

## Testing Procedures

### 1. Filter Testing
1. **Navigate to:** Sales → Reporting → Commission Financial Report
2. **Test filters:**
   - **"Posted Only (Not Paid)"** - Should show $1,922.10 in forecast commissions
   - **"Paid Only"** - Should show $2,436.25 in actual commissions
   - **"All Posted Invoices"** - Should show $4,358.35 total commissions

### 2. Date Range Testing
1. **Set date range** to cover last 30 days
2. **Narrow range** to last 7 days to see only recent orders
3. **Verify filtering** works correctly with different periods

### 3. Salesperson Filtering
1. **Select John Smith only** - Should show his paid ($698.25) and unpaid ($840.00) commissions separately
2. **Select multiple salespersons** - Should combine their data correctly
3. **Leave empty** - Should include all salespersons

### 4. Report Generation Testing
1. **Export to Excel** - Should create comprehensive spreadsheet with summary and details
2. **Generate PDF** - Should create formatted report with all data
3. **Verify calculations** match the expected totals above

### 5. Commission Sync Testing
1. **Create new invoice** manually and post it
2. **Run commission sync** via the wizard
3. **Verify new commission line** appears in reports
4. **Mark invoice as paid** and re-run sync
5. **Check filter behavior** changes appropriately

## Troubleshooting

### No Commission Data Found
1. **Check invoice states** - Ensure invoices are posted
2. **Verify commission rates** - Products must have rates > 0
3. **Run commission sync** - Use the manual sync wizard
4. **Check date ranges** - Ensure filters cover your invoice dates

### Incorrect Totals
1. **Verify payment states** - Check if invoices are marked as paid correctly
2. **Check refunds** - Ensure credit notes are properly handled
3. **Review commission rates** - Confirm product commission percentages
4. **Re-run sync** - Commission service updates existing lines

### Missing Invoices in Reports
1. **Check filters** - Try "All Posted Invoices" to see everything
2. **Expand date range** - Include historical dates
3. **Verify salesperson assignment** - Check invoice.invoice_user_id field
4. **Review invoice states** - Ensure invoices are properly posted

## Demo Data Benefits

✅ **Comprehensive Testing** - Covers all commission filtering scenarios  
✅ **Realistic Data** - Mirrors actual business transactions  
✅ **Multiple Salespersons** - Tests aggregation and filtering  
✅ **Different Payment States** - Tests all filter combinations  
✅ **Refund Handling** - Verifies negative commission processing  
✅ **Mixed Scenarios** - Tests edge cases and real-world complexity  
✅ **Performance Testing** - Sufficient volume for testing reports  
✅ **User Training** - Provides realistic data for demos and training
