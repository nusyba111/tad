# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class FuelTrack(models.Model):
    _name = 'fuel.tracking.report'
    _description = 'Print all Fleet With Preventive Maintainance'

    from_date=fields.Date('From Date', required=True)
    to_date=fields.Date('To Date' , required=True)
    location=fields.Many2one('stock.warehouse','Warehouse',required=True)
    fuel_type=fields.Many2one('product.product',string='Fuel Type',required=True)

    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            if report.from_date > report.to_date:
                raise UserError(_("You must be enter start date less than end date !"))
            if report.from_date.month != report.to_date.month:
                raise UserError(_("You must be enter start date and end date in the same month !"))
            file_name = _('Fuel Tracking Sheet.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Fuel Tracking Sheet')
            excel_sheet_two = workbook.add_worksheet('Vehicle and Equipment Sheet')
            report_title = 'Fuel Tracking Sheet For SRCS Fleets '
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

            excel_sheet.merge_range('A1:G1', report_title, title_format)
            excel_sheet.merge_range('A2:G2', report_second_title, title_format)

            col = 0
            row = 3
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Date', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Opening Stock', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Fuel Recieved From', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Fuel Qty', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Issued To', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Issued Qty', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Vehicle and Equipment', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Issued', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Current Stock', header_format)
            col += 1
            x=0
            y=0
            day = self.from_date.day
            days=self.from_date.day
            print('tttt',day)
            col = 0
            row += 1
            while day <= self.to_date.day:
                date = report.from_date + relativedelta(days=x)
                excel_sheet.write(row, col, day, format)
                day = day + 1
                col += 1
                quant = self.fuel_type.with_context({'warehouse':self.location.name, 'to_date': date}).qty_available
                excel_sheet.write(row, col,quant, format)
                x = x + 1
                col += 1
                total = 0.00
                total_sales=0.00
                total_sales_hq=0.00
                vendor=''
                customer=''
                location_id = self.location.in_type_id.default_location_dest_id
                self._cr.execute('SELECT move.id, ' \
                                 'move.state, '
                                 'min(move.state),' \
                                 'min(move.date) ' \
                                 'FROM stock_move move ' \
                                 'where move.product_id = ' + str(self.fuel_type.id) + ' AND move.location_id =' + str(
                    location_id.id) + ' GROUP BY move.id ' \
                                      'ORDER BY move.id ASC')
                move_ids = self._cr.fetchall()
                move_ids = move_ids and [x[0] for x in move_ids] or []
                for res in self.env['stock.move'].browse(move_ids):
                    # print('lllllllllllllllllllllllllllllll',res)
                    if res.state == 'done' and res.date.strftime(
                            "%Y-%m") == date and res.location_dest_id.usage == 'internal':
                        total += res.product_uom_qty
                        vendor = res.picking_id.partner_id.name

                excel_sheet.write(row, col, vendor, format)
                col += 1
                excel_sheet.write(row, col,total, format)
                col += 1
                fleets = self.env['fuel.service'].search([('date', '=', date)])
                print('fleeet',fleets,date)
                for flet in fleets:
                    if flet.fuel_id.fuel_type.id==self.fuel_type.id:
                        if flet.request_type != 'hq':
                            customer += str(flet.partner.name) + ', '
                            for fuel in flet.fuel_id:
                                total_sales += fuel.qty
                        if flet.request_type=="hq":
                            for fuel in flet.fuel_id:
                                total_sales_hq += fuel.qty
                excel_sheet.write(row, col, customer, format)
                col += 1
                excel_sheet.write(row, col, total_sales, format)
                col += 1
                excel_sheet.write(row, col, total_sales_hq, format)
                col += 1
                total_issue=total_sales_hq+total_sales
                excel_sheet.write(row, col, total_issue, format)
                col += 1
                current_stock=quant-total_issue
                excel_sheet.write(row, col, current_stock, format)
                col += 1
                col = 0
                row += 1

            excel_sheet_two.merge_range('A1:G1', report_title, title_format)
            excel_sheet_two.merge_range('A2:G2', report_second_title, title_format)
            col = 0
            row = 3
            excel_sheet_two.set_column(col, col, 25)
            excel_sheet_two.write(row, col, 'Date', header_format)
            col += 1
            excel_sheet_two.set_column(col, col, 25)
            excel_sheet_two.write(row, col,'Fleet', header_format)
            col += 1
            excel_sheet_two.set_column(col, col, 25)
            excel_sheet_two.write(row, col, 'Quantity', header_format)
            col = 0
            row +=1
            while days <= self.to_date.day:
                date = report.from_date + relativedelta(days=y)
                fleets = self.env['fuel.type'].search([('service_id.date', '=', date),('fuel_type','=',self.fuel_type.id)])
                print('dddddddd',date,fleets)
                for fleet in fleets:
                    excel_sheet_two.set_column(col, col, 25)
                    excel_sheet_two.write(row, col,days, format)
                    col += 1
                    excel_sheet_two.set_column(col, col, 25)
                    excel_sheet_two.write(row, col, fleet.service_id.vehicle.license_plate, format)
                    col += 1
                    excel_sheet_two.set_column(col, col, 25)
                    excel_sheet_two.write(row, col, fleet.qty, format)
                    col = 0
                    row +=1
                days = days + 1
                y=y+1
                print('days',days)

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['fuel.tracking.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fuel.tracking.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }




class Fuel_Tracking(models.TransientModel):
    _name = 'fuel.tracking.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
