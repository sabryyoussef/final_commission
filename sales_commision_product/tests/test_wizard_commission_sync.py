# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from unittest.mock import patch


class TestWizardCommissionSync(TransactionCase):
    """Test cases for commission sync wizard."""

    def setUp(self):
        super(TestWizardCommissionSync, self).setUp()
        self.WizardSync = self.env['wizard.commission.sync']
        self.CommissionService = self.env['sales.commission.service']

    def test_wizard_create(self):
        """Test creating a wizard instance."""
        wizard = self.WizardSync.create({})
        self.assertTrue(wizard)
        self.assertFalse(wizard.message)

    def test_action_run_sync_success(self):
        """Test running sync successfully updates message."""
        wizard = self.WizardSync.create({})
        
        with patch.object(self.CommissionService, 'run_commission_sync', return_value=True):
            result = wizard.action_run_sync()
        
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'wizard.commission.sync')
        self.assertIn('✅', wizard.message)
        self.assertIn('Successfully', wizard.message)

    def test_action_run_sync_failure(self):
        """Test running sync with failure updates message."""
        wizard = self.WizardSync.create({})
        
        with patch.object(self.CommissionService, 'run_commission_sync', return_value=False):
            result = wizard.action_run_sync()
        
        self.assertIn('❌', wizard.message)
        self.assertIn('Failed', wizard.message)

    def test_action_run_sync_exception(self):
        """Test running sync with exception raises UserError."""
        wizard = self.WizardSync.create({})
        
        with patch.object(self.CommissionService, 'run_commission_sync', side_effect=Exception('Test error')):
            with self.assertRaises(UserError):
                wizard.action_run_sync()

    def test_action_run_sync_returns_wizard_view(self):
        """Test that action returns wizard view with updated message."""
        wizard = self.WizardSync.create({})
        
        with patch.object(self.CommissionService, 'run_commission_sync', return_value=True):
            result = wizard.action_run_sync()
        
        self.assertEqual(result['view_mode'], 'form')
        self.assertEqual(result['target'], 'new')
        self.assertEqual(result['res_id'], wizard.id)

    def test_wizard_transient_model(self):
        """Test that wizard is a transient model."""
        self.assertEqual(self.WizardSync._transient, True)
