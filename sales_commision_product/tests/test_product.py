# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestProduct(TransactionCase):
    """Test cases for product commission rate functionality."""

    def setUp(self):
        super(TestProduct, self).setUp()
        self.Product = self.env['product.product']
        self.ProductTemplate = self.env['product.template']

    def test_product_commission_rate_default(self):
        """Test that default commission rate is 0.0."""
        product = self.Product.create({
            'name': 'Test Product Default',
            'type': 'consu',
        })
        self.assertEqual(product.commission_rate, 0.0)

    def test_product_commission_rate_set(self):
        """Test setting a valid commission rate."""
        product = self.Product.create({
            'name': 'Test Product Commission',
            'type': 'consu',
            'commission_rate': 15.0,
        })
        self.assertEqual(product.commission_rate, 15.0)

    def test_product_commission_rate_negative(self):
        """Test that negative commission rates raise validation error."""
        with self.assertRaises(ValidationError):
            self.Product.create({
                'name': 'Test Product Negative',
                'type': 'consu',
                'commission_rate': -5.0,
            })

    def test_product_commission_rate_over_100(self):
        """Test that commission rates over 100% raise validation error."""
        with self.assertRaises(ValidationError):
            self.Product.create({
                'name': 'Test Product Over 100',
                'type': 'consu',
                'commission_rate': 150.0,
            })

    def test_product_commission_rate_boundary_0(self):
        """Test boundary value 0%."""
        product = self.Product.create({
            'name': 'Test Product 0%',
            'type': 'consu',
            'commission_rate': 0.0,
        })
        self.assertEqual(product.commission_rate, 0.0)

    def test_product_commission_rate_boundary_100(self):
        """Test boundary value 100%."""
        product = self.Product.create({
            'name': 'Test Product 100%',
            'type': 'consu',
            'commission_rate': 100.0,
        })
        self.assertEqual(product.commission_rate, 100.0)

    def test_product_commission_rate_decimal(self):
        """Test decimal commission rate."""
        product = self.Product.create({
            'name': 'Test Product Decimal',
            'type': 'consu',
            'commission_rate': 12.5,
        })
        self.assertEqual(product.commission_rate, 12.5)

    def test_product_commission_rate_update(self):
        """Test updating commission rate after creation."""
        product = self.Product.create({
            'name': 'Test Product Update',
            'type': 'consu',
            'commission_rate': 10.0,
        })
        product.write({'commission_rate': 20.0})
        self.assertEqual(product.commission_rate, 20.0)

    def test_product_commission_rate_update_invalid(self):
        """Test updating to invalid commission rate raises error."""
        product = self.Product.create({
            'name': 'Test Product Update Invalid',
            'type': 'consu',
            'commission_rate': 10.0,
        })
        with self.assertRaises(ValidationError):
            product.write({'commission_rate': -10.0})
