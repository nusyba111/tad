# -*- coding: utf-8 -*-
###########
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *
from datetime import datetime



class Vehiclevehiclematriculation(models.Model):
    _name = 'vehicle.matriculation.report'
    _description = 'matriculation'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    def last_day_of_month(any_day):
        # this will never fail
        # get close to the end of the month for any day, and add 4 days 'over'
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
        return next_month - datetime.timedelta(days=next_month.day)
    def print_report(self):
        print("**********************")
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
            file_name = _('Vehicle Matriculation.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Vehicle Matriculation')
            report_title = 'Vehicle Matriculation'
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
            col = 0
            row = 0
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Year السنة', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'KM Start بداية الكيلومترات', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'KM Finish نهاية الكيلومترات', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Distance مجموع المسافة', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Fuel جملة الوقود', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Total Oil جملة الزيت', header_format)
            col += 1

            col = 0
            row += 1

            # a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            num_months = (self.to_date.year - self.from_date.year) * 12 + (
                    self.to_date.month - self.from_date.month)
            print('num of months', num_months)
            i = 0
            # col = 0
            while i <= num_months :
                date = self.from_date + relativedelta(months=i)
                month_no = str(date.strftime("%m"))
                # col += 1
                i += 1
                print('month no', month_no)
                month_name = calendar.month_name[int(month_no)]
                # print('month name', month_name)
            #
                excel_sheet.write(row, col,  month_name)
                row +=1

            col = 0
            row = 1
            i = 0
            while i <= num_months :
                if i == 0:
                    start_date = self.from_date + relativedelta(months=i)
                else:
                    start_date = self.from_date + relativedelta(months=i)
                    start_date = start_date.replace(day=1)
                if i > num_months:
                    end_date = self.to_date + relativedelta(months=i)
                else:
                    lats_day = calendar.monthrange(start_date.year, start_date.month)[1]
                    # print("&&&&&&&&&&&&&&&&&&&&&&&&*",lats_day)
                    # end_date = self.to_date + relativedelta(months=i)
                    end_date = start_date.replace(day=lats_day)

                # month_no = str(date.strftime("%m"))
                col += 1
                i += 1
                odom = self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',self.vehicle_id.id),('date','>=',start_date) ,('date','<=',end_date)], order='value asc', limit=1)
                excel_sheet.write(row, col, odom.value, format)
                print("**********************************&&&&&&&&&&&&", end_date)
                col += 1
                odomter = self.env['fleet.vehicle.odometer'].search(
                    [('vehicle_id', '=', self.vehicle_id.id), ('date', '>=',start_date), ('date', '<=', end_date)],
                    order='value desc', limit=1)
                excel_sheet.write(row, col, odomter.value, format)
                col += 1
                odom_tolal = 0.0
                odom_tolal = odomter.value - odom.value
                excel_sheet.write(row, col, odom_tolal, format)
                col += 1
                total_fule = self.env['fuel.service'].search(
                    [('vehicle', '=', self.vehicle_id.id), ('date', '>=', start_date), ('date', '<=', end_date)])
                excel_sheet.write(row, col, total_fule.total_amount, format)
                col += 1
                total_lubricant_lubricant = self.env['repair'].search(
                    [('fleet', '=', self.vehicle_id.id), ('date', '>=', start_date), ('date', '<=', end_date)])
                # print("total_lubricant_lubricant",total_lubricant_lubricant)
                excel_sheet.write(row, col, total_lubricant_lubricant.lubricant_amount, format)
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


class Fleetmatriculation_Report_Excel(models.TransientModel):
    _name = 'fleet.vehicle.matriculation.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    download_file = fields.Binary('File to Download', readonly=True)
