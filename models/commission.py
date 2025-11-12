from odoo import api, fields, models


class SalesCommissionLine(models.Model):
    _name = "sales.commission.line"
    _description = "Sales Commission Line Item"
    _order = "invoice_date desc, id desc"

    salesperson_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        required=True,
        index=True,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        ondelete="cascade",
        required=True,
        index=True,
    )
    invoice_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Invoice Line",
        ondelete="cascade",
        required=True,
        index=True,
    )
    invoice_date = fields.Date(related="invoice_id.invoice_date", store=True)
    move_type = fields.Selection(related="invoice_id.move_type", store=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        index=True,
    )
    quantity = fields.Float(string="Quantity", digits="Product Unit of Measure")
    commission_rate = fields.Float(string="Commission Rate (%)")
    commission_amount = fields.Monetary(
        string="Commission Amount",
        currency_field="company_currency_id",
        required=True,
    )
    line_subtotal = fields.Monetary(
        string="Line Subtotal",
        currency_field="company_currency_id",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Company Currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "unique_invoice_line",
            "unique(invoice_line_id, company_id)",
            "Commission line already exists for this invoice line.",
        ),
    ]

    @api.model
    def create(self, vals):
        # Ensure commission_rate mirrors the related product rate if not provided
        if not vals.get("commission_rate") and vals.get("product_id"):
            product = self.env["product.product"].browse(vals["product_id"])
            vals["commission_rate"] = product.product_tmpl_id.commission_rate
        return super().create(vals)

