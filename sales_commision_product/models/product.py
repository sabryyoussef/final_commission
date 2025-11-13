from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    commission_rate = fields.Float(
        string="Commission Rate (%)",
        help="Enter the commission percentage for this product "
             "(e.g., 5.0 for 5%). This rate will be used to calculate "
             "commission on paid invoices.",
    )

