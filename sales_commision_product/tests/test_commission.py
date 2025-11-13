# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
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
        
        # Create test data
        self.partner = self.Partner.create({
            'name': 'Test Customer',
        })
        
        self.salesperson = self.User.create({
            'name': 'Test Salesperson',
            'login': 'test_salesperson',
            'email': 'salesperson@test.com',
        })
        
        self.product = self.Product.create({
            'name': 'Test Product with Commission',
            'type': 'consu',
            'commission_rate': 10.0,
            'list_price': 100.0,
        })

    def test_commission_line_create(self):
        """Test creating a commission line."""
        invoice = self._create_invoice()
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
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
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
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
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
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
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
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
        
        commission = self.CommissionLine.create({
            'invoice_id': invoice.id,
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

    def _create_invoice(self, move_type='out_invoice', invoice_date=None):
        """Helper method to create a test invoice."""
        if invoice_date is None:
            invoice_date = datetime.today().date()
        
        invoice = self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': self.salesperson.id,
            'move_type': move_type,
            'invoice_date': invoice_date,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1.0,
                'price_unit': 100.0,
            })],
        })
        return invoice
