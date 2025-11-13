"""
RECOMMENDED FIX FOR WIZARD COMMISSION REPORT
===========================================

This is the corrected _get_commission_data() method that should replace
the existing one in wizard_commission_report.py

This fix makes the wizard query from sales.commission.line (the same
data source as the Commission Report) instead of rebuilding everything
from account.move.

BENEFITS:
- Consistent data between Report and Wizard
- Better performance (uses pre-computed data)
- Single source of truth
- Respects commission sync business logic
"""

def _get_commission_data(self):
    """
    Query commission data from sales.commission.line model.
    Returns structured data grouped by salesperson.
    """
    self.ensure_one()
    
    # Build domain for commission lines
    domain = [
        ('invoice_date', '>=', self.date_from),
        ('invoice_date', '<=', self.date_to),
    ]
    
    # Status filter - check the related invoice's payment state
    if self.status_filter == 'paid':
        domain.append(('invoice_id.payment_state', 'in', ['paid', 'in_payment']))
    elif self.status_filter == 'posted':
        domain.append(('invoice_id.payment_state', 'not in', ['paid', 'in_payment']))
    # 'all' doesn't need additional payment_state filter
    
    # Ensure invoice is still posted (in case it was cancelled after sync)
    domain.append(('invoice_id.state', '=', 'posted'))
    
    # Salesperson filter
    if self.salesperson_ids:
        domain.append(('salesperson_id', 'in', self.salesperson_ids.ids))
    
    # Get commission lines ordered by salesperson and date
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
        
        # Handle refunds (already negative in commission line)
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


"""
ALTERNATIVE QUICK FIX (If you want to keep current architecture)
================================================================

If you prefer to keep querying from account.move but just want to see data,
you can relax the payment_state filter by changing lines 63-66 to:

    # Status filter
    if self.status_filter == 'paid':
        domain.append(('payment_state', '=', 'paid'))
    elif self.status_filter == 'posted':
        domain.append(('payment_state', '!=', 'paid'))
    # 'all' includes everything

Or even more permissive:

    # Status filter - only 'paid' is strict, others show all posted
    if self.status_filter == 'paid':
        domain.append(('payment_state', 'in', ['paid', 'in_payment']))
    # For 'posted' and 'all', don't add payment_state filter

However, this doesn't solve the fundamental issue of data inconsistency.
"""


"""
DIAGNOSTIC SCRIPT
=================

Run this in Odoo shell (bin/odoo-bin shell -c odoo.conf) to understand your data:
"""

def diagnose_commission_data(env):
    """
    Run this in Odoo shell to diagnose the commission data issue
    """
    print("=" * 80)
    print("COMMISSION DATA DIAGNOSTIC")
    print("=" * 80)
    
    # 1. Check commission lines
    commission_lines = env['sales.commission.line'].search([])
    print(f"\n✓ Total commission lines in database: {len(commission_lines)}")
    
    if not commission_lines:
        print("✗ No commission lines found! Run commission sync first.")
        return
    
    # 2. Check invoice states
    print("\n" + "-" * 80)
    print("INVOICE STATES FOR COMMISSION LINES:")
    print("-" * 80)
    
    invoice_states = {}
    payment_states = {}
    
    for line in commission_lines:
        inv = line.invoice_id
        state = inv.state
        payment = inv.payment_state
        
        invoice_states[state] = invoice_states.get(state, 0) + 1
        payment_states[payment] = payment_states.get(payment, 0) + 1
    
    print("\nInvoice States:")
    for state, count in invoice_states.items():
        print(f"  {state}: {count} lines")
    
    print("\nPayment States:")
    for state, count in payment_states.items():
        print(f"  {state}: {count} lines")
    
    # 3. Check date range
    print("\n" + "-" * 80)
    print("DATE RANGE:")
    print("-" * 80)
    
    dates = commission_lines.mapped('invoice_date')
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        print(f"Earliest invoice: {min_date}")
        print(f"Latest invoice: {max_date}")
    
    # 4. Check salespersons
    print("\n" + "-" * 80)
    print("SALESPERSONS:")
    print("-" * 80)
    
    salesperson_data = {}
    for line in commission_lines:
        sp = line.salesperson_id
        sp_name = sp.name if sp else "No Salesperson"
        if sp_name not in salesperson_data:
            salesperson_data[sp_name] = {
                'count': 0,
                'total_commission': 0.0,
                'total_sales': 0.0
            }
        salesperson_data[sp_name]['count'] += 1
        salesperson_data[sp_name]['total_commission'] += line.commission_amount
        salesperson_data[sp_name]['total_sales'] += line.line_subtotal
    
    for sp_name, data in salesperson_data.items():
        print(f"\n{sp_name}:")
        print(f"  Lines: {data['count']}")
        print(f"  Total Sales: ${data['total_sales']:,.2f}")
        print(f"  Total Commission: ${data['total_commission']:,.2f}")
    
    # 5. Sample data
    print("\n" + "-" * 80)
    print("SAMPLE COMMISSION LINES (first 5):")
    print("-" * 80)
    
    for line in commission_lines[:5]:
        inv = line.invoice_id
        print(f"\n{line.id}:")
        print(f"  Invoice: {inv.name}")
        print(f"  Date: {line.invoice_date}")
        print(f"  Salesperson: {line.salesperson_id.name if line.salesperson_id else 'None'}")
        print(f"  Product: {line.product_id.name}")
        print(f"  Invoice State: {inv.state}")
        print(f"  Payment State: {inv.payment_state}")
        print(f"  Commission: ${line.commission_amount:,.2f}")
    
    # 6. Check what wizard would find
    print("\n" + "=" * 80)
    print("WIZARD QUERY SIMULATION:")
    print("=" * 80)
    
    from datetime import date
    today = date.today()
    first_of_month = today.replace(day=1)
    
    print(f"\nDefault wizard date range: {first_of_month} to {today}")
    
    # Simulate wizard query
    wizard_domain = [
        ('move_type', 'in', ['out_invoice', 'out_refund']),
        ('state', '=', 'posted'),
        ('invoice_date', '>=', first_of_month),
        ('invoice_date', '<=', today),
        ('payment_state', 'in', ['paid', 'in_payment']),
    ]
    
    wizard_invoices = env['account.move'].search(wizard_domain)
    print(f"Invoices wizard would find: {len(wizard_invoices)}")
    
    if wizard_invoices:
        print("\nWizard would find these invoices:")
        for inv in wizard_invoices[:5]:
            print(f"  - {inv.name} ({inv.invoice_date}): {inv.payment_state}")
    else:
        print("\n✗ Wizard finds NO invoices! This explains 'No data found' error.")
        print("\nPossible reasons:")
        print("  1. No invoices in current month date range")
        print("  2. Invoices not in 'paid' or 'in_payment' state")
        print("  3. Invoices not posted")
    
    # 7. Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if not wizard_invoices:
        print("\n1. Try wizard with:")
        print("   - Expanded date range covering all your invoice dates")
        print("   - Status filter = 'all' instead of 'paid'")
        print("\n2. Or apply the recommended fix to query from sales.commission.line")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)


"""
TO RUN THE DIAGNOSTIC:

1. SSH to your Odoo.sh server or use local Odoo shell:
   $ odoo-bin shell -c /path/to/odoo.conf -d your_database

2. In the shell, run:
   >>> diagnose_commission_data(env)

3. Review the output to understand your data
"""
