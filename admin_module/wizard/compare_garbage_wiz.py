# -*- coding: utf-8 -*-
import calendar

from dateutil.relativedelta import relativedelta
from odoo import api, models, fields, _
# import calendar
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class GarbageFollowReportWiz(models.TransientModel):
    _name = 'garbage.follow.wiz'

    from_date = fields.Date(string='From', required=True, )
    to_date = fields.Date(string='To', required=True)

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        return self.env.ref('admin_module.report_compare_all_garbage').report_action([], data=data)


class GarbageFollowReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_compare_garbage'

    def _get_header_info(self, data):
        global month, lmonth
        from_date = data['from_date']
        to_date = data['to_date']
        f_year = datetime.strptime(str(data['from_date']), '%Y-%m-%d').strftime('%Y')
        return {
            'from_date': from_date,
            'to_date': to_date,
            'f_year': f_year
        }

    # all data
    def _get_compare_garbage_details(self, data):
        global month
        list_data = []
        from_date = datetime.strptime(str(data['from_date']), '%Y-%m-%d')
        to_date = datetime.strptime(str(data['to_date']), '%Y-%m-%d')
        num_months = (to_date.year - from_date.year) * 12 + (
                to_date.month - from_date.month)
        i = 0
        while i != num_months + 1:
            total_all = 0.0
            total = 0.0
            cost = 0.0
            report_count_total = 0.0
            report_cost_total = 0.0
            report_total_total = 0.0
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
            fday = date.replace(day=1)
            lday = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            agreed_count = self.env['garbage.calculation'].search([
                ('date', '>=', fday),
                ('date', '<=', lday), ])
            for agreed in agreed_count:
                total = agreed.total_agreed_report
                cost = agreed.total_cost_report
                total_all = total * cost
                report_count_total += total
                report_cost_total += cost
                report_total_total += total_all
            list_data.append({
                'month': month,
                'total_all': total_all,
                'total_count': total,
                'total_cost': cost,
            })
            print('list_data', list_data)
            i += 1
        return list_data

    # @api.model
    # def _get_total(self, data):
    #     global fday, lday
    #     list_total = []
    #     print(list_total, 'pppppppppppppppppppppppppp')
    #     from_date = datetime.strptime(str(data['from_date']), '%Y-%m-%d')
    #     to_date = datetime.strptime(str(data['to_date']), '%Y-%m-%d')
    #     num_months = (to_date.year - from_date.year) * 12 + (
    #             to_date.month - from_date.month)
    #     i = 0
    #     while i != num_months + 1:
    #         date = from_date + relativedelta(months=i)
    #         fday = date.replace(day=1)
    #         lday = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    #         garbage_company = self.env['garbage.calculation'].search([])
    #         list_total.append({'total': len(garbage_company)})
    #         print(list_total, ';;;;;;;;;;;;;;;;;;;;;;;;')
    #         i += 1
    #     return list_total

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['garbage.calculation.info'].browse(data)
        docs = data['records']
        compare_garbage_details_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_garbage_ids')
        docargs = {
            'data': data,
            'docs': docs,
        }

        return {
            'doc_ids': self.ids,
            'doc_model': compare_garbage_details_report.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_compare_garbage_details': self._get_compare_garbage_details(data),
            # '_get_total': self._get_total(data)
        }
