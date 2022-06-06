from odoo import api, fields, models, _
# from datetime import date
from datetime import datetime, timedelta, date
# import xlsxwriter
# import base64

class SRCSProjectReport(models.TransientModel):
    _name = "project.report.wizard"

    branch_id = fields.Many2one('res.branch', string='Branch')
    date_from = fields.Date('Date From')
    date_to= fields.Date('Date To')
    project_id = fields.Many2one('account.analytic.account',string='Project', required=True, domain="[('type','=','project')]")

    def print_excel_project(self):
        move_line = self.env['account.move.line'].search_read([('analytic_account_id','=',self.project_id.id),
                                                        ('move_id.date','>=',self.date_from),('move_id.date','<=',self.date_to),('branch_id_line','=',self.branch_id.id)])
        budget = self.env['crossovered.budget'].search_read([('project_id','=',self.project_id.id),('date_from','>=',self.date_from),('date_to','<=',self.date_to)])
        data = {
            'move_line': move_line,
            'budget': budget,
        }
        # print('______________nfhhhghfh',data)
        print('____***************',budget)
        return self.env.ref('srcs_branch.action_report_project').report_action(self, data=data)
  

class ProjectXlsx(models.AbstractModel):
    _name = 'report.srcs_branch.project_report_excel_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        print('kdfjffoinadfpffffffffffffff',data,'partners',partners)
        sheet = workbook.add_worksheet('Expenditure Report')
        print('________________________',partners)
        bold = workbook.add_format({'bold': True})
        branch_format = workbook.add_format({'font_size': '13','bold': True ,'bg_color':'yellow'})
        title_format = workbook.add_format({'font_size': '18','bold': True })
        border = workbook.add_format({ 'border': 1})
        bold_border = workbook.add_format({ 'border': 1,'bold': True ,'font_size': '11'})
        format = workbook.add_format({'bg_color':'gray'})
        format_format = workbook.add_format({'bg_color':'yellow','border': 1,'font_size': '15','bold': True })
        bank_format = workbook.add_format({'bg_color':'yellow','border': 1,'bold': True})
        details_format = workbook.add_format({'bg_color':'yellow','border': 1})
        signature_format = workbook.add_format({'font_size': '13','bold': True })
        title_format.set_align('center')
        bold_border.set_align('center')
        format.set_align('center')
        format_format.set_align('center')
        bank_format.set_align('center')
        sheet.merge_range(0,0,1,1,'Sudanese Red Crescent Society', title_format)
        branch = 'Branch Name:' + ' ' + str(partners.branch_id.name) 
        sheet.merge_range(2,0,3,1,branch,branch_format)
        name = 'Project Name:' +' ' + ' '+ str(partners.project_id.name)
        sheet.merge_range(4,0,5,1,name,bold)
        #######################
        # project_period = 'Project Duration:' + ' ' + 
        sheet.merge_range(6,0,7,1,'Project Duration:', bold)
        # date_from = fields.Date.to_string(
        #                         datetime.strptime(str(partners.date_from), '%d-%m-%y'))
        # date = str(partners.date_from)
        # date_start = datetime.strptime('%d-%m-%y',str(partners.date_from))
        period = 'Report Period:' + ' '+ ' ' + 'From' + ' '+ str(partners.date_from) + ' ' + 'To'+ ' ' +str(partners.date_to)
        sheet.merge_range(8,0,9,1,period, bold)
        sheet.set_column('A:K',25)
        sheet.write(11,0,'Entry Date',bold_border)
        sheet.write(12,0,' ',format)
        sheet.write(11,1,'Entry',bold_border)
        sheet.write(12,1,' ',format)
        sheet.write(11,2,'Check',bold_border)
        sheet.write(12,2,'Payee',format)
        sheet.write(11,3,'Description',bold_border)
        sheet.write(12,3,' ',format)
        sheet.write(11,4,'Account',bold_border)
        sheet.write(12,4,'code',format)
        sheet.write(11,5,'Project ',bold_border)
        sheet.write(12,5,'code',format)
        sheet.write(11,6,'Activity ',bold_border)
        sheet.write(12,6,'code',format)
        sheet.write(11,7,'Donor ',bold_border)
        sheet.write(12,7,'code',format)
        sheet.write(11,8,'Location ',bold_border)
        sheet.write(12,8,'code',format)
        sheet.write(11,9,'Credit ',bank_format)
        sheet.write(12,9,'Income',bank_format)
        sheet.merge_range(9,9,10,11,'SDG Bank Account No',format_format)
        # sheet.write(10,)
        sheet.write(11,10,'Debit',bank_format)
        sheet.write(12,10,'Expenditure',bank_format)
        sheet.write(11,11,'Balance',bank_format)
        sheet.write(12,11,' ',bank_format)
        row = 13
        col = 0
        for line in data['move_line']:
            print('+++++++++++++++++++++++++++++++++++++++++++++++',line)
            sheet.write(row,col,line['date'],border)
            sheet.write(row,col+1,line['move_id'][1],border)
            sheet.write(row,col+3,line['name'],border)
            sheet.write(row,col+4,line['account_id'][1],border)
            sheet.write(row,col+5,line['analytic_account_id'][1],border)
            sheet.write(row,col+6,line['activity_id'][1],border)
            sheet.write(row,col+7,line['partner_id'][1],border)
            sheet.write(row,col+8,line['location_id'][1],border)
            sheet.write(row,col+9,line['credit'],details_format)
            sheet.write(row,col+10,line['debit'],details_format)
            sheet.write(row,col+11,line['balance'],details_format)
            row += 1 

        sheet.write(row+3,col+3,'Project Coordinator',signature_format)
        sheet.write(row+5,col+3,'Signature',signature_format)
        sheet.write(row+7,col+3,'Date',signature_format)
        sheet.write(row+3,col+5,'Finance Director',signature_format)
        sheet.write(row+5,col+5,'Signature',signature_format)
        sheet.write(row+7,col+5,'Date',signature_format)
        sheet.write(row+3,col+7,'Project Accountant',signature_format)
        sheet.write(row+5,col+7,'Signature',signature_format)
        sheet.write(row+7,col+7,'Date',signature_format)

            