# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class GarbageReportWiz(models.TransientModel):
    _name = 'garbage.wiz'

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    contractor = fields.Many2one('res.partner', string='Contractor')

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['contractor'] = self.contractor.id
        return self.env.ref('admin_module.report_all_garbage_ids').report_action([], data=data)


class GarbageReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_garbage_ids'

    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        contractor = data['contractor']
        return {
            'from_date': from_date,
            'to_date': to_date,
            'contractor': contractor,
        }

    def _get_garbage_details(self, data):
        list_data = []

        garbage = self.env['garbage.calculation'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']), ])
        garbage_line = garbage.mapped('gar_info_ids')
        # for all
        if data['from_date'] and data['to_date'] and not data['contractor']:
            if garbage_line:
                for rec in garbage_line:
                    print("jjjjjjjjjjjjj", garbage_line)
                    list_data.append({
                        'contractor': rec.contractor.name,
                        'total': rec.total,
                        'cost': rec.cost,
                        'total_cost': rec.total_cost,
                        'notes': rec.notes,
                    })
                return list_data
                print('kkkkkkkkkk', list_data)
            #     for contractor only  --done
        if data['from_date'] and data['to_date'] and data['contractor']:
            print('pppppppppppp')
            if garbage_line:
                print('!!!!!!!!!!!!')
                for rec in garbage_line.filtered(lambda r: r.contractor.id == data['contractor']):
                    print('llllllll', rec)
                    list_data.append({
                        'contractor': rec.contractor.name,
                        'total': rec.total,
                        'cost': rec.cost,
                        'total_cost': rec.total_cost,
                        'notes': rec.notes,
                    })
                return list_data
                print('mmmmmmmmm', list_data)

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['garbage.calculation.info'].browse(data)
        docs = data['records']
        garbage_details_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_garbage_ids')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': garbage_details_report.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_garbage_details': self._get_garbage_details(data),
        }
