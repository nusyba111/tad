# -*- coding: utf-8 -*-
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _


class CarMoveWiz(models.TransientModel):
    _name = 'car.move.wiz'
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    # loan_type = fields.Selection([('contractor', 'Contractor'), ('driver', 'Driver')], string='Loan Type')
    car = fields.Many2one("fleet.vehicle", string="Car", domain="[('car_noe', '!=', False)]")

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        # data['loan_type'] = self.loan_type
        data['car'] = self.car.id
        return self.env.ref('admin_module.report_cars_move_id').report_action([], data=data)


class CarMoveReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_cars_move'

    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        # loan_type = data['loan_type']
        car = data['car']
        return {
            'from_date': from_date,
            'to_date': to_date,
            # 'loan_type': loan_type,
            'car': car,
        }

    def _get_car_move(self, data):
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
        # all --done
        if data['from_date'] and data['to_date'] and not data['car']:
            for lo in loan:
                for rec in car_att:
                    for line in rec.cars_transport_list_ids:
                        for wa in car_warning:
                            list_data.append({
                                'car': line.car_no.name,
                                'attend_time': line.attend_time,
                                'loan_amount': lo.loan_amount,
                                'deduction_amount': wa.deduction_amount,
                                # 'remain_loan_amount': rec.remain_loan_amount,
                                'notes': line.notes,
                            })
                    return list_data
        #     for car only  --done
        if data['from_date'] and data['to_date'] and data['car']:
            for lo in loan:
                if car_list:
                    for rec in car_list.filtered(lambda r: r.car_no.id == data['car']):
                        for wa in car_warning:
                            list_data.append({
                                'car': rec.car_no.name,
                                'attend_time': rec.attend_time,
                                # 'doc_num': rec.doc_num,
                                'loan_amount': lo.loan_amount,
                                'deduction_amount': wa.deduction_amount,
                                # 'remain_loan_amount': rec.remain_loan_amount,
                                'notes': rec.notes,
                            })
                    return list_data
        # #  for no car but type only ----done
        # if data['from_date'] and data['to_date'] and not data['car'] and data['loan_type']:
        #     for lo in loan:
        #         for rec in loan.filtered(lambda r: r.loan_type == data['loan_type']):
        #             if car_list:
        #                 for car in car_list:
        #                     for wa in car_warning:
        #                         list_data.append({
        #                             'car': rec.car_no.name,
        #                             'attend_time': car.attend_time,
        #                             # 'doc_num': rec.doc_num,
        #                             'loan_amount': rec.loan_amount,
        #                             'deduction_amount': wa.deduction_amount,
        #                             # 'remain_loan_amount': rec.remain_loan_amount,
        #                             'notes': rec.notes,
        #                         })
        #                 return list_data

        #  for both car and type
        # if data['from_date'] and data['to_date'] and data['car'] and data['loan_type']:
        #     if loan:
        #         for rec in loan.filtered(
        #                 lambda r: r.car_no.id == data['car'] and r.loan_type == data['loan_type']):
        #             for wa in car_warning:
        #                 for car in car_list:
        #                     list_data.append({
        #                         'car': rec.car_no.name,
        #                         'attend_time': car.attend_time,
        #                         # 'doc_num': rec.doc_num,
        #                         'loan_amount': rec.loan_amount,
        #                         'deduction_amount': wa.deduction_amount,
        #                         # 'remain_loan_amount': rec.remain_loan_amount,
        #                         'notes': rec.notes,
        #                     })
        #             return list_data

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['transportation.cars.attendance'].browse(data)
        docs = data['records']
        car_move_details_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_cars_move')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': car_move_details_report.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_car_move': self._get_car_move(data),
            # 'get_loan_info': self._get_loan_info(data),

        }
