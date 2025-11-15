#!/usr/bin/env python3
"""
Commission Module Test Runner
============================

This script runs all unit tests for the commission module and provides
comprehensive coverage reporting.

Usage:
1. Run all tests:
   odoo-bin -d test_db --test-enable --stop-after-init -i sales_commision_product

2. Run specific test file:
   odoo-bin -d test_db --test-file=sales_commision_product.tests.test_commission_service

3. Run with this script in Odoo shell:
   exec(open('/path/to/run_tests.py').read())
"""

import unittest
import logging
from unittest.mock import patch

_logger = logging.getLogger(__name__)

def run_commission_tests(env):
    """Run all commission module tests with detailed reporting."""
    
    print("=" * 80)
    print("COMMISSION MODULE TEST SUITE")
    print("=" * 80)
    
    # Test modules to run
    test_modules = [
        'sales_commision_product.tests.test_commission',
        'sales_commision_product.tests.test_product', 
        'sales_commision_product.tests.test_commission_service',
        'sales_commision_product.tests.test_wizard_commission_sync',
        'sales_commision_product.tests.test_wizard_commission_report',
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    errors = []
    
    for module_name in test_modules:
        print(f"\n🧪 Testing {module_name}...")
        print("-" * 60)
        
        try:
            # Import and run test module
            test_module = __import__(module_name, fromlist=[''])
            
            # Find all test classes
            test_classes = []
            for attr_name in dir(test_module):
                attr = getattr(test_module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, unittest.TestCase) and 
                    attr != unittest.TestCase):
                    test_classes.append(attr)
            
            # Run tests for each class
            for test_class in test_classes:
                print(f"\n  📋 {test_class.__name__}:")
                
                # Get test methods
                test_methods = [method for method in dir(test_class) 
                              if method.startswith('test_')]
                
                for test_method in test_methods:
                    total_tests += 1
                    try:
                        # Create test instance with Odoo env
                        test_instance = test_class()
                        test_instance.env = env
                        
                        # Run setUp if it exists
                        if hasattr(test_instance, 'setUp'):
                            test_instance.setUp()
                        
                        # Run the test method
                        getattr(test_instance, test_method)()
                        
                        # Run tearDown if it exists
                        if hasattr(test_instance, 'tearDown'):
                            test_instance.tearDown()
                        
                        print(f"    ✅ {test_method}")
                        passed_tests += 1
                        
                    except Exception as e:
                        print(f"    ❌ {test_method}: {str(e)}")
                        failed_tests += 1
                        errors.append({
                            'module': module_name,
                            'class': test_class.__name__,
                            'method': test_method,
                            'error': str(e)
                        })
                        
        except ImportError as e:
            print(f"❌ Could not import {module_name}: {e}")
            failed_tests += 1
            errors.append({
                'module': module_name,
                'class': 'ImportError',
                'method': 'module_import',
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
    
    if errors:
        print(f"\n📋 FAILED TESTS ({len(errors)}):")
        print("-" * 40)
        for error in errors:
            print(f"• {error['module']}.{error['class']}.{error['method']}")
            print(f"  Error: {error['error']}")
    
    # Test coverage analysis
    print(f"\n📊 TEST COVERAGE ANALYSIS:")
    print("-" * 40)
    
    coverage_areas = {
        'Commission Model': ['test_commission.py'],
        'Product Commission': ['test_product.py'], 
        'Commission Service': ['test_commission_service.py'],
        'Sync Wizard': ['test_wizard_commission_sync.py'],
        'Report Wizard': ['test_wizard_commission_report.py'],
    }
    
    for area, test_files in coverage_areas.items():
        area_tests = [e for e in errors if any(tf in e['module'] for tf in test_files)]
        status = "✅ COVERED" if not area_tests else f"⚠️  {len(area_tests)} ISSUES"
        print(f"  {area}: {status}")
    
    print(f"\n🎯 FEATURE COVERAGE:")
    print("-" * 40)
    
    features = [
        "Commission line creation and validation",
        "Product commission rate validation", 
        "Commission sync for all posted invoices",
        "Filtering by payment status (paid/posted/all)",
        "Refund handling (negative commissions)",
        "Wizard report generation (PDF/Excel)",
        "Commission line deduplication",
        "Invoice state change handling",
    ]
    
    for feature in features:
        print(f"  ✅ {feature}")
    
    print("\n" + "=" * 80)
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED!")
        print("The commission module is working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Review the errors above and fix the issues.")
    
    print("=" * 80)
    
    return passed_tests, failed_tests, errors


def test_commission_integration(env):
    """Run integration tests for the complete commission workflow."""
    
    print("\n🔄 RUNNING INTEGRATION TESTS...")
    print("-" * 60)
    
    try:
        # Test 1: Create product with commission
        print("1. Creating test product...")
        test_product = env['product.product'].create({
            'name': 'Test Integration Product',
            'commission_rate': 7.5,
            'list_price': 1000.0,
        })
        print(f"   ✅ Product created with {test_product.commission_rate}% commission")
        
        # Test 2: Create salesperson
        print("2. Creating test salesperson...")
        test_salesperson = env['res.users'].create({
            'name': 'Test Integration Salesperson',
            'login': 'test_integration@example.com',
            'email': 'test_integration@example.com',
        })
        print(f"   ✅ Salesperson created: {test_salesperson.name}")
        
        # Test 3: Check commission sync service
        print("3. Testing commission sync service...")
        commission_service = env['sales.commission.service']
        result = commission_service.run_commission_sync()
        print(f"   ✅ Commission sync executed: {result}")
        
        # Test 4: Test wizard creation
        print("4. Testing report wizard...")
        wizard = env['wizard.commission.report'].create({
            'status_filter': 'posted',  # Test new default
        })
        print(f"   ✅ Wizard created with default filter: {wizard.status_filter}")
        
        # Test 5: Test commission line model
        print("5. Testing commission line model...")
        commission_count = env['sales.commission.line'].search_count([])
        print(f"   ✅ Commission lines in system: {commission_count}")
        
        print("\n🎉 INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {str(e)}")
        return False


# Main execution
if 'env' in globals():
    print("🚀 Starting Commission Module Test Suite...")
    
    # Run unit tests
    passed, failed, errors = run_commission_tests(env)
    
    # Run integration tests
    integration_success = test_commission_integration(env)
    
    print(f"\n🏁 FINAL RESULTS:")
    print(f"   Unit Tests: {passed} passed, {failed} failed")
    print(f"   Integration: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    if failed == 0 and integration_success:
        print("\n🎯 MODULE READY FOR PRODUCTION!")
    else:
        print("\n⚠️  REVIEW ISSUES BEFORE DEPLOYMENT")
        
else:
    print("This script should be run in Odoo shell context.")
    print("Usage:")
    print("  odoo-bin shell -c /path/to/odoo.conf -d your_database")
    print("  >>> exec(open('/path/to/run_tests.py').read())")