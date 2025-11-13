from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import logging
import base64
from io import BytesIO

_logger = logging.getLogger(__name__)


class WizardCommissionReport(models.TransientModel):
    _name = "wizard.commission.report"
    _description = "Commission Financial Report Wizard"

    salesperson_ids = fields.Many2many(
        'res.users',
        string='Salespersons',
        domain=[('share', '=', False)],
        help="Leave empty to include all salespeople"
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.today
    )
    status_filter = fields.Selection([
        ('paid', 'Paid Only'),
        ('posted', 'Posted Only (Not Paid)'),
        ('all', 'All Posted Invoices')
    ], string='Invoice Status', required=True, default='paid',
        help="Paid: Only fully paid invoices\n"
             "Posted Only: Posted but not paid (forecast)\n"
             "All: Both paid and unpaid posted invoices")

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range."""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError("Date From cannot be later than Date To.")

    def _get_commission_data(self):
        """
        Query live data from account.move and account.move.line.
        Returns structured data grouped by salesperson.
        """
        self.ensure_one()
        
        # Build domain based on filters
        domain = [
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
        ]
        
        # Status filter
        if self.status_filter == 'paid':
            domain.append(('payment_state', 'in', ['paid', 'in_payment']))
        elif self.status_filter == 'posted':
            domain.append(('payment_state', 'not in', ['paid', 'in_payment']))
        
        # Salesperson filter
        if self.salesperson_ids:
            domain.append(('invoice_user_id', 'in', self.salesperson_ids.ids))
        
        # Get invoices
        invoices = self.env['account.move'].search(domain, order='invoice_user_id, invoice_date')
        
        # Structure: {salesperson_id: {data}}
        data_by_salesperson = {}
        
        for invoice in invoices:
            salesperson = invoice.invoice_user_id
            if not salesperson:
                continue
            
            if salesperson.id not in data_by_salesperson:
                data_by_salesperson[salesperson.id] = {
                    'salesperson': salesperson,
                    'total_sales': 0.0,
                    'total_returns': 0.0,
                    'total_commission': 0.0,
                    'lines': []
                }
            
            # Process invoice lines
            for line in invoice.invoice_line_ids:
                if line.display_type or not line.product_id:
                    continue
                
                commission_rate = line.product_id.commission_rate
                if commission_rate <= 0:
                    continue
                
                # Calculate commission
                line_subtotal = line.price_subtotal
                commission_amount = line_subtotal * (commission_rate / 100.0)
                
                # Handle refunds (negative values)
                if invoice.move_type == 'out_refund':
                    line_subtotal = -line_subtotal
                    commission_amount = -commission_amount
                    data_by_salesperson[salesperson.id]['total_returns'] += abs(line_subtotal)
                else:
                    data_by_salesperson[salesperson.id]['total_sales'] += line_subtotal
                
                data_by_salesperson[salesperson.id]['total_commission'] += commission_amount
                
                # Add line detail
                data_by_salesperson[salesperson.id]['lines'].append({
                    'invoice_date': invoice.invoice_date,
                    'invoice_number': invoice.name,
                    'invoice_id': invoice.id,
                    'product_name': line.product_id.display_name,
                    'quantity': line.quantity,
                    'line_subtotal': line_subtotal,
                    'commission_rate': commission_rate,
                    'commission_amount': commission_amount,
                    'move_type': 'Invoice' if invoice.move_type == 'out_invoice' else 'Refund',
                })
        
        return data_by_salesperson

    def action_print_excel(self):
        """Generate Excel report and return as download."""
        self.ensure_one()
        
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            raise UserError("The 'openpyxl' Python library is required for Excel export. "
                          "Please install it or contact your administrator.")
        
        # Get data
        data = self._get_commission_data()
        
        if not data:
            raise UserError("No commission data found for the selected filters.")
        
        # Create workbook
        wb = openpyxl.Workbook()
        
        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])
        
        # Create Summary sheet
        ws_summary = wb.create_sheet('Summary')
        
        # Header styling
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        
        # Summary headers
        headers_summary = ['Salesperson', 'Total Sales', 'Total Returns', 'Net Sales', 'Total Commission']
        for col_num, header in enumerate(headers_summary, 1):
            cell = ws_summary.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Summary data
        row_num = 2
        grand_sales = 0.0
        grand_returns = 0.0
        grand_commission = 0.0
        
        for sp_id in sorted(data.keys(), key=lambda x: data[x]['salesperson'].name):
            sp_data = data[sp_id]
            total_sales = sp_data['total_sales']
            total_returns = sp_data['total_returns']
            net_sales = total_sales - total_returns
            total_commission = sp_data['total_commission']
            
            ws_summary.cell(row=row_num, column=1).value = sp_data['salesperson'].name
            ws_summary.cell(row=row_num, column=2).value = total_sales
            ws_summary.cell(row=row_num, column=2).number_format = '#,##0.00'
            ws_summary.cell(row=row_num, column=3).value = total_returns
            ws_summary.cell(row=row_num, column=3).number_format = '#,##0.00'
            ws_summary.cell(row=row_num, column=4).value = net_sales
            ws_summary.cell(row=row_num, column=4).number_format = '#,##0.00'
            ws_summary.cell(row=row_num, column=5).value = total_commission
            ws_summary.cell(row=row_num, column=5).number_format = '#,##0.00'
            
            grand_sales += total_sales
            grand_returns += total_returns
            grand_commission += total_commission
            
            row_num += 1
        
        # Grand totals
        ws_summary.cell(row=row_num, column=1).value = 'GRAND TOTAL'
        ws_summary.cell(row=row_num, column=1).font = Font(bold=True)
        ws_summary.cell(row=row_num, column=2).value = grand_sales
        ws_summary.cell(row=row_num, column=2).number_format = '#,##0.00'
        ws_summary.cell(row=row_num, column=2).font = Font(bold=True)
        ws_summary.cell(row=row_num, column=3).value = grand_returns
        ws_summary.cell(row=row_num, column=3).number_format = '#,##0.00'
        ws_summary.cell(row=row_num, column=3).font = Font(bold=True)
        ws_summary.cell(row=row_num, column=4).value = grand_sales - grand_returns
        ws_summary.cell(row=row_num, column=4).number_format = '#,##0.00'
        ws_summary.cell(row=row_num, column=4).font = Font(bold=True)
        ws_summary.cell(row=row_num, column=5).value = grand_commission
        ws_summary.cell(row=row_num, column=5).number_format = '#,##0.00'
        ws_summary.cell(row=row_num, column=5).font = Font(bold=True)
        
        # Auto-width columns
        for col in ws_summary.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws_summary.column_dimensions[column].width = max_length + 2
        
        # Create Detailed Lines sheet
        ws_detail = wb.create_sheet('Detailed Lines')
        
        # Detail headers
        headers_detail = ['Date', 'Salesperson', 'Invoice', 'Product', 'Quantity', 
                         'Subtotal', 'Commission Rate', 'Commission', 'Type']
        for col_num, header in enumerate(headers_detail, 1):
            cell = ws_detail.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Detail data
        row_num = 2
        for sp_id in sorted(data.keys(), key=lambda x: data[x]['salesperson'].name):
            sp_data = data[sp_id]
            for line in sp_data['lines']:
                ws_detail.cell(row=row_num, column=1).value = line['invoice_date']
                ws_detail.cell(row=row_num, column=1).number_format = 'YYYY-MM-DD'
                ws_detail.cell(row=row_num, column=2).value = sp_data['salesperson'].name
                ws_detail.cell(row=row_num, column=3).value = line['invoice_number']
                ws_detail.cell(row=row_num, column=4).value = line['product_name']
                ws_detail.cell(row=row_num, column=5).value = line['quantity']
                ws_detail.cell(row=row_num, column=5).number_format = '#,##0.00'
                ws_detail.cell(row=row_num, column=6).value = line['line_subtotal']
                ws_detail.cell(row=row_num, column=6).number_format = '#,##0.00'
                ws_detail.cell(row=row_num, column=7).value = line['commission_rate']
                ws_detail.cell(row=row_num, column=7).number_format = '0.00"%"'
                ws_detail.cell(row=row_num, column=8).value = line['commission_amount']
                ws_detail.cell(row=row_num, column=8).number_format = '#,##0.00'
                ws_detail.cell(row=row_num, column=9).value = line['move_type']
                
                row_num += 1
        
        # Auto-width columns for detail sheet
        for col in ws_detail.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws_detail.column_dimensions[column].width = min(max_length + 2, 50)
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Create attachment
        filename = f"Commission_Report_{self.date_from}_{self.date_to}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_print_pdf(self):
        """Generate PDF report."""
        self.ensure_one()
        
        data = self._get_commission_data()
        
        if not data:
            raise UserError("No commission data found for the selected filters.")
        
        return self.env.ref('sales_commision_product.action_report_commission_financial').report_action(self, data={'report_data': data})
