#!/usr/bin/env python3
"""
Commission Demo Data Creator
============================

This script creates comprehensive demo invoices with different payment states
to test all commission filtering scenarios.

Run this in Odoo shell after installing the module with demo data:
exec(open('/path/to/create_demo_invoices.py').read())
"""

from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)

def create_demo_invoices(env):
    """Create demo invoices for all commission scenarios."""
    
    print("=" * 80)
    print("CREATING COMMISSION DEMO INVOICES")
    print("=" * 80)
    
    # Get demo data references
    try:
        # Products
        laptop = env.ref('sales_commision_product.product_laptop_demo')
        smartphone = env.ref('sales_commision_product.product_smartphone_demo')
        tablet = env.ref('sales_commision_product.product_tablet_demo')
        monitor = env.ref('sales_commision_product.product_monitor_demo')
        keyboard = env.ref('sales_commision_product.product_keyboard_demo')
        mouse = env.ref('sales_commision_product.product_mouse_demo')
        no_commission = env.ref('sales_commision_product.product_no_commission_demo')
        
        # Salespersons
        john = env.ref('sales_commision_product.user_salesperson_john')
        sarah = env.ref('sales_commision_product.user_salesperson_sarah')
        mike = env.ref('sales_commision_product.user_salesperson_mike')
        
        # Customers
        acme = env.ref('sales_commision_product.partner_customer_acme')
        techcorp = env.ref('sales_commision_product.partner_customer_techcorp')
        globalinc = env.ref('sales_commision_product.partner_customer_globalinc')
        startup = env.ref('sales_commision_product.partner_customer_startup')
        enterprise = env.ref('sales_commision_product.partner_customer_enterprise')
        
    except Exception as e:
        print(f"❌ Error loading demo data references: {e}")
        print("Make sure the module is installed with demo data!")
        return
    
    # Get or create accounting setup
    company = env.company
    
    # Find or create necessary accounts
    receivable_account = env['account.account'].search([
        ('account_type', '=', 'asset_receivable'),
        ('company_id', '=', company.id)
    ], limit=1)
    
    if not receivable_account:
        receivable_account = env['account.account'].create({
            'name': 'Demo Accounts Receivable',
            'code': 'DEMO120000',
            'account_type': 'asset_receivable',
            'reconcile': True,
            'company_id': company.id,
        })
    
    income_account = env['account.account'].search([
        ('account_type', '=', 'income'),
        ('company_id', '=', company.id)
    ], limit=1)
    
    if not income_account:
        income_account = env['account.account'].create({
            'name': 'Demo Product Sales',
            'code': 'DEMO400000',
            'account_type': 'income',
            'company_id': company.id,
        })
    
    # Find or create sale journal
    sale_journal = env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id', '=', company.id)
    ], limit=1)
    
    if not sale_journal:
        sale_journal = env['account.journal'].create({
            'name': 'Demo Sales Journal',
            'code': 'DSALE',
            'type': 'sale',
            'company_id': company.id,
        })
    
    # Find bank journal for payments
    bank_journal = env['account.journal'].search([
        ('type', '=', 'bank'),
        ('company_id', '=', company.id)
    ], limit=1)
    
    if not bank_journal:
        bank_account = env['account.account'].create({
            'name': 'Demo Bank Account',
            'code': 'DEMO100000',
            'account_type': 'asset_current',
            'company_id': company.id,
        })
        bank_journal = env['account.journal'].create({
            'name': 'Demo Bank Journal',
            'code': 'DBANK',
            'type': 'bank',
            'company_id': company.id,
            'default_account_id': bank_account.id,
        })
    
    # Set receivable account on customers
    for customer in [acme, techcorp, globalinc, startup, enterprise]:
        customer.write({
            'property_account_receivable_id': receivable_account.id,
            'property_payment_term_id': False,
        })
    
    # Set income account on products
    for product in [laptop, smartphone, tablet, monitor, keyboard, mouse, no_commission]:
        product.write({
            'property_account_income_id': income_account.id,
        })
    
    # Calculate dates
    today = date.today()
    days_15_ago = today - timedelta(days=15)
    days_10_ago = today - timedelta(days=10)
    days_8_ago = today - timedelta(days=8)
    days_5_ago = today - timedelta(days=5)
    days_3_ago = today - timedelta(days=3)
    days_2_ago = today - timedelta(days=2)
    yesterday = today - timedelta(days=1)
    
    invoices_created = []
    
    try:
        # === SCENARIO 1: John's PAID Invoice ===
        print("\n📄 Creating Scenario 1: John's PAID invoice...")
        invoice_1 = env['account.move'].create({
            'partner_id': acme.id,
            'invoice_user_id': john.id,
            'move_type': 'out_invoice',
            'invoice_date': days_15_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': laptop.id,
                    'quantity': 3.0,
                    'price_unit': 1500.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': monitor.id,
                    'quantity': 3.0,
                    'price_unit': 450.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_1.action_post()
        _register_payment(env, invoice_1, bank_journal)
        invoices_created.append(('PAID', invoice_1.name, john.name, invoice_1.amount_total))
        
        # === SCENARIO 2: Sarah's UNPAID Invoice ===
        print("📄 Creating Scenario 2: Sarah's UNPAID invoice...")
        invoice_2 = env['account.move'].create({
            'partner_id': techcorp.id,
            'invoice_user_id': sarah.id,
            'move_type': 'out_invoice',
            'invoice_date': days_10_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': smartphone.id,
                    'quantity': 10.0,
                    'price_unit': 899.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': tablet.id,
                    'quantity': 5.0,
                    'price_unit': 650.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_2.action_post()
        # Leave unpaid
        invoices_created.append(('UNPAID', invoice_2.name, sarah.name, invoice_2.amount_total))
        
        # === SCENARIO 3: Mike's PAID Invoice ===
        print("📄 Creating Scenario 3: Mike's PAID invoice...")
        invoice_3 = env['account.move'].create({
            'partner_id': globalinc.id,
            'invoice_user_id': mike.id,
            'move_type': 'out_invoice',
            'invoice_date': days_8_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': keyboard.id,
                    'quantity': 20.0,
                    'price_unit': 120.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': mouse.id,
                    'quantity': 20.0,
                    'price_unit': 45.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_3.action_post()
        _register_payment(env, invoice_3, bank_journal)
        invoices_created.append(('PAID', invoice_3.name, mike.name, invoice_3.amount_total))
        
        # === SCENARIO 4: John's UNPAID Large Order ===
        print("📄 Creating Scenario 4: John's UNPAID large order...")
        invoice_4 = env['account.move'].create({
            'partner_id': startup.id,
            'invoice_user_id': john.id,
            'move_type': 'out_invoice',
            'invoice_date': days_5_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': tablet.id,
                    'quantity': 15.0,
                    'price_unit': 650.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_4.action_post()
        # Leave unpaid
        invoices_created.append(('UNPAID', invoice_4.name, john.name, invoice_4.amount_total))
        
        # === SCENARIO 5: Sarah's Recent PAID Order ===
        print("📄 Creating Scenario 5: Sarah's recent PAID order...")
        invoice_5 = env['account.move'].create({
            'partner_id': enterprise.id,
            'invoice_user_id': sarah.id,
            'move_type': 'out_invoice',
            'invoice_date': days_3_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': laptop.id,
                    'quantity': 5.0,
                    'price_unit': 1500.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': monitor.id,
                    'quantity': 5.0,
                    'price_unit': 450.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': keyboard.id,
                    'quantity': 5.0,
                    'price_unit': 120.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_5.action_post()
        _register_payment(env, invoice_5, bank_journal)
        invoices_created.append(('PAID', invoice_5.name, sarah.name, invoice_5.amount_total))
        
        # === SCENARIO 6: Mike's Recent UNPAID Order ===
        print("📄 Creating Scenario 6: Mike's recent UNPAID order...")
        invoice_6 = env['account.move'].create({
            'partner_id': acme.id,
            'invoice_user_id': mike.id,
            'move_type': 'out_invoice',
            'invoice_date': yesterday,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': smartphone.id,
                    'quantity': 8.0,
                    'price_unit': 899.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': tablet.id,
                    'quantity': 2.0,
                    'price_unit': 650.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_6.action_post()
        # Leave unpaid
        invoices_created.append(('UNPAID', invoice_6.name, mike.name, invoice_6.amount_total))
        
        # === SCENARIO 7: John's PARTIALLY PAID Invoice ===
        print("📄 Creating Scenario 7: John's PARTIALLY paid invoice...")
        invoice_7 = env['account.move'].create({
            'partner_id': techcorp.id,
            'invoice_user_id': john.id,
            'move_type': 'out_invoice',
            'invoice_date': days_2_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': laptop.id,
                    'quantity': 2.0,
                    'price_unit': 1500.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_7.action_post()
        # Register partial payment (50%)
        _register_payment(env, invoice_7, bank_journal, invoice_7.amount_total * 0.5)
        invoices_created.append(('PARTIAL', invoice_7.name, john.name, invoice_7.amount_total))
        
        # === SCENARIO 8: Mike's REFUND ===
        print("📄 Creating Scenario 8: Mike's REFUND...")
        refund_1 = env['account.move'].create({
            'partner_id': globalinc.id,
            'invoice_user_id': mike.id,
            'move_type': 'out_refund',
            'invoice_date': days_2_ago,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': keyboard.id,
                    'quantity': 3.0,
                    'price_unit': 120.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        refund_1.action_post()
        # Refunds don't need payment registration
        invoices_created.append(('REFUND', refund_1.name, mike.name, refund_1.amount_total))
        
        # === SCENARIO 9: Invoice with NO COMMISSION product ===
        print("📄 Creating Scenario 9: Invoice with NO commission product...")
        invoice_no_comm = env['account.move'].create({
            'partner_id': startup.id,
            'invoice_user_id': sarah.id,
            'move_type': 'out_invoice',
            'invoice_date': yesterday,
            'journal_id': sale_journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': no_commission.id,
                    'quantity': 5.0,
                    'price_unit': 200.0,
                    'account_id': income_account.id,
                }),
                (0, 0, {
                    'product_id': laptop.id,  # This has commission
                    'quantity': 1.0,
                    'price_unit': 1500.0,
                    'account_id': income_account.id,
                }),
            ],
        })
        invoice_no_comm.action_post()
        _register_payment(env, invoice_no_comm, bank_journal)
        invoices_created.append(('PAID+NO_COMM', invoice_no_comm.name, sarah.name, invoice_no_comm.amount_total))
        
    except Exception as e:
        print(f"❌ Error creating invoices: {e}")
        return
    
    # Display summary
    print("\n" + "=" * 80)
    print("✅ DEMO INVOICES CREATED SUCCESSFULLY!")
    print("=" * 80)
    
    print("\n📋 INVOICE SUMMARY:")
    total_amount = 0
    for status, name, salesperson, amount in invoices_created:
        print(f"  {status:12} | {name:15} | {salesperson:20} | ${amount:8,.2f}")
        total_amount += amount
    
    print(f"\nTotal Demo Invoices Created: {len(invoices_created)}")
    print(f"Total Demo Amount: ${total_amount:,.2f}")
    
    # Run commission sync
    print("\n🔄 RUNNING COMMISSION SYNC...")
    commission_service = env['sales.commission.service']
    result = commission_service.run_commission_sync()
    
    if result:
        commission_count = env['sales.commission.line'].search_count([])
        print(f"✅ Commission sync completed! {commission_count} commission lines created.")
    else:
        print("❌ Commission sync failed!")
    
    print("\n🎯 TESTING INSTRUCTIONS:")
    print("-" * 40)
    print("1. Navigate to: Sales → Reporting → Commission Financial Report")
    print("2. Test these filter combinations:")
    print("   • 'Posted Only (Not Paid)' - Should show forecast commissions")
    print("   • 'Paid Only' - Should show actual earned commissions")
    print("   • 'All Posted Invoices' - Should show combined data")
    print("3. Try different date ranges and salesperson filters")
    print("4. Export to Excel/PDF to test report generation")
    print("\n" + "=" * 80)


def _register_payment(env, invoice, journal, amount=None):
    """Register payment for an invoice."""
    if amount is None:
        amount = invoice.amount_total
    
    try:
        payment_register = env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=invoice.ids,
        ).create({
            'journal_id': journal.id,
            'amount': amount,
        })
        payment_register.action_create_payments()
    except Exception as e:
        print(f"⚠️  Warning: Could not register payment for {invoice.name}: {e}")


# Main execution
if 'env' in globals():
    create_demo_invoices(env)
else:
    print("This script should be run in Odoo shell context.")
    print("Example:")
    print("  odoo-bin shell -c /path/to/odoo.conf -d your_database")
    print("  >>> exec(open('/path/to/create_demo_invoices.py').read())")