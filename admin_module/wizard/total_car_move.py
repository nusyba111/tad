# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, models, fields, _


class LoanCarWiz(models.TransientModel):
    _name = 'total.car.move'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    car = fields.Many2one("fleet.vehicle", string="Car", domain="[('car_noe', '!=', False)]")
    # number_of_days = fields.Integer(compute='com_number_of_days', string='duration')

    # @api.onchange('from_date', 'to_date')
    # def com_number_of_days(self):
    #     self.number_of_days = 0
    #     for rec in self:
    #         daaa = (rec.to_date, rec.from_date)
    #         rec.number_of_days = daaa.days

            # for rec in self:
        #     dt_delta = (rec.to_date - rec.from_date)
        #     rec.number_of_days = dt_delta.days + ((dt_delta.seconds / 3600) / 24)
        #     print('ddddddddddddddddddddddddddddddddddddd', rec.number_of_days)

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['car'] = self.car.id
        return self.env.ref('admin_module.report_total_cars_move').report_action([], data=data)


class CarMoveReport(models.AbstractModel):
    _name = 'report.admin_module.template_total_cars_move'

    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        car = data['car']
        return {
            'from_date': from_date,
            'to_date': to_date,
            'car': car,
        }

    def _get_total_car_move(self, data):
        list_data = []

        car_att = self.env['transportation.cars.attendance'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']),
        ])
        car_list = car_att.mapped('cars_transport_list_ids')
        loan = self.env['loan.car'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']),
        ])
        car_warning = self.env['cars.warning'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']),
        ])
        if data['from_date'] and data['to_date'] and data['car']:
            if car_att:
                for line in car_list.filtered(lambda r: r.car_no.id == data['car']):
                    for war in car_warning:
                        list_data.append({
                            'att_count': line.att_count,
                            # 'attend_time_count': line.attend_time_count,
                            'total_warning': war.total_warning,  # 'loan_amount': rec.loan_amount,
                            # 'loan_type': rec.loan_type,
                            # 'remain_loan_amount': rec.remain_loan_amount,
                            # 'notes': rec.notes,
                        })
            return list_data

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['transportation.cars.attendance.line'].browse(data)
        docs = data['records']
        total_car_move = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_total_cars_move')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': total_car_move.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_total_car_move': self._get_total_car_move(data),

        }
