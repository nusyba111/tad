# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class CustomTrack(models.Model):
    _name = 'custom.tracking.report'
    _description = 'Print all Custom'

    date_from=fields.Datetime('Date From')
    date_to=fields.Datetime('Date To')

    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            file_name = _('Procurement Report.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Procurement Report')
            report_title = 'Procurement Report For SRCS Purchase '
            report_second_title =  self.date_from.strftime('%Y ')
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#0080ff', 'border': 1})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format.set_align('center')
            format.set_align('center')
            header_format_sequence.set_align('center')
            format.set_text_wrap()
            format.set_num_format('#,##0.000')
            sequence_format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            sequence_format.set_align('center')
            sequence_format.set_text_wrap()
            total_format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#808080', 'border': 1, 'font_size': '10'})

            excel_sheet.merge_range('A1:G1', report_title, title_format)
            excel_sheet.merge_range('A2:G2', report_second_title, title_format)

            col = 0
            row = 3
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Description', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Quantity', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Department', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Donor', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Cost Amount', header_format)
            col += 1

            procs = self.env['purchase.order'].search([('date_approve','>=',report.date_from),('date_approve','<=',report.date_to),('state','in',['purchase','grn','payment','receive_good','done'])])
            col = 0
            row += 1
            for pro in procs:
                description = ''
                total=0.0
                quantity=0.0
                excel_sheet.write(row, col, a, format)
                a = a + 1
                col += 1
                for rec in pro.order_line:
                    total +=(rec.price_unit * rec.qty_received)
                    quantity += rec.qty_received
                    description += str(rec.product_id.name) + ', '
                excel_sheet.write(row, col, description, format)
                col += 1
                excel_sheet.write(row, col, quantity, format)
                col += 1
                if pro.purchase_request_id:
                    excel_sheet.write(row, col, pro.purchase_request_id.department_id.name, format)
                    col += 1
                    excel_sheet.write(row, col, pro.purchase_request_id.donor_id.name, format)
                    col += 1
                else:
                    excel_sheet.write(row, col, pro.user_id.department_id.name, format)
                    col += 1
                    excel_sheet.write(row, col, '-', format)
                    col += 1
                excel_sheet.write(row, col, total, format)
                col += 1
                col = 0
                row += 1

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['custom.tracking.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.tracking.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }

class Custom(models.TransientModel):
    _name = 'custom.tracking.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
