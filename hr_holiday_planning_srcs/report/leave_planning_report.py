# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import xlsxwriter
import base64
import datetime

from io import StringIO
from datetime import *
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import os

from odoo.exceptions import Warning as UserError
from dateutil import relativedelta
from io import BytesIO

class HolidayPlanningReport(models.Model):
    _name = "leave.planning.report"

    date = fields.Date(string="Date")


    
    def print_report(self):
        for report in self:
            logo = report.env.user.company_id.logo
            
            
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            address1 = company_id.street
            address2 = company_id.street2
            country = company_id.country_id.name
            phone = company_id.phone
            website = company_id.website
            
            file_name = None
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Secretary General Office')
            image_data = BytesIO(base64.b64decode(logo))  
            # excel_sheet.insert_image('A1', 'logo.png', {'image_data': image_data})
            
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#a4f3dd', 'border': 1})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white'})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 0, 'font_size': '10'})
            format1 = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': '#f4e350', 'border': 1})
            title_format.set_align('center')
            format.set_align('center')
            format1.set_align('center')
            header_format_sequence.set_align('center')
            format.set_text_wrap()
            format1.set_text_wrap()
            format.set_num_format('#,##0.000')
            format1.set_num_format('#,##0.000')
            date_format = workbook.add_format({'num_format': 'dd/mm/yy','border': 0, 'font_size': '10'})
            date_format.set_align('center')
            date_time_format = workbook.add_format({'num_format': 'dd/mm/yy :H:M:S','border': 0, 'font_size': '10'})
            date_time_format.set_align('center')

            format_details = workbook.add_format()
            sequence_format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            sequence_format.set_align('center')
            sequence_format.set_text_wrap()
            total_format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#e18ce0', 'border': 1, 'font_size': '10'})
            total_format2 = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#aacbf1', 'border': 1, 'font_size': '10'}) 
            total_format.set_align('center')
            total_format.set_text_wrap()
            total_format2.set_align('center')
            total_format2.set_text_wrap()
            format_details.set_num_format('#,##0.00')
            sequence_id = 0
            col = 0
            row = 3
            first_row = 9
            # total1 = 0.0
            # total_owner = 0.0
            # count = 0.0
            # tot = 0.0
            # own = 0.0
            # con = 0

            report_title = 'Secretary General Office'
            file_name = _('Secretary General Office.xlsx')
            
            excel_sheet.merge_range(0, 1, 2, 8, report_title, title_format)
            excel_sheet.write(row, col+1, 'الإسم', header_format)
            excel_sheet.write(row, col+2, 'المستحق', header_format)
            excel_sheet.write(row, col+3, 'الررصيد الحالي', header_format)
            planns = self.env['hr.leave.planning'].search([])
            


            # excel_sheet.write(row, col+4, 'No Of Transaction', header_format)
            # excel_sheet.write(row, col+5, 'Total Of Amount', header_format)
            # excel_sheet.write(row, col+6, 'Total Fees', header_format)
            # excel_sheet.write(row, col+7, 'Agent Commision 20%', header_format)
            # excel_sheet.write(row, col+8, 'E-connect Net Commision', header_format)
      
            # excel_sheet.set_column(col+1, col+4, 20)
            # excel_sheet.set_column(col+2, col+4, 20)
            # excel_sheet.set_column(col+3, col+4, 20)
            # excel_sheet.set_column(col+4, col+4, 20)
            # excel_sheet.set_column(col+5, col+5, 20)
            # excel_sheet.set_column(col+7, col+7, 20)
            # excel_sheet.set_column(col+8, col+8, 20)
            

            # objects = self.env['agent.fees'].search([])
            # for name in objects:
            #       row+=1
            #       excel_sheet.write(row,col+1,name.agent_name,format1)
            #       excel_sheet.write(row,col+2,name.location,format1)
            #       excel_sheet.write(row,col+3,name.terminal_id,format1)
            #       excel_sheet.write(row,col+4,name.number_of_transaction,format1)
            #       excel_sheet.write(row,col+5,name.total_of_amount,format1)
            #       excel_sheet.write(row,col+6,name.total_fees,format1)
            #       excel_sheet.write(row,col+7,name.agent_commision,format1)
            #       excel_sheet.write(row,col+8,name.connect_net_commision,format1)

                        

                                                    

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['leave.planning.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'leave.planning.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


class LeavePlanningReportExcel(models.TransientModel):
    _name = 'leave.planning.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)