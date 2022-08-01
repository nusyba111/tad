# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *


class LedgerReport(models.Model):
    _name = 'ledger.report'
    _description = 'ledger'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)

    # no = fields.Integer()

    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            file_name = _('Ledger report.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Ledger report')
            report_title = 'الشؤون الإدارية'
            report_title1 = 'قسم الخدمات'
            report_title3 = 'حضور وانصراف العربات'
            report_title2 = 'للفترة من ' + str(report.from_date) + ' الى ' + str(report.to_date)
            report_title3 = 'To'
            report_title4 = 'قسم الخدمات'
            report_title1 = 'حضور وانصراف العربات'
            report_title5 = 'الأيام'
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#ccccff', 'border': 1})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
            title_format = workbook.add_format(
                {'bold': True, 'font_color': 'red', 'bg_color': 'Light Blue2', 'border': 1})
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
                {'bold': True, 'font_color': 'black', 'bg_color': '#ccccff', 'border': 1, 'font_size': '10'})
            report_title4 = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#99CCFF', 'border': 1, 'font_size': '12'})
            report_title4.set_align('center')

            col = 0
            row = 1
            excel_sheet.merge_range(row, col, row + 1, col + 14, report_title, report_title4)
            col = 0
            row = 3
            excel_sheet.merge_range(row, col, row + 1, col + 14, report_title1, report_title4)
            col = 0
            row = 5
            excel_sheet.merge_range(row, col, row + 1, col + 14, report_title2, report_title4)

            col = 0
            row = 7
            # excel_sheet.merge_range(row, col, row + 1, col + 14, report_title5, report_title4)
            col = 0
            row = 9
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col + 3, 'Car Number', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.merge_range(row, col, row + 1, col + 14, report_title5, report_title4)
            # excel_sheet.write(row, col, 'Driver Name', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 25)
            # excel_sheet.write(row, col, 'Location', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Goal', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Site', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Situation', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Budget Code/Out-put', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Account Code ', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Cheque Number', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Payee', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Particulars/Descriptions', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'DR Amount', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'CR Amount', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Balance', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Remarks if any', header_format)
            # col += 1

            budget = self.env['transportation.cars.attendance'].search([])

            col = 0
            row += 1
            i = 1
            for rec in budget:
                for x in rec.cars_transport_list_ids:
                    # excel_sheet.write(row, col, str(i), format)
                    # i = i + 1
                    # col += 1
                    # excel_sheet.write(row, col, str(rec.date), format)
                    # col += 1
                    excel_sheet.write(row, col, x.car_no.car_noe, format)
                    col += 1
                    # excel_sheet.write(row, col, str(x.analytic_account_id.goal), format)
                    # col += 1
                    # excel_sheet.write(row, col, str(x.analytic_account_id.site), format)
                    # col += 1
                    # excel_sheet.write(row, col, str(x.analytic_account_id.situation), format)
                    # col += 1
                    # # budget
                    # excel_sheet.write(row, col, x.activity_id.name, format)
                    # col += 1
                    # account code
                    # excel_sheet.write(row, col, x.account_id.code, format)
                    # col += 1
                    # # check no
                    # excel_sheet.write(row, col, x.activity_id.name, format)
                    # col += 1
                    # excel_sheet.write(row, col, x.partner_id.name, format)
                    # col += 1
                    # excel_sheet.write(row, col, rec.line_ids.name, format)
                    # col += 1
                    # excel_sheet.write(row, col, x.name, format)
                    # col += 1
                    # excel_sheet.write(row, col, x.debit, format)
                    # col += 1
                    # excel_sheet.write(row, col, x.credit, format)
                    # col += 1
                    # balance
                    # excel_sheet.write(row, col, x.activity_id.name, format)
                    # col += 1
                    # # remarks
                    # excel_sheet.write(row, col, x.activity_id.name, format)
                    col += 1
                    col = 0
                    row += 1

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['ledger.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ledger.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


class ledger_Report_Excel(models.TransientModel):
    _name = 'ledger.report.excel'
    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
