# Commission Wizard Data Issue - Root Cause Analysis

**Date:** 2025-11-13  
**Module:** sales_commision_product  
**Issue:** Financial Report Wizard returns "No commission data found" while Commission Report shows data

---

## Executive Summary

The Financial Report Wizard (`wizard.commission.report`) is querying **live invoice data** directly from `account.move` and `account.move.line`, while the Commission Report view displays data from the **`sales.commission.line`** model. This architectural mismatch is causing the wizard to return no results even when commission line records exist.

### Critical Discovery

**The wizard does NOT use the `sales.commission.line` model at all!** It rebuilds commission data from scratch by querying invoices directly, which means:

1. The wizard's query logic may not match the actual commission sync logic
2. Different filtering conditions could cause discrepancies
3. Data visible in Commission Report may not satisfy wizard's stricter criteria

---

## Root Cause Analysis

### 1. **Payment State Filter Mismatch**

**Commission Sync Logic** (`commission_service.py`, line 39):
```python
("move_id.payment_state", "in", ["paid"]),  # Only 'paid' for invoices
```

**Wizard Logic** (`wizard_commission_report.py`, line 64):
```python
if self.status_filter == 'paid':
    domain.append(('payment_state', 'in', ['paid', 'in_payment']))
```

**Issue:** The commission sync only creates records for invoices with `payment_state = 'paid'`, but the wizard also includes `'in_payment'` state. However, this shouldn't cause the "no data" issue unless the actual invoices have a different payment state.

### 2. **Most Likely Issue: Invoice Payment State**

The invoices visible in the Commission Report (showing 300.00 commission) likely have:
- `state = 'posted'` ✓
- `move_type = 'out_invoice'` ✓
- **`payment_state` might be something other than 'paid' or 'in_payment'**

Possible payment states in Odoo:
- `not_paid` - Invoice is posted but not paid
- `in_payment` - Payment is being processed
- `paid` - Fully paid
- `partial` - Partially paid
- `reversed` - Reversed
- `invoicing_legacy` - Legacy state

**Hypothesis:** Your invoices likely have `payment_state = 'not_paid'` or `'partial'`, which:
- ✓ Allows commission sync to create commission line records (if they were created when paid, then later changed)
- ✗ Prevents wizard from finding them (wizard filters by payment_state)

### 3. **Date Range Filter**

The wizard defaults to:
- `date_from`: First day of current month
- `date_to`: Today

If your invoices were dated before the current month, they won't appear unless you adjust the date range.

### 4. **Salesperson Filter**

Both wizard and commission sync use `invoice_user_id`:
```python
# Wizard
domain.append(('invoice_user_id', 'in', self.salesperson_ids.ids))

# Commission Sync
salesperson = move.invoice_user_id or self.env.user
```

If `invoice_user_id` is not set on the invoices, commission records might be created with a default user, but wizard might filter them out.

---

## Investigation Steps Performed

### 1. **Code Analysis**
- ✓ Reviewed `wizard_commission_report.py` - Found it queries `account.move` directly
- ✓ Reviewed `commission.py` - Found it's a separate storage model
- ✓ Reviewed `commission_service.py` - Found sync logic differences
- ✓ Compared domain filters between wizard and sync

### 2. **Test File Analysis**
The test file `test_wizard_commission_report.py` shows:
```python
def _mark_invoice_paid(self, invoice):
    """Helper method to mark invoice as paid."""
    payment_register = self.env['account.payment.register'].with_context(
        active_model='account.move',
        active_ids=invoice.ids,
    ).create({
        'payment_date': invoice.invoice_date,
    })
    payment_register.action_create_payments()
```

This confirms the wizard expects invoices to be **actually paid** (with payment records), not just posted.

---

## Diagnostic Queries

### To verify the issue, run these queries on Odoo:

#### 1. Check payment state of invoices with commission lines:
```python
# In Odoo shell or debug mode
commission_lines = env['sales.commission.line'].search([])
for line in commission_lines:
    invoice = line.invoice_id
    print(f"Invoice: {invoice.name}")
    print(f"  State: {invoice.state}")
    print(f"  Payment State: {invoice.payment_state}")
    print(f"  Date: {invoice.invoice_date}")
    print(f"  Salesperson: {invoice.invoice_user_id.name}")
    print(f"  Commission: {line.commission_amount}")
    print("---")
```

