# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class TotalTankerWiz(models.TransientModel):
    _name = 'total.tanker.wiz'

    from_date = fields.Date(string='From Date', )
    to_date = fields.Date(string='To Date', )
    tanker_type = fields.Selection([('commercial', 'Commercial'), ('company', 'Company')]
                                   , string='tanker type')
    contractor = fields.Many2one('res.partner', string='Contractor')
    date = fields.Date(string='Date')

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['date'] = self.date
        data['tanker_type'] = self.tanker_type
        data['contractor'] = self.contractor.id
        return self.env.ref('admin_module.report_tanker_details').report_action([], data=data)


class TotalTankerReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_tanker_details'

    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        date = data['date']
        tanker_type = data['tanker_type']
        contractor = data['contractor']
        return {
            'from_date': from_date,
            'to_date': to_date,
            'date': date,
            'tanker_type': tanker_type,
            'contractor': contractor,
        }

    def _get_tanker_details(self, data):
        list_data = []
        # list_data2 = []
        tanker = self.env['sanitation.calculation'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']), ])
        tanker_line = tanker.mapped('santi_info_ids')
        # tanker_date = self.env['sanitation.calculation'].search([('date', '>=', data['date']), ])
        # if data['date']:
        # and not data['from_date'] and not data['to_date'] and not data['tanker_type'] and not data['contractor']:
        # if tanker_date:
        #     for rec in tanker_date.filtered(lambda r: r.date == data['date']):
        #         print('yyyyyyyyyyyyyy', rec)
        #         list_data2.append({
        #             'tanker_type': rec.tanker_type,
        #             'contractor': rec.contractor.name,
        #             'tanker_count': rec.tanker_count,
        #             'notes': rec.notes,
        #         })
        #     return list_data2

        # for all
        if data['from_date'] and data['to_date'] and not data['tanker_type'] and not data['contractor']:
            for t in tanker:
                # if tanker_line:
                for rec in t.santi_info_ids:
                    list_data.append({
                        'date': t.date,
                        'tanker_type': rec.tanker_type,
                        'contractor': rec.contractor.name,
                        'tanker_count': rec.tanker_count,
                        'notes': rec.notes,
                    })
            return list_data
            #     for tanker only  --done
        if data['from_date'] and data['to_date'] and data['tanker_type'] and not data['contractor']:
            for t in tanker:
                if tanker_line:
                    for rec in t.santi_info_ids.filtered(lambda r: r.tanker_type == data['tanker_type']):
                        list_data.append({
                            'date': t.date,
                            'tanker_type': rec.tanker_type,
                            'contractor': rec.contractor.name,
                            'tanker_count': rec.tanker_count,
                            'notes': rec.notes,
                        })
            return list_data
            #  for no tanker type but contractor only
        if data['from_date'] and data['to_date'] and not data['tanker_type'] and data['contractor']:
            if tanker_line:
                for rec in tanker_line.filtered(lambda r: r.contractor.id == data['contractor']):
                    list_data.append({
                        'tanker_type': rec.tanker_type,
                        'contractor': rec.contractor.name,
                        'tanker_count': rec.tanker_count,
                        'notes': rec.notes,
                    })
                return list_data

                #  for both car and type
        if data['from_date'] and data['to_date'] and data['tanker_type'] and data['contractor']:
            if tanker_line:
                for rec in tanker_line.filtered(
                        lambda r: r.tanker_type == data['tanker_type'] and r.contractor.id == data['contractor']):
                    list_data.append({
                        'tanker_type': rec.tanker_type,
                        'contractor': rec.contractor.name,
                        'tanker_count': rec.tanker_count,
                        'notes': rec.notes,
                    })
                return list_data

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['sanitation.calculation.info'].browse(data)
        docs = data['records']
        tanker_details_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_sanitation_follow')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': tanker_details_report.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_tanker_details': self._get_tanker_details(data),
        }
