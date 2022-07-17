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
    _name = 'maintainance.report'
    _description = 'Print all Fleet Maintainance'

    from_date=fields.Date('From Date', required=True)
    to_date=fields.Date('To Date' , required=True)
    vat=fields.Float('VAT %', required=True)


    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            file_name = _('FleetWave Maintainance Reporting.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Maintainance Reporting')
            report_title = 'FleetWave Maintainance Reporting'
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
            excel_sheet.write(row, col, 'Workshop', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Date In', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Date Out', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Invoice No.', header_format)
            col += 1
            excel_sheet.set_column(col, col, 40)
            excel_sheet.write(row, col, 'Mileage at Start of Service', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Cost Of Parts', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Cost of Lubricants', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Cost Per Hour', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Miscellenous', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'No of Job hours Charged', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total cost on labour', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Local Cost', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Country Currency', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Job Reason', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Job Specification)', header_format)
            col += 1


            fleets = self.env['fleet.vehicle'].search([])
            col = 0
            row += 1
            for fleet in fleets:
                total_price = 0.0
                total_lube = 0.0
                service=''
                repair = self.env['repair'].search([('date','>=',self.from_date),
                                                    ('date','<=',self.to_date),('fleet','=',fleet.id)])

                for rec in repair:
                    excel_sheet.write(row, col, a, format)
                    a = a + 1
                    col += 1
                    excel_sheet.write(row, col, fleet.federation_vehicle_code, format)
                    col += 1
                    excel_sheet.write(row, col, rec.workshop_id.name, format)
                    col += 1
                    excel_sheet.write(row, col, rec.start_maintainance.strftime('%Y-%m-%d'), format)
                    col += 1
                    excel_sheet.write(row, col, rec.end_maintainance.strftime('%Y-%m-%d'), format)
                    col += 1
                    excel_sheet.write(row, col, rec.invoice_no, format)
                    col += 1
                    excel_sheet.write(row, col, rec.odometer, format)
                    col += 1
                    if rec.spare_id:
                        for record in rec.spare_id:
                            if record.spare.categ_id.spare ==True:
                                total_price = + record.total
                            if record.spare.categ_id.lubricant == True:
                                total_lube = + record.total
                    excel_sheet.write(row, col, total_price, format)
                    col += 1
                    excel_sheet.write(row, col, total_lube, format)
                    col += 1
                    if rec.service_id:
                        services=''
                        for record in rec.service_id:
                            total_hour_price = + record.hour_price
                            total_hour = + record.hour
                            total_labor = + record.service_price
                            services += str(record.service.name) + ', '

                    excel_sheet.write(row, col,total_hour_price, format)
                    col += 1
                    excel_sheet.write(row, col,'', format)
                    col += 1
                    excel_sheet.write(row, col, total_hour, format)
                    col += 1
                    excel_sheet.write(row, col,total_labor, format)
                    col += 1
                    local_cost=total_labor+total_price+total_lube
                    excel_sheet.write(row, col, local_cost, format)
                    col += 1
                    excel_sheet.write(row, col, fleet.company_id.currency_id.name, format)
                    col += 1
                    excel_sheet.write(row, col, rec.job_reason.name, format)
                    col += 1
                    excel_sheet.write(row, col, services, format)
                    col += 1
            row +=1
            col = 6
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'VAT', header_format)
            col += 7
            repair = self.env['repair'].search([('date', '>=', self.from_date),
                                                    ('date', '<=', self.to_date)])
            total = 0.0
            tot_lube=0.00

            for rec in repair:
                if rec.service_id:
                    for record in rec.service_id:
                        tot_hour_price = + record.hour_price
                        tot_hour =+ record.hour
                        tot_labor = + record.service_price
                if rec.spare_id:
                    for record in rec.spare_id:
                        if record.spare.categ_id.spare == True:
                            tot_spare = + record.total
                        if record.spare.categ_id.lubricant == True:
                            tot_lube = + record.total
                if rec.invoice_no == 0:
                    if rec.service_id:
                        for record in rec.service_id:
                            total = + record.service_price
                    if rec.spare_id:
                        for record in rec.spare_id:
                            total_spare = + record.total
            print('tttt',total,total_spare)
            vat=(total+total_spare)*(self.vat/100)
            tot_local = tot_labor + tot_spare + tot_lube + vat
            excel_sheet.write(row, col, vat, format)
            row += 1
            col = 6
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total', header_format)
            col += 1
            excel_sheet.write(row, col, tot_spare, format)
            col +=1
            excel_sheet.write(row, col, tot_lube, format)
            col += 1
            excel_sheet.write(row, col, tot_hour_price, format)
            col += 1
            excel_sheet.write(row, col, '', format)
            col += 1
            excel_sheet.write(row, col,tot_hour, format)
            col += 1
            excel_sheet.write(row, col,tot_labor, format)
            col += 1
            excel_sheet.write(row, col,tot_local, format)

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['maintainance.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'maintainance.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }




class Fuel_Mileage_Report_Excel(models.TransientModel):
    _name = 'maintainance.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
