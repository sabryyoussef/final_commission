#!/usr/bin/env python3
"""
Fix Commission Rate Data Script
===============================

This script fixes any commission lines that might have null or invalid commission rates.
Run this in Odoo shell after the PDF error fix.

Usage:
odoo-bin shell -c /path/to/odoo.conf -d your_database
>>> exec(open('/path/to/fix_commission_rates.py').read())
"""

def fix_commission_rates(env):
    """Fix commission lines with invalid commission rates."""
    print("=" * 80)
    print("FIXING COMMISSION RATE DATA")
    print("=" * 80)
    
    # Find commission lines with null or invalid commission rates
    commission_lines = env['sales.commission.line'].search([
        '|',
        ('commission_rate', '=', False),
        ('commission_rate', '=', None)
    ])
    
    print(f"Found {len(commission_lines)} commission lines with invalid rates")
    
    if not commission_lines:
        print("✅ No commission lines need fixing!")
        return
    
    fixed_count = 0
    
    for line in commission_lines:
        try:
            # Get commission rate from product
            commission_rate = line.product_id.product_tmpl_id.commission_rate or 0.0
            
            # Update the line
            line.write({
                'commission_rate': commission_rate
            })
            
            print(f"Fixed line ID {line.id}: {line.product_id.name} -> {commission_rate}%")
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Error fixing line ID {line.id}: {str(e)}")
    
    print(f"\n✅ Fixed {fixed_count} commission lines!")
    print("PDF reports should now work properly.")
    print("=" * 80)

# Main execution
if 'env' in globals():
    fix_commission_rates(env)
else:
    print("This script should be run in Odoo shell context.")
    print("Example:")
    print("  odoo-bin shell -c /path/to/odoo.conf -d your_database")
    print("  >>> exec(open('/path/to/fix_commission_rates.py').read())")