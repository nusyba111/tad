# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from datetime import date, datetime, time
import calendar
from datetime import datetime, timedelta
from dateutil import relativedelta

from dateutil.relativedelta import relativedelta


class CompareSanitationWiz(models.TransientModel):
    _name = 'compare.sanitation.wiz'

    from_date = fields.Date(string='From', required=True, )
    to_date = fields.Date(string='To', required=True)
    tanker_type = fields.Selection([('commercial', 'تجاري'), ('company', 'خاص بالشركة')]
                                   , string='Tanker Type')

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['tanker_type'] = self.tanker_type

        return self.env.ref('admin_module.report_sanitation_id').report_action([], data=data)


class CompareSanitationReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_sanitation_ids'

    def _get_header_info(self, data):
        global month, lmonth
        from_date = data['from_date']
        to_date = data['to_date']
        tanker_type = data['tanker_type']

        #     ################################################################# get month my own way
        f_month = datetime.strptime(str(data['from_date']), '%Y-%m-%d').strftime('%m')
        if f_month == 1:
            month = 'يناير'
        return {
            'from_date': from_date,
            'to_date': to_date,
            'tanker_type': tanker_type,
            'month': month,
        }

    ################################################## get month by jameela way

    def _get_months(self, data):
        date_list = []
        global month
        from_date = datetime.strptime(str(data['from_date']), '%Y-%m-%d')
        to_date = datetime.strptime(str(data['to_date']), '%Y-%m-%d')
        num_months = (to_date.year - from_date.year) * 12 + (
                to_date.month - from_date.month)
        i = 0
        col = 0
        while i != num_months + 1:
            date = from_date + relativedelta(months=i)
            if date.month == 1:
                month = 'يناير'
            if date.month == 2:
                month = 'فبراير'
            if date.month == 3:
                month = 'مارس'
            if date.month == 4:
                month = 'أبريل'
            if date.month == 5:
                month = 'مايو'
            if date.month == 6:
                month = 'يونيو'
            if date.month == 7:
                month = 'يوليو'
            if date.month == 8:
                month = 'أغسطس'
            if date.month == 9:
                month = 'سبتمبر'
            if date.month == 10:
                month = 'أكتوبر'
            if date.month == 11:
                month = 'نوفمبر'
            if date.month == 12:
                month = 'ديسمبر'
            col += 1
            i += 1
            date_list.append(month)
            res = [date_list[0], date_list[-1]]
            name_length = len(date_list)
            print(name_length)
        return date_list

    # all company
    def _get_sanitation_company(self, data):
        global fday, lday
        list_data_company = []
        from_date = datetime.strptime(str(data['from_date']), '%Y-%m-%d')
        to_date = datetime.strptime(str(data['to_date']), '%Y-%m-%d')
        num_months = (to_date.year - from_date.year) * 12 + (
                to_date.month - from_date.month)
        i = 0
        while i != num_months + 1:
            date = from_date + relativedelta(months=i)
            fday = date.replace(day=1)
            lday = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            sanitation_company = self.env['sanitation.follow'].search([
                ('date', '>=', fday),
                ('date', '<=', lday),
                ('tanker_type', '=', 'company')])
            list_data_company.append({
                'tanker_type': 'company',
                'total_company': len(sanitation_company),
            })
            i += 1
        return list_data_company

        # all commercial

    def _get_sanitation_commercial(self, data):
        list_data_commercial = []
        from_date = datetime.strptime(str(data['from_date']), '%Y-%m-%d')
        to_date = datetime.strptime(str(data['to_date']), '%Y-%m-%d')
        num_months = (to_date.year - from_date.year) * 12 + (
                to_date.month - from_date.month)
        i = 0
        while i != num_months + 1:
            date = from_date + relativedelta(months=i)
            fday = date.replace(day=1)
            lday = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            sanitation_commercial = self.env['sanitation.follow'].search([
                ('date', '>=', fday),
                ('date', '<=', lday),
                ('tanker_type', '=', 'commercial')])
            list_data_commercial.append({
                'tanker_type': 'commercial',
                'total_commercial': len(sanitation_commercial),
            })
            i += 1
        return list_data_commercial

    @api.model
    def _get_total(self, data):
        global fday, lday
        list_total = []
        from_date = datetime.strptime(str(data['from_date']), '%Y-%m-%d')
        to_date = datetime.strptime(str(data['to_date']), '%Y-%m-%d')
        num_months = (to_date.year - from_date.year) * 12 + (
                to_date.month - from_date.month)
        i = 0
        while i != num_months + 1:
            date = from_date + relativedelta(months=i)
            fday = date.replace(day=1)
            lday = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            sanitation_company = self.env['sanitation.follow'].search([('date', '>=', fday), ('date', '<=', lday), ])
            list_total.append({'total': len(sanitation_company)})
            i += 1
        return list_total

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['sanitation.follow'].browse(data)
        docs = data['records']
        sanitation_details_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_sanitation_ids')
        docargs = {
            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': sanitation_details_report.model,
            'docs': data,
            'get_months': self._get_months(data),
            'get_header_info': self._get_header_info(data),
            'get_total': self._get_total(data),
            'get_sanitation_company': self._get_sanitation_company(data),
            'get_sanitation_commercial': self._get_sanitation_commercial(data)
        }
