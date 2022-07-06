# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class Vehiclevehicle(models.Model):
    _name = 'vehicle.vehicle.report'
    _description = 'vehicle'

    from_date=fields.Date('From Date', required=True)
    to_date=fields.Date('To Date' , required=True)


    def print_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date': self.from_date, 'expiration_date': self.to_date,
            },
        }
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            # file_name = _('Preventive Maintainance.xlsx')
            file_name = _('Fleet Wave.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Fleet Wave')
            report_title = 'Fleets Vehicle'
            report_second_title = self.from_date.strftime('%Y-%m-%d')
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#0080ff', 'border': 1})
            # header_format_sequence = workbook.add_format(
            #     {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format.set_align('center')
            format.set_align('center')
            # header_format_sequence.set_align('center')
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
            excel_sheet.write(row, col, 'Federation Vehicle Code', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Chassis Number', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Engine Type/Model', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Registration Start', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Registration End', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Local Insurance Policy Number', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Insurance Start Date', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Insurance End Date', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Cost Third Party Local(Country Currency Sudan Pound SDG)', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Registration Plate Type', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Car Model', header_format)
            col += 1

            fleets = self.env['fleet.vehicle'].search([])
            col = 0
            row += 1
            for fleet in fleets:

                # serv=self.env['fleet.service'].search([('vehicle_id','=',fleet.id)])
                # serv=self.env['fleet.service'].search([('vehicle_id','=',fleet.id),('minimum_odometer','<=',fleet.odometer),('maximum_odometer','>=',fleet.odometer)])
                excel_sheet.write(row, col, fleet.federation_vehicle_code, format)
                # excel_sheet.write(row, col, a, format)
                # a = a + 1
                col += 1
                excel_sheet.write(row, col, fleet.vin_sn, format)
                col += 1
                excel_sheet.write(row, col, fleet.engine_type, format)
                col += 1
                excel_sheet.write(row, col, fleet.registration_start, format)
                col += 1
                excel_sheet.write(row, col, fleet.registration_end, format)
                col += 1
                excel_sheet.write(row, col, fleet.local_insurance_policy_number, format)
                col += 1
                excel_sheet.write(row, col, fleet.insurance_start, format)
                col += 1
                excel_sheet.write(row, col, fleet.insurance_end, format)
                col += 1
                excel_sheet.write(row, col, fleet.cost_third_party_local, format)
                col += 1
                excel_sheet.write(row, col, fleet.registration_plate_type, format)
                col += 1
                excel_sheet.write(row, col, fleet.model_id.name, format)
                col += 1
                col = 0
                row += 1

            workbook.close()
            download_file = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['fleet.fleet.vehicle.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'download_file': download_file})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fleet.fleet.vehicle.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }

class FleetMaintainance_Report_Excel(models.TransientModel):
    _name = 'fleet.fleet.vehicle.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    download_file = fields.Binary('File to Download', readonly=True)
