# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import datetime, timedelta


class TestCommission(TransactionCase):
    """Test cases for sales commission line model."""

    def setUp(self):
        super(TestCommission, self).setUp()
        self.CommissionLine = self.env['sales.commission.line']
        self.Product = self.env['product.product']
        self.Partner = self.env['res.partner']
        self.User = self.env['res.users']
        self.AccountMove = self.env['account.move']
        self.AccountAccount = self.env['account.account']
        self.AccountJournal = self.env['account.journal']
        
        company = self.env.company
        
        # Create minimal receivable account
        self.receivable_account = self.AccountAccount.create({
            'name': 'Test Receivable',
            'code': 'TREC001',
            'account_type': 'asset_receivable',
            'reconcile': True,
            'company_id': company.id,
        })
        
        # Create minimal income account
        self.income_account = self.AccountAccount.create({
            'name': 'Test Income',
            'code': 'TINC001',
            'account_type': 'income',
            'company_id': company.id,
        })
        
        # Create sale journal with proper default account
        self.journal = self.AccountJournal.create({
            'name': 'Test Sale Journal',
            'code': 'TSJ',
            'type': 'sale',
            'company_id': company.id,
            'default_account_id': self.income_account.id,
        })
        
        # Create test partner with receivable account and NO payment term
        self.partner = self.Partner.create({
            'name': 'Test Customer',
            'property_account_receivable_id': self.receivable_account.id,
            'property_payment_term_id': False,  # ✅ NO payment terms
        })
        
        # Create test salesperson
        self.salesperson = self.User.create({
            'name': 'Test Salesperson',
            'login': 'test_salesperson',
            'email': 'salesperson@test.com',
        })
        
        # Create test product with income account
        self.product = self.Product.create({
            'name': 'Test Product with Commission',
            'type': 'consu',
            'commission_rate': 10.0,
            'list_price': 100.0,
            'property_account_income_id': self.income_account.id,
        })

    def test_commission_line_create(self):
        """Test creating a commission line."""
        invoice = self._create_invoice()
        invoice_line = invoice.invoice_line_ids[0]
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 5.0,
            'line_subtotal': 500.0,
            'commission_rate': 10.0,
            'commission_amount': 50.0,
            'move_type': 'out_invoice',
        })
        
        self.assertEqual(commission.invoice_id.id, invoice.id)
        self.assertEqual(commission.salesperson_id.id, self.salesperson.id)
        self.assertEqual(commission.product_id.id, self.product.id)
        self.assertEqual(commission.quantity, 5.0)
        self.assertEqual(commission.line_subtotal, 500.0)
        self.assertEqual(commission.commission_rate, 10.0)
        self.assertEqual(commission.commission_amount, 50.0)

    def test_commission_line_search_by_salesperson(self):
        """Test searching commission lines by salesperson."""
        invoice = self._create_invoice()
        invoice_line = invoice.invoice_line_ids[0]
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': 100.0,
            'commission_rate': 10.0,
            'commission_amount': 10.0,
            'move_type': 'out_invoice',
        })
        
        found = self.CommissionLine.search([
            ('salesperson_id', '=', self.salesperson.id)
        ])
        
        self.assertIn(commission, found)

    def test_commission_line_search_by_date_range(self):
        """Test searching commission lines by date range."""
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)
        
        invoice = self._create_invoice(invoice_date=yesterday)
        invoice_line = invoice.invoice_line_ids[0]
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': yesterday,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': 100.0,
            'commission_rate': 10.0,
            'commission_amount': 10.0,
            'move_type': 'out_invoice',
        })
        
        found = self.CommissionLine.search([
            ('invoice_date', '>=', yesterday),
            ('invoice_date', '<=', today)
        ])
        
        self.assertIn(commission, found)

    def test_commission_line_name_get(self):
        """Test name_get method returns correct format."""
        invoice = self._create_invoice()
        invoice_line = invoice.invoice_line_ids[0]
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': 100.0,
            'commission_rate': 10.0,
            'commission_amount': 10.0,
            'move_type': 'out_invoice',
        })
        
        name = commission.name_get()[0][1]
        self.assertIn(self.salesperson.name, name)
        self.assertIn(self.product.name, name)

    def test_commission_line_refund_negative_amount(self):
        """Test that refund commission lines have negative amounts."""
        invoice = self._create_invoice(move_type='out_refund')
        invoice_line = invoice.invoice_line_ids[0]
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': -100.0,
            'commission_rate': 10.0,
            'commission_amount': -10.0,
            'move_type': 'out_refund',
        })
        
        self.assertEqual(commission.move_type, 'out_refund')
        self.assertLess(commission.commission_amount, 0)

    def test_commission_line_create_sets_rate_from_product(self):
        """Test that create method sets commission_rate from product if not provided."""
        invoice = self._create_invoice()
        invoice_line = invoice.invoice_line_ids[0]
        
        # Create commission without specifying commission_rate
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': 100.0,
            'commission_amount': 10.0,
            'move_type': 'out_invoice',
            # commission_rate not specified - should be set from product
        })
        
        # Should automatically set commission_rate from product
        self.assertEqual(commission.commission_rate, self.product.product_tmpl_id.commission_rate)
        self.assertEqual(commission.commission_rate, 10.0)

    def test_commission_line_create_preserves_explicit_rate(self):
        """Test that create method preserves explicitly provided commission_rate."""
        invoice = self._create_invoice()
        invoice_line = invoice.invoice_line_ids[0]
        
        # Create commission with explicit commission_rate
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': 100.0,
            'commission_amount': 15.0,
            'commission_rate': 15.0,  # Explicit rate different from product
            'move_type': 'out_invoice',
        })
        
        # Should preserve explicit rate, not use product rate
        self.assertEqual(commission.commission_rate, 15.0)
        self.assertNotEqual(commission.commission_rate, self.product.product_tmpl_id.commission_rate)

    def test_commission_line_unique_constraint(self):
        """Test that unique constraint prevents duplicate commission lines."""
        invoice = self._create_invoice()
        invoice_line = invoice.invoice_line_ids[0]
        
        # Create first commission line
        self.CommissionLine.create({
            'invoice_id': invoice.id,
            'invoice_line_id': invoice_line.id,
            'invoice_date': invoice.invoice_date,
            'salesperson_id': self.salesperson.id,
            'product_id': self.product.id,
            'quantity': 1.0,
            'line_subtotal': 100.0,
            'commission_amount': 10.0,
            'commission_rate': 10.0,
            'move_type': 'out_invoice',
        })
        
        # Try to create duplicate - should raise constraint error
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            self.CommissionLine.create({
                'invoice_id': invoice.id,
                'invoice_line_id': invoice_line.id,
                'invoice_date': invoice.invoice_date,
                'salesperson_id': self.salesperson.id,
                'product_id': self.product.id,
                'quantity': 2.0,  # Different quantity
                'line_subtotal': 200.0,  # Different subtotal
                'commission_amount': 20.0,  # Different commission
                'commission_rate': 10.0,
                'move_type': 'out_invoice',
            })

    def _create_invoice(self, move_type='out_invoice', invoice_date=None):
        """Helper method to create a test invoice."""
        if invoice_date is None:
            invoice_date = fields.Date.today()
        
        invoice = self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': self.salesperson.id,
            'move_type': move_type,
            'invoice_date': invoice_date,
            'journal_id': self.journal.id,
            'invoice_payment_term_id': False,  # ✅ NO payment terms to avoid dynamic lines
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1.0,
                'price_unit': 100.0,
                'account_id': self.income_account.id,
            })],
        })
        return invoice