#### 2. Check what invoices exist in the date range:
```python
from datetime import date
today = date.today()
first_of_month = today.replace(day=1)

invoices = env['account.move'].search([
    ('move_type', '=', 'out_invoice'),
    ('state', '=', 'posted'),
    ('invoice_date', '>=', first_of_month),
    ('invoice_date', '<=', today),
])

for inv in invoices:
    print(f"{inv.name}: payment_state={inv.payment_state}, date={inv.invoice_date}")
```

---

## Recommended Fixes

### **Option 1: Align Wizard with Commission Sync Logic (Recommended)**

Modify the wizard to query from `sales.commission.line` instead of rebuilding from invoices:

```python
def _get_commission_data(self):
    """Query from sales.commission.line model."""
    self.ensure_one()
    
    # Build domain for commission lines
    domain = [
        ('invoice_date', '>=', self.date_from),
        ('invoice_date', '<=', self.date_to),
    ]
    
    # Status filter - map to invoice payment states
    if self.status_filter == 'paid':
        domain.append(('invoice_id.payment_state', 'in', ['paid', 'in_payment']))
    elif self.status_filter == 'posted':
        domain.append(('invoice_id.payment_state', 'not in', ['paid', 'in_payment']))
    # 'all' doesn't need additional filter
    
    # Ensure invoice is still posted
    domain.append(('invoice_id.state', '=', 'posted'))
    
    # Salesperson filter
    if self.salesperson_ids:
        domain.append(('salesperson_id', 'in', self.salesperson_ids.ids))
    
    # Get commission lines
    commission_lines = self.env['sales.commission.line'].search(
        domain, 
        order='salesperson_id, invoice_date'
    )
    
    # Structure: {salesperson_id: {data}}
    data_by_salesperson = {}
    
    for line in commission_lines:
        salesperson = line.salesperson_id
        if not salesperson:
            continue
        
        if salesperson.id not in data_by_salesperson:
            data_by_salesperson[salesperson.id] = {
                'salesperson': salesperson,
                'total_sales': 0.0,
                'total_returns': 0.0,
                'total_commission': 0.0,
                'lines': []
            }
        
        # Handle refunds (negative values)
        if line.move_type == 'out_refund':
            data_by_salesperson[salesperson.id]['total_returns'] += abs(line.line_subtotal)
        else:
            data_by_salesperson[salesperson.id]['total_sales'] += line.line_subtotal
        
        data_by_salesperson[salesperson.id]['total_commission'] += line.commission_amount
        
        # Add line detail
        data_by_salesperson[salesperson.id]['lines'].append({
            'invoice_date': line.invoice_date,
            'invoice_number': line.invoice_id.name,
            'invoice_id': line.invoice_id.id,
            'product_name': line.product_id.display_name,
            'quantity': line.quantity,
            'line_subtotal': line.line_subtotal,
            'commission_rate': line.commission_rate,
            'commission_amount': line.commission_amount,
            'move_type': 'Invoice' if line.move_type == 'out_invoice' else 'Refund',
        })
    
    return data_by_salesperson
```

**Benefits:**
- ✓ Consistent data between Report and Wizard
- ✓ Better performance (queries pre-computed data)
- ✓ Single source of truth
- ✓ Respects commission sync business logic

### **Option 2: Relax Payment State Filter**

If you want to keep the current architecture but include more invoices:

```python
# Status filter
if self.status_filter == 'paid':
    domain.append(('payment_state', 'in', ['paid', 'in_payment']))
elif self.status_filter == 'posted':
    domain.append(('payment_state', 'in', ['not_paid', 'partial']))
elif self.status_filter == 'all':
    # Don't filter by payment_state at all
    pass
```

**Benefits:**
- ✓ Quick fix
- ✗ May show commissions for unpaid invoices
- ✗ Doesn't match commission sync logic

### **Option 3: Update Commission Sync to be More Lenient**

Change commission sync to create records for all posted invoices:

```python
# In commission_service.py, line 36-42
invoice_lines = move_line_model.search([
    ("move_id.state", "=", "posted"),
    ("move_id.move_type", "=", "out_invoice"),
    # Remove payment_state filter to include all posted invoices
    ("product_id", "!=", False),
    ("display_type", "not in", ["line_section", "line_note"]),
])
```

