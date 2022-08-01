# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import xlsxwriter
import base64
from io import BytesIO
from odoo.exceptions import UserError
import calendar
from datetime import datetime, timedelta


class CarXlsxMain(models.Model):
    _name = 'car.report.xls1.main'

    # from_date = fields.Date('From Date', required=True)
    # to_date = fields.Date('To Date', required=True)
    # car = fields.Many2one("fleet.vehicle", string="Car", domain="[('car_noe', '!=', False)]")
    #
    # def print_report(self):
    #     data = {
    #         'model': self._name,
    #         'ids': self.ids,
    #         'form': {
    #             'start_date': self.from_date, 'expiration_date': self.to_date,
    #         },
    #     }
    #     for report in self:
    #         a = 1
    #         # logo = report.env.user.company_id.logo
    #         # company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
    #         # file_name = _('Preventive Maintainance.xlsx')
    #         file_name = _('Car Attendance.xlsx')
    #         fp = BytesIO()
    #         workbook = xlsxwriter.Workbook(fp)
    #         excel_sheet = workbook.add_worksheet('Car Attendance ')
    #         report_title = 'Car Attendance Report'
    #         header_format = workbook.add_format(
    #             {'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
    #         header_format.set_align('center')
    #         header_format.set_align('vertical center')
    #         header_format.set_text_wrap()
    #         format = workbook.add_format(
    #             {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
    #         title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
    #         title_format.set_align('center')
    #         format.set_align('center')
    #         format.set_text_wrap()
    #         format.set_num_format('#,##0.000')
    #         sequence_format = workbook.add_format(
    #             {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
    #         sequence_format.set_align('center')
    #         sequence_format.set_text_wrap()
    #         total_format = workbook.add_format(
    #             {'bold': True, 'font_color': 'black', 'bg_color': '#808080', 'border': 1, 'font_size': '10'})
    #         col = 0
    #         row = 0
    #         # row += 1
    #         excel_sheet.set_column(col, col, 25)
    #         excel_sheet.write(row, col, '', header_format)
    #         col += 1
    #         excel_sheet.set_column(col, col, 100)
    #         excel_sheet.write(row, col, 'Days', header_format)
    #         row = 1
    #         fleets = self.env['transportation.cars.attendance.line'].search([])
    #         col = 0
    #         row = 4
    #         for fleet in fleets:
    #             excel_sheet.write(row, col, fleet.car_no.id, format)
    #             col += 1
    #             excel_sheet.write(row, col, '', format)
    #             col += 1
    #
    #         workbook.close()
    #         download_file = base64.b64encode(fp.getvalue())
    #         fp.close()
    #         wizardmodel = self.env['xlsx.wizard']
    #         res_id = wizardmodel.create({'name': file_name, 'download_file': download_file})
    #         return {
    #             'name': 'Files to Download',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'xlsx.wizard',
    #             'type': 'ir.actions.act_window',
    #             'target': 'new',
    #             'res_id': res_id.id,
    #         }


class Wizard(models.TransientModel):
    _name = "xlsx.wizard"

    # name = fields.Char('File Name', size=256, readonly=True)
    # download_file = fields.Binary('File to Download', readonly=True)
