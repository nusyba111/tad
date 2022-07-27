# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class ProcurmentTrack(models.Model):
    _name = 'procurement.tracking.report'
    _description = 'Print all Procurement'

    from_date=fields.Date('From Date', required=True)
    to_date=fields.Date('To Date' , required=True)


    def print_report(self):
        for report in self:
            a = 1
            logo = report.env.user.company_id.logo
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            if report.from_date > report.to_date:
                raise UserError(_("You must be enter start date less than end date !"))
            if report.from_date.month != report.to_date.month:
                raise UserError(_("You must be enter start date and end date in the same month !"))
            file_name = _('Procurement Tracking Sheet.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Procurement Tracking Sheet')
            report_title = 'Procurement Tracking Sheet For SRCS Purchase '
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
            excel_sheet.write(row, col, 'No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Requisition No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Goods or Service', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Description', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Department', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Donor', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Urgency', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Procurement Employee', header_format)
            col += 1
            excel_sheet.set_column(col, col, 30)
            excel_sheet.write(row, col, 'Purchase Order/Service Order/Contract Value', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Currency', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Requisition Recieved Date', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Vendor/Service Provider', header_format)
            col += 1
            excel_sheet.set_column(col, col, 30)
            excel_sheet.write(row, col, 'Purchase Order/Service Order/Contract No', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Current Status', header_format)
            col += 1

            procs = self.env['purchase.request'].search([('request_date','>=',report.from_date),('request_date','<=',report.to_date)])
            col = 0
            row += 1
            for pro in procs:
                description = ''
                total=0.0
                excel_sheet.write(row, col, a, format)
                a = a + 1
                col += 1
                excel_sheet.write(row, col, pro.sequence, format)
                col += 1
                if pro.service==True:
                    type='Service'
                else:
                    type='Products'
                excel_sheet.write(row, col, type, format)
                col += 1
                for rec in pro.purchase_request_line_ids:
                    total +=rec.price_subtotal
                    description += str(rec.product_id.name) + ', '
                excel_sheet.write(row, col, description, format)
                col += 1
                excel_sheet.write(row, col, pro.department_id.name, format)
                col += 1
                excel_sheet.write(row, col, pro.donor_id.name, format)
                col += 1
                excel_sheet.write(row, col, '-', format)
                col += 1
                excel_sheet.write(row, col, pro.requester_id.name, format)
                col += 1
                if pro.state in['secratry_general','tender_procedure','committee_minute','cba','purchase','grn','payment','receive_goods','done']:
                    excel_sheet.write(row, col, total, format)
                    col += 1
                else:
                    excel_sheet.write(row, col, '-', format)
                    col += 1
                excel_sheet.write(row, col,pro.currency_id.name, format)
                col += 1
                excel_sheet.write(row, col, "-", format)
                col += 1
                if pro.purchase_order_id:
                    excel_sheet.write(row, col, pro.purchase_order_id.vendor_id.name, format)
                    col += 1
                    excel_sheet.write(row, col, pro.purchase_order_id.name, format)
                    col += 1
                else:
                    excel_sheet.write(row, col, "-", format)
                    col += 1
                    excel_sheet.write(row, col, "-", format)
                    col += 1
                excel_sheet.write(row, col,pro.state, format)
                col += 1
                col = 0
                row += 1

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['procurement.tracking.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'procurement.tracking.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }




class Fuel_Tracking(models.TransientModel):
    _name = 'procurement.tracking.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
