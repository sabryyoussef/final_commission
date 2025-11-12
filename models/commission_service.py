from odoo import api, fields, models
from odoo.tools import float_compare


class CommissionService(models.Model):
    _name = "sales.commission.service"
    _description = "Sales Commission Computation Service"
    _log_access = False

    last_processed_move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Last Processed Move Line",
        help="Technical field to avoid duplicate commission entries.",
    )

    @api.model
    def _get_service(self):
        service = self.search([], limit=1)
        if not service:
            service = self.create({})
        return service

    @api.model
    def run_commission_sync(self):
        self._get_service()  # ensure record exists for backward compatibility
        move_line_model = self.env["account.move.line"]
        commission_line_model = self.env["sales.commission.line"]

        invoice_lines = move_line_model.search([
            ("parent_state", "=", "posted"),
            ("move_id.state", "=", "posted"),
            ("move_id.move_type", "=", "out_invoice"),
            ("move_id.payment_state", "in", ["paid"]),
            ("product_id", "!=", False),
            ("display_type", "=", False),
        ])

        refund_lines = move_line_model.search([
            ("parent_state", "=", "posted"),
            ("move_id.state", "=", "posted"),
            ("move_id.move_type", "=", "out_refund"),
            ("product_id", "!=", False),
            ("display_type", "=", False),
        ])

        eligible_lines = invoice_lines | refund_lines

        eligible_map = {}
        for line in eligible_lines:
            commission_rate = line.product_id.product_tmpl_id.commission_rate
            if not commission_rate:
                continue

            move = line.move_id
            base_amount = line.price_subtotal
            commission_amount = base_amount * (commission_rate / 100.0)
            if move.move_type == "out_refund":
                commission_amount *= -1

            salesperson = move.invoice_user_id or move.user_id or self.env.user

            eligible_map[line.id] = {
                "salesperson_id": salesperson.id,
                "invoice_id": move.id,
                "invoice_line_id": line.id,
                "product_id": line.product_id.id,
                "quantity": line.quantity,
                "commission_rate": commission_rate,
                "commission_amount": commission_amount,
                "line_subtotal": base_amount,
                "company_id": move.company_id.id,
            }

        existing_lines = commission_line_model.search([])
        create_vals = []

        for commission_line in existing_lines:
            line_vals = eligible_map.pop(commission_line.invoice_line_id.id, None)
            if not line_vals:
                commission_line.unlink()
                continue

            updates = {}
            if commission_line.salesperson_id.id != line_vals["salesperson_id"]:
                updates["salesperson_id"] = line_vals["salesperson_id"]
            if commission_line.invoice_id.id != line_vals["invoice_id"]:
                updates["invoice_id"] = line_vals["invoice_id"]
            if commission_line.product_id.id != line_vals["product_id"]:
                updates["product_id"] = line_vals["product_id"]
            uom = commission_line.invoice_line_id.product_uom_id
            qty_differs = False
            if uom and uom.rounding:
                qty_differs = float_compare(
                    commission_line.quantity,
                    line_vals["quantity"],
                    precision_rounding=uom.rounding,
                )
            else:
                qty_differs = float_compare(
                    commission_line.quantity,
                    line_vals["quantity"],
                    precision_digits=6,
                )
            if qty_differs:
                updates["quantity"] = line_vals["quantity"]
            if float_compare(commission_line.commission_rate, line_vals["commission_rate"], precision_digits=4):
                updates["commission_rate"] = line_vals["commission_rate"]

            currency = commission_line.company_currency_id
            if currency and not currency.is_zero(commission_line.commission_amount - line_vals["commission_amount"]):
                updates["commission_amount"] = line_vals["commission_amount"]
            if currency and not currency.is_zero(commission_line.line_subtotal - line_vals["line_subtotal"]):
                updates["line_subtotal"] = line_vals["line_subtotal"]
            if commission_line.company_id.id != line_vals["company_id"]:
                updates["company_id"] = line_vals["company_id"]

            if updates:
                commission_line.write(updates)

        if eligible_map:
            create_vals.extend(eligible_map.values())
            commission_line_model.create(create_vals)

