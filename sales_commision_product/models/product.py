from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    commission_rate = fields.Float(
        string="Commission Rate (%)",
        help="Enter the commission percentage for this product "
             "(e.g., 5.0 for 5%). This rate will be used to calculate "
             "commission on paid invoices.",
    )

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        """Validate commission rate is between 0 and 100."""
        for product in self:
            if product.commission_rate < 0:
                raise ValidationError("Commission rate cannot be negative.")
            if product.commission_rate > 100:
                raise ValidationError("Commission rate cannot exceed 100%.")

