#!/usr/bin/env python3
"""
Test Commission Filtering Script
===============================

This script helps you test the new commission filtering functionality.
Run this in Odoo shell after implementing the changes.

Usage:
1. SSH to your Odoo server or open local shell:
   odoo-bin shell -c /path/to/odoo.conf -d your_database

2. In the shell, run:
   exec(open('/path/to/test_commission_filters.py').read())
"""

def test_commission_filters(env):
    """Test the new commission filtering functionality."""
    print("=" * 80)
    print("COMMISSION FILTERING TEST")
    print("=" * 80)
    
    # 1. Check current invoice states
    print("\n📊 INVOICE ANALYSIS:")
    print("-" * 40)
    
    posted_invoices = env['account.move'].search([
        ('state', '=', 'posted'),
        ('move_type', '=', 'out_invoice')
    ])
    
    if not posted_invoices:
        print("❌ No posted invoices found!")
        return
    
    payment_states = {}
    for inv in posted_invoices:
        state = inv.payment_state
        payment_states[state] = payment_states.get(state, 0) + 1
    
    print(f"Total posted invoices: {len(posted_invoices)}")
    for state, count in payment_states.items():
        print(f"  - {state}: {count} invoices")
    
    # 2. Run commission sync
    print("\n🔄 RUNNING COMMISSION SYNC:")
    print("-" * 40)
    
    commission_service = env['sales.commission.service']
    result = commission_service.run_commission_sync()
    
    if result:
        print("✅ Commission sync completed successfully!")
    else:
        print("❌ Commission sync failed!")
        return
    
    # 3. Check commission lines created
    print("\n📋 COMMISSION LINES ANALYSIS:")
    print("-" * 40)
    
    commission_lines = env['sales.commission.line'].search([])
    print(f"Total commission lines: {len(commission_lines)}")
    
    if not commission_lines:
        print("❌ No commission lines found!")
        return
    
    # Group by payment state of related invoices
    payment_commission = {}
    for line in commission_lines:
        payment_state = line.invoice_id.payment_state
        if payment_state not in payment_commission:
            payment_commission[payment_state] = {
                'count': 0,
                'total_commission': 0.0,
                'total_sales': 0.0
            }
        payment_commission[payment_state]['count'] += 1
        payment_commission[payment_state]['total_commission'] += line.commission_amount
        payment_commission[payment_state]['total_sales'] += line.line_subtotal
    
    for state, data in payment_commission.items():
        print(f"\n{state.upper()} Invoices:")
        print(f"  - Commission lines: {data['count']}")
        print(f"  - Total sales: ${data['total_sales']:,.2f}")
        print(f"  - Total commission: ${data['total_commission']:,.2f}")
    
    # 4. Test wizard filtering
    print("\n🧪 TESTING WIZARD FILTERS:")
    print("-" * 40)
    
    # Create test wizard
    wizard = env['wizard.commission.report'].create({
        'date_from': env['sales.commission.line'].search([], limit=1).invoice_date,
        'date_to': env['sales.commission.line'].search([('invoice_date', '!=', False)], order='invoice_date desc', limit=1).invoice_date,
    })
    
    # Test each filter
    for filter_type in ['paid', 'posted', 'all']:
        wizard.status_filter = filter_type
        data = wizard._get_commission_data()
        
        total_commission = sum(sp['total_commission'] for sp in data)
        total_sales = sum(sp['total_sales'] for sp in data)
        salesperson_count = len(data)
        
        print(f"\n{filter_type.upper()} Filter:")
        print(f"  - Salespersons: {salesperson_count}")
        print(f"  - Total sales: ${total_sales:,.2f}")
        print(f"  - Total commission: ${total_commission:,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETED!")
    print("\nNext steps:")
    print("1. Navigate to Sales → Reporting → Commission Financial Report")
    print("2. Test different status filters:")
    print("   - 'Posted Only (Not Paid)' for forecast commissions")
    print("   - 'Paid Only' for actual earned commissions")
    print("   - 'All Posted Invoices' for complete picture")
    print("=" * 80)

# If running directly in Odoo shell
if 'env' in globals():
    test_commission_filters(env)
else:
    print("This script should be run in Odoo shell context.")
    print("Example: exec(open('/path/to/test_commission_filters.py').read())")