# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestWizardCommissionReport(TransactionCase):
    """Test cases for commission financial report wizard."""

    def setUp(self):
        super(TestWizardCommissionReport, self).setUp()
        self.WizardReport = self.env['wizard.commission.report']
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
                'code': 'TWCR',
                'type': 'sale',
                'company_id': self.env.company.id,
            })
        
        # Create test data
        self.partner = self.Partner.create({
            'name': 'Test Customer Report',
        })
        
        self.salesperson1 = self.User.create({
            'name': 'Salesperson One',
            'login': 'salesperson1_report',
            'email': 'sp1@test.com',
        })
        
        self.salesperson2 = self.User.create({
            'name': 'Salesperson Two',
            'login': 'salesperson2_report',
            'email': 'sp2@test.com',
        })
        
        self.product = self.Product.create({
            'name': 'Test Product Report',
            'type': 'consu',
            'commission_rate': 10.0,
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
                'code': 'TEST402',
                'account_type': 'income',
                'company_id': self.env.company.id,
            })
        
        self.today = datetime.today().date()
        self.yesterday = self.today - timedelta(days=1)

    def test_wizard_create_default_values(self):
        """Test wizard creation with default values."""
        wizard = self.WizardReport.create({})
        
        self.assertTrue(wizard.date_from)
        self.assertTrue(wizard.date_to)
        self.assertEqual(wizard.status_filter, 'paid')
        self.assertFalse(wizard.salesperson_ids)

    def test_wizard_date_validation_valid(self):
        """Test valid date range."""
        wizard = self.WizardReport.create({
            'date_from': self.yesterday,
            'date_to': self.today,
        })
        self.assertEqual(wizard.date_from, self.yesterday)
        self.assertEqual(wizard.date_to, self.today)

    def test_wizard_date_validation_invalid(self):
        """Test invalid date range raises error."""
        with self.assertRaises(UserError):
            self.WizardReport.create({
                'date_from': self.today,
                'date_to': self.yesterday,
            })

    def test_wizard_status_filter_paid(self):
        """Test paid status filter."""
        wizard = self.WizardReport.create({
            'status_filter': 'paid',
        })
        self.assertEqual(wizard.status_filter, 'paid')

    def test_wizard_status_filter_posted(self):
        """Test posted status filter."""
        wizard = self.WizardReport.create({
            'status_filter': 'posted',
        })
        self.assertEqual(wizard.status_filter, 'posted')

    def test_wizard_status_filter_all(self):
        """Test all status filter."""
        wizard = self.WizardReport.create({
            'status_filter': 'all',
        })
        self.assertEqual(wizard.status_filter, 'all')

    def test_wizard_salesperson_filter(self):
        """Test salesperson filter."""
        wizard = self.WizardReport.create({
            'salesperson_ids': [(6, 0, [self.salesperson1.id])],
        })
        self.assertIn(self.salesperson1, wizard.salesperson_ids)

    def test_get_commission_data_no_invoices(self):
        """Test _get_commission_data with no invoices."""
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        data = wizard._get_commission_data()
        self.assertEqual(data, {})

    def test_get_commission_data_with_paid_invoice(self):
        """Test _get_commission_data with paid invoice."""
        # Create and post invoice
        invoice = self._create_invoice(self.salesperson1)
        invoice.action_post()
        self._mark_invoice_paid(invoice)
        
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
            'status_filter': 'paid',
        })
        
        data = wizard._get_commission_data()
        
        self.assertIn(self.salesperson1.id, data)
        sp_data = data[self.salesperson1.id]
        self.assertEqual(sp_data['salesperson'], self.salesperson1)
        self.assertGreater(sp_data['total_commission'], 0)
        self.assertTrue(sp_data['lines'])

    def test_get_commission_data_filters_by_salesperson(self):
        """Test _get_commission_data filters by salesperson."""
        # Create invoices for two salespersons
        invoice1 = self._create_invoice(self.salesperson1)
        invoice1.action_post()
        self._mark_invoice_paid(invoice1)
        
        invoice2 = self._create_invoice(self.salesperson2)
        invoice2.action_post()
        self._mark_invoice_paid(invoice2)
        
        # Filter for only salesperson1
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
            'salesperson_ids': [(6, 0, [self.salesperson1.id])],
        })
        
        data = wizard._get_commission_data()
        
        self.assertIn(self.salesperson1.id, data)
        self.assertNotIn(self.salesperson2.id, data)

    def test_get_commission_data_filters_by_date(self):
        """Test _get_commission_data filters by date range."""
        # Create invoice yesterday
        invoice = self._create_invoice(self.salesperson1, self.yesterday)
        invoice.action_post()
        self._mark_invoice_paid(invoice)
        
        # Query only for today (should find nothing)
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        data = wizard._get_commission_data()
        self.assertEqual(data, {})

    def test_get_commission_data_handles_refunds(self):
        """Test _get_commission_data handles refunds correctly."""
        # Create refund
        refund = self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': self.salesperson1.id,
            'move_type': 'out_refund',
            'invoice_date': self.today,
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1.0,
                'price_unit': 100.0,
            })],
        })
        refund.action_post()
        self._mark_invoice_paid(refund)
        
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        data = wizard._get_commission_data()
        
        self.assertIn(self.salesperson1.id, data)
        sp_data = data[self.salesperson1.id]
        self.assertGreater(sp_data['total_returns'], 0)
        self.assertLess(sp_data['total_commission'], 0)

    def test_action_print_excel_no_data(self):
        """Test Excel export with no data raises error."""
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        with self.assertRaises(UserError):
            wizard.action_print_excel()

    def test_action_print_excel_success(self):
        """Test successful Excel export."""
        # Create invoice
        invoice = self._create_invoice(self.salesperson1)
        invoice.action_post()
        self._mark_invoice_paid(invoice)
        
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        try:
            import openpyxl
            result = wizard.action_print_excel()
            
            self.assertEqual(result['type'], 'ir.actions.act_url')
            self.assertIn('/web/content/', result['url'])
        except ImportError:
            # Skip test if openpyxl not installed
            self.skipTest("openpyxl not installed")

    def test_action_print_excel_no_openpyxl(self):
        """Test Excel export without openpyxl raises error."""
        invoice = self._create_invoice(self.salesperson1)
        invoice.action_post()
        self._mark_invoice_paid(invoice)
        
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        with patch('builtins.__import__', side_effect=ImportError('No module named openpyxl')):
            with self.assertRaises(UserError):
                wizard.action_print_excel()

    def test_action_print_pdf_no_data(self):
        """Test PDF export with no data raises error."""
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        with self.assertRaises(UserError):
            wizard.action_print_pdf()

    def test_action_print_pdf_success(self):
        """Test successful PDF export."""
        # Create invoice
        invoice = self._create_invoice(self.salesperson1)
        invoice.action_post()
        self._mark_invoice_paid(invoice)
        
        wizard = self.WizardReport.create({
            'date_from': self.today,
            'date_to': self.today,
        })
        
        result = wizard.action_print_pdf()
        
        # Should return report action
        self.assertIn('type', result)

    def test_wizard_transient_model(self):
        """Test that wizard is a transient model."""
        self.assertEqual(self.WizardReport._transient, True)

    def _create_invoice(self, salesperson, invoice_date=None):
        """Helper method to create an invoice."""
        if invoice_date is None:
            invoice_date = self.today
        
        return self.AccountMove.create({
            'partner_id': self.partner.id,
            'invoice_user_id': salesperson.id,
            'move_type': 'out_invoice',
            'invoice_date': invoice_date,
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1.0,
                'price_unit': 100.0,
                'account_id': self.account_income.id,
            })],
        })

    def _mark_invoice_paid(self, invoice):
        """Helper method to mark invoice as paid."""
        payment_register = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=invoice.ids,
        ).create({
            'payment_date': invoice.invoice_date,
        })
        payment_register.action_create_payments()
