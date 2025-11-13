# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestCommissionService(TransactionCase):
    """Test cases for commission service."""

    def setUp(self):
        super(TestCommissionService, self).setUp()
        self.CommissionService = self.env['sales.commission.service']
        self.CommissionLine = self.env['sales.commission.line']
        self.Product = self.env['product.product']
        self.Partner = self.env['res.partner']
        self.User = self.env['res.users']
        self.AccountMove = self.env['account.move']
        
        # Create sale journal if it doesn't exist
        self.journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not self.journal:
            self.journal = self.env['account.journal'].create({
                'name': 'Test Sale Journal',
                'code': 'TSJ',
                'type': 'sale',
                'company_id': self.env.company.id,
            })
        
        # Create test data
        self.partner = self.Partner.create({
            'name': 'Test Customer',
        })
        
        self.salesperson = self.User.create({
            'name': 'Test Salesperson',
            'login': 'test_salesperson_service',
            'email': 'salesperson_service@test.com',
        })
        
        self.product_with_commission = self.Product.create({
            'name': 'Product with Commission',
            'type': 'consu',
            'commission_rate': 15.0,
            'list_price': 200.0,
        })
        
        self.product_without_commission = self.Product.create({
            'name': 'Product without Commission',
            'type': 'consu',
            'commission_rate': 0.0,
            'list_price': 100.0,
        })
        
        # Get income account for invoice lines
        self.account_income = self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not self.account_income:
            self.account_income = self.env['account.account'].create({
                'name': 'Product Sales',
                'code': 'TEST401',
                'account_type': 'income',
                'company_id': self.env.company.id,
            })

    def test_run_commission_sync_creates_lines(self):
        """Test that run_commission_sync creates commission lines for paid invoices."""
        # Create and post an invoice
        invoice = self._create_and_post_invoice()
        
        # Mark invoice as paid
        self._mark_invoice_paid(invoice)
        
        # Clear existing commission lines
        self.CommissionLine.search([]).unlink()
        
        # Run commission sync
        result = self.CommissionService.run_commission_sync()
        
        self.assertTrue(result)
        
        # Check commission lines created
        commission_lines = self.CommissionLine.search([
            ('invoice_id', '=', invoice.id)
        ])
        
        self.assertTrue(commission_lines)
        self.assertEqual(len(commission_lines), 1)  # One line with commission
        
        commission = commission_lines[0]
        self.assertEqual(commission.salesperson_id.id, self.salesperson.id)
        self.assertEqual(commission.product_id.id, self.product_with_commission.id)
        self.assertEqual(commission.commission_rate, 15.0)
        # Commission = 200 * 15% = 30
        self.assertAlmostEqual(commission.commission_amount, 30.0, places=2)

    def test_run_commission_sync_skips_unpaid_invoices(self):
        """Test that sync skips unpaid invoices."""
        # Create and post invoice (but don't mark as paid)
        invoice = self._create_and_post_invoice()
        
        # Clear existing commission lines
        self.CommissionLine.search([]).unlink()
        
        # Run commission sync
        self.CommissionService.run_commission_sync()
        
        # Check no commission lines created for unpaid invoice
        commission_lines = self.CommissionLine.search([
            ('invoice_id', '=', invoice.id)
        ])
        
        self.assertFalse(commission_lines)

    def test_run_commission_sync_skips_zero_commission_products(self):
        """Test that sync skips products with 0% commission rate."""
        # Create invoice with product without commission
        invoice = self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': self.salesperson.id,
            'move_type': 'out_invoice',
            'invoice_date': datetime.today().date(),
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_without_commission.id,
                'quantity': 1.0,
                'price_unit': 100.0,
                'account_id': self.account_income.id,
            })],
        })
        invoice.action_post()
        self._mark_invoice_paid(invoice)
        
        # Clear existing commission lines
        self.CommissionLine.search([]).unlink()
        
        # Run commission sync
        self.CommissionService.run_commission_sync()
        
        # Check no commission lines created
        commission_lines = self.CommissionLine.search([
            ('invoice_id', '=', invoice.id)
        ])
        
        self.assertFalse(commission_lines)

    def test_run_commission_sync_handles_refunds(self):
        """Test that sync handles refunds correctly (negative commission)."""
        # Create and post a refund
        refund = self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': self.salesperson.id,
            'move_type': 'out_refund',
            'invoice_date': datetime.today().date(),
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_with_commission.id,
                'quantity': 1.0,
                'price_unit': 200.0,
                'account_id': self.account_income.id,
            })],
        })
        refund.action_post()
        self._mark_invoice_paid(refund)
        
        # Clear existing commission lines
        self.CommissionLine.search([]).unlink()
        
        # Run commission sync
        self.CommissionService.run_commission_sync()
        
        # Check commission lines created with negative amounts
        commission_lines = self.CommissionLine.search([
            ('invoice_id', '=', refund.id)
        ])
        
        self.assertTrue(commission_lines)
        commission = commission_lines[0]
        self.assertEqual(commission.move_type, 'out_refund')
        self.assertLess(commission.commission_amount, 0)

    def test_run_commission_sync_prevents_duplicates(self):
        """Test that sync doesn't create duplicate commission lines."""
        # Create and post an invoice
        invoice = self._create_and_post_invoice()
        self._mark_invoice_paid(invoice)
        
        # Clear existing commission lines
        self.CommissionLine.search([]).unlink()
        
        # Run sync first time
        self.CommissionService.run_commission_sync()
        count_first = self.CommissionLine.search_count([
            ('invoice_id', '=', invoice.id)
        ])
        
        # Run sync second time
        self.CommissionService.run_commission_sync()
        count_second = self.CommissionLine.search_count([
            ('invoice_id', '=', invoice.id)
        ])
        
        # Should not create duplicates
        self.assertEqual(count_first, count_second)

    def test_run_commission_sync_error_handling(self):
        """Test that sync handles errors gracefully."""
        with patch.object(self.CommissionLine, 'search', side_effect=Exception('Test error')):
            result = self.CommissionService.run_commission_sync()
            # Should return False on error
            self.assertFalse(result)

    def _create_and_post_invoice(self):
        """Helper method to create and post an invoice."""
        invoice = self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': self.salesperson.id,
            'move_type': 'out_invoice',
            'invoice_date': datetime.today().date(),
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_with_commission.id,
                'quantity': 1.0,
                'price_unit': 200.0,
                'account_id': self.account_income.id,
            })],
        })
        invoice.action_post()
        return invoice

    def _mark_invoice_paid(self, invoice):
        """Helper method to mark an invoice as paid."""
        # In Odoo 16, we need to register payment
        payment_register = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=invoice.ids,
        ).create({
            'payment_date': invoice.invoice_date,
        })
        payment_register.action_create_payments()
