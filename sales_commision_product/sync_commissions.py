#!/usr/bin/env python3
"""
Manual Commission Sync Script
Run this to manually trigger commission synchronization
"""
import xmlrpc.client

# Odoo connection settings
url = "http://localhost:8116"
db = "odoo162"
username = "admin"  # Change if needed
password = "admin"  # Change to your admin password

def sync_commissions():
    """Manually trigger commission sync"""
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Authentication failed. Check username/password.")
            return
        
        print(f"✅ Authenticated as user ID: {uid}")
        
        # Get models proxy
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Call the commission sync method
        print("🔄 Running commission sync...")
        result = models.execute_kw(
            db, uid, password,
            'sales.commission.service', 'run_commission_sync',
            []
        )
        
        if result:
            print("✅ Commission sync completed successfully!")
        else:
            print("⚠️  Commission sync returned False. Check Odoo logs for details.")
        
        # Check how many commission lines were created
        count = models.execute_kw(
            db, uid, password,
            'sales.commission.line', 'search_count',
            [[]]
        )
        print(f"📊 Total commission lines in database: {count}")
        
        if count > 0:
            # Get commission summary
            lines = models.execute_kw(
                db, uid, password,
                'sales.commission.line', 'search_read',
                [[]],
                {'fields': ['salesperson_id', 'commission_amount', 'line_subtotal'], 'limit': 10}
            )
            print("\n📋 Sample commission lines:")
            for line in lines:
                salesperson = line['salesperson_id'][1] if line['salesperson_id'] else 'Unknown'
                print(f"  - {salesperson}: ${line['commission_amount']:.2f} (on ${line['line_subtotal']:.2f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync_commissions()

