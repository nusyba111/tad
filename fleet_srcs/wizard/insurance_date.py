# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class Insurance(models.Model):
    _name = 'insurance.date.report'
    _description = 'Print all Fleet With Preventive Maintainance'

    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            file_name = _('Insurance Expiration Date.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Insurance Expiration Date')
            report_title = 'Insurance Expiration Date For SRCS Fleets '
            report_second_title = self.from_date.strftime('%Y-%m-%d')
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
            excel_sheet.write(row, col, 'Sr.No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Car Type', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Model', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Chassis No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Engine No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'License Plate', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Insurance End Date', header_format)
            col += 1

            fleets = self.env['fleet.vehicle'].search([])
            col = 0
            row += 1
            for fleet in fleets:
                excel_sheet.write(row, col, a, format)
                a = a + 1
                col += 1
                excel_sheet.write(row, col, fleet.model_id.name, format)
                col += 1
                excel_sheet.write(row, col, fleet.model_id.model_year, format)
                col += 1
                excel_sheet.write(row, col, fleet.vin_sn, format)
                col += 1
                excel_sheet.write(row, col, fleet.engine_no, format)
                col += 1
                excel_sheet.write(row, col, fleet.license_plate, format)
                col += 1
                excel_sheet.write(row, col, fleet.insurance_end, format)
                col += 1

                col = 0
                row += 1

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['insurance.date.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'insurance.date.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }




class Insurance_Date_Report_Excel(models.TransientModel):
    _name = 'insurance.date.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
