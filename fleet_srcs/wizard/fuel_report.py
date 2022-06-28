# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class FuelMileage(models.Model):
    _name = 'fuel.mileage.report'
    _description = 'Print all Fleet Fuel and Mileage'

    from_date=fields.Date('From Date', required=True)
    to_date=fields.Date('To Date' , required=True)


    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            file_name = _('FleetWave Fuel And Mileage Reporting.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Fuel Mileage Report')
            report_title = 'FleetWave Fuel And Mileage Reporting'
            report_second_title =  self.from_date.strftime('%Y-%m-%d')
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

            excel_sheet.merge_range('A1:G1',  report_title, title_format)
            excel_sheet.merge_range('A2:G2', report_second_title, title_format)

            col = 0
            row = 3
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Sr.No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Federation Vehicle Code', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Plate Number', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Location', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Period Start', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Period End', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'VRP User?', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Country', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Fuel Type', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Start Odometer', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'End Odometer', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total KM', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Fuel Purchased(Litres)', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Cost Per Litre(Local Currency)', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Cost of Litre(Local Currency)', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Next Service at Km)', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Next Service Due Km)', header_format)
            col += 1

            fleets = self.env['fleet.vehicle'].search([])
            col = 0
            row += 1
            for fleet in fleets:
                excel_sheet.write(row, col, a, format)
                a = a + 1
                col += 1
                excel_sheet.write(row, col, fleet.federation_vehicle_code, format)
                col += 1
                excel_sheet.write(row, col, fleet.license_plate, format)
                col += 1
                excel_sheet.write(row, col, fleet.base_location.name, format)
                col += 1
                excel_sheet.write(row, col, self.from_date.strftime('%Y-%m-%d'), format)
                col += 1
                excel_sheet.write(row, col, self.to_date.strftime('%Y-%m-%d'), format)
                col += 1
                excel_sheet.write(row, col, fleet.vrp_user.name, format)
                col += 1
                excel_sheet.write(row, col, fleet.company_id.country_id.name, format)
                col += 1
                excel_sheet.write(row, col, fleet.fuel_type, format)
                col += 1
                odo=self.env['fleet.vehicle.odometer'].search([('date','>=',self.from_date),('date','<=',self.to_date),
                                                               ('vehicle_id','=',fleet.id)], order='date ASC',limit=1)
                excel_sheet.write(row, col, odo.value, format)
                col += 1
                odom=self.env['fleet.vehicle.odometer'].search([('date','>=',self.from_date),('date','<=',self.to_date),
                                                               ('vehicle_id','=',fleet.id)], order='date DESC',limit=1)
                excel_sheet.write(row, col, odom.value, format)
                col += 1
                total_km=odom.value-odo.value
                excel_sheet.write(row, col, total_km, format)
                col += 1
                fuels = self.env['fuel.type'].search(
                    [('service_id.date', '>=', self.from_date), ('service_id.date', '<=', self.to_date),
                     ('service_id.vehicle', '=', fleet.id)])
                for fuel in fuels:
                    total_qty =+ fuel.qty
                    unit_price =+ fuel.price
                    total_price =+ fuel.total
                excel_sheet.write(row, col, total_qty, format)
                col += 1
                excel_sheet.write(row, col, unit_price, format)
                col += 1
                excel_sheet.write(row, col, total_price, format)
                col += 1
                service = self.env['fleet.service'].search(
                    [('minimum_odometer', '>', fleet.odometer),('vehicle_id', '=', fleet.id)],order='minimum_odometer ASC',limit=1)
                excel_sheet.write(row, col, service.minimum_odometer, format)
                col += 1
                excel_sheet.write(row, col, service.maximum_odometer, format)
                col += 1
                col = 0
                row += 1

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['fuel.mileage.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fuel.mileage.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }




class Fuel_Mileage_Report_Excel(models.TransientModel):
    _name = 'fuel.mileage.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