**Benefits:**
- ✓ More commission data available
- ✗ Shows commissions for unpaid invoices (may not be desired)
- ✗ Requires re-thinking business logic

---

## Testing Plan

### 1. **Unit Tests** (Cannot run without Odoo environment)
The existing tests in `test_wizard_commission_report.py` all create invoices and mark them as paid, which may not reflect your production scenario.

### 2. **Manual Testing Steps**

1. **Verify current invoice states:**
   ```python
   # Check the invoices that have commission lines
   lines = env['sales.commission.line'].search([])
   invoice_ids = lines.mapped('invoice_id')
   for inv in invoice_ids:
       print(f"{inv.name}: state={inv.state}, payment={inv.payment_state}")
   ```

2. **Test wizard with different filters:**
   - Try `status_filter = 'all'`
   - Try expanding date range to cover all historical data
   - Try leaving salesperson filter empty

3. **Test with paid invoice:**
   - Create a test invoice
   - Register a payment
   - Run commission sync
   - Try wizard again

---

## Impact Analysis

### Current State
- ✓ Commission Report works (shows 300.00 commission)
- ✗ Financial Report Wizard returns "No data found"
- ✓ Commission sync creates records successfully

### After Option 1 Fix (Recommended)
- ✓ Commission Report continues to work
- ✓ Financial Report Wizard shows same data as Report
- ✓ Consistent business logic
- ✓ Better performance

### After Option 2 Fix
- ✓ Commission Report continues to work
- ✓ Financial Report Wizard may show data
- ⚠️  May include unpaid invoices depending on filter
- ⚠️  Still has architectural inconsistency

---

## Immediate Actions

### 1. **Quick Diagnostic** (5 minutes)
Run this in Odoo shell to see your actual data:

```python
# Check commission lines
lines = env['sales.commission.line'].search([], limit=10)
print(f"Commission lines found: {len(env['sales.commission.line'].search([]))}")

for line in lines:
    inv = line.invoice_id
    print(f"\nCommission: {line.commission_amount}")
    print(f"Invoice: {inv.name}")
    print(f"Date: {inv.invoice_date}")
    print(f"State: {inv.state}")
    print(f"Payment State: {inv.payment_state}")
    print(f"Salesperson: {inv.invoice_user_id.name if inv.invoice_user_id else 'None'}")

# Check wizard filters
from datetime import date
today = date.today()
first_of_month = today.replace(day=1)
print(f"\nWizard default date range: {first_of_month} to {today}")
print(f"Invoice date in range: {line.invoice_date >= first_of_month and line.invoice_date <= today}")
```

### 2. **Workaround** (Immediate)
When using the wizard:
- Set date range to include your invoice dates (possibly all-time)
- Set status filter to 'all'
- Leave salesperson filter empty

### 3. **Implement Fix** (30 minutes)
Apply Option 1 (recommended) by modifying `wizard_commission_report.py`

---

## Code Changes Required

See the code snippet in **Option 1** above. The main change is replacing the entire `_get_commission_data()` method to query from `sales.commission.line` instead of `account.move`.

**Files to modify:**
- `sales_commision_product/models/wizard_commission_report.py` (1 method replacement)

**Files to update (tests):**
- May need to update tests to ensure commission lines are synced before testing wizard

---

## Conclusion

The issue is an **architectural design problem** where two different data sources are being used:
1. Commission Report → uses `sales.commission.line` (synced data)
2. Financial Wizard → uses `account.move` (live data)

The wizard's live query approach has stricter filters that don't match what exists in commission lines, causing the "no data found" error even when commission line records exist.

**Recommended Solution:** Make the wizard query from `sales.commission.line` for consistency, performance, and reliability.

---

## Additional Notes

### Why This Design Exists
The wizard appears to have been designed to provide "real-time" reporting without depending on the sync process. However, this creates:
- Data inconsistency
- Performance overhead (recalculating everything)
- Complex logic duplication
- Maintenance burden

### Best Practice
In Odoo, it's better to have:
1. A scheduled action that computes/syncs data → `commission_service.py` ✓
2. Reports that query the synced data → Should apply to wizard too
3. Clear separation between computation and presentation

This approach is more maintainable and performant.
