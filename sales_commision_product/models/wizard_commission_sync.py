from odoo import api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WizardCommissionSync(models.TransientModel):
    _name = "wizard.commission.sync"
    _description = "Commission Sync Wizard"

    message = fields.Html(
        string="Message",
        readonly=True,
    )

    def action_run_sync(self):
        """Run the commission sync and display results."""
        self.ensure_one()
        try:
            service = self.env["sales.commission.service"]
            result = service.run_commission_sync()
            
            if result:
                # Count commission lines for feedback
                commission_count = self.env["sales.commission.line"].search_count([])
                self.message = f"""
                    <div class="alert alert-success" role="alert">
                        <h4>✅ Commission Sync Completed Successfully!</h4>
                        <p>Total commission lines in database: <strong>{commission_count}</strong></p>
                        <p>The commission data has been synchronized. You can now view the updated report.</p>
                    </div>
                """
            else:
                self.message = """
                    <div class="alert alert-danger" role="alert">
                        <h4>❌ Commission Sync Failed</h4>
                        <p>An error occurred during the sync. Please check the Odoo logs for details.</p>
                    </div>
                """
            
            return {
                "type": "ir.actions.act_window",
                "name": "Commission Sync",
                "res_model": "wizard.commission.sync",
                "view_mode": "form",
                "target": "new",
                "res_id": self.id,
            }
        except Exception as e:
            _logger.error("Error in commission sync wizard: %s", str(e), exc_info=True)
            raise UserError(f"An error occurred while running the commission sync: {str(e)}")
