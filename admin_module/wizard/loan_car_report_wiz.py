# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class LoanCarWiz(models.TransientModel):
    _name = 'loan.car.wiz'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    loan_type = fields.Selection([('contractor', 'Contractor'), ('driver', 'Driver')], string='Loan Type')
    car = fields.Many2one("fleet.vehicle", string="Car", domain="[('car_noe', '!=', False)]")

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        # data['filter'] = self.filter
        data['loan_type'] = self.loan_type
        data['car'] = self.car.id
        return self.env.ref('admin_module.report_all_cars_id').report_action([], data=data)


class LoanCarReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_cars_ids'

    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        car = data['car']
        loan_type = data['loan_type']

        return {
            'from_date': from_date,
            'to_date': to_date,
            'car': car,
            'loan_type': loan_type
        }

    def _get_car_loan(self, data):
        list_data = []
        # amount_to_cleared
        loans = self.env['loan.car'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']),
        ])
        clearance = self.env['loan.car.clearance'].search([
            ('date', '>=', data['from_date']),
            ('date', '<=', data['to_date']),
        ])
        # all --done
        if data['from_date'] and data['to_date'] and not data['car'] and not data['loan_type']:
            if loans:
                for rec in loans:
                    for cl in clearance:
                        list_data.append({
                            'car': rec.car_no.name,
                            'loan_count': rec.loan_count,
                            'doc_num': rec.doc_num,
                            'loan_amount': rec.loan_amount,
                            'loan_type': rec.loan_type,
                            'amount_to_cleared': cl.amount_to_cleared,
                            'remain_loan_amount': rec.remain_loan_amount,
                            'notes': rec.notes,
                        })
                return list_data
        #     for car only  --done
        if data['from_date'] and data['to_date'] and data['car'] and not data['loan_type']:
            if loans:
                for rec in loans.filtered(lambda r: r.car_no.id == data['car']):
                    for cl in clearance:
                        list_data.append({
                            'car': rec.car_no.name,
                            'loan_count': rec.loan_count,
                            'doc_num': rec.doc_num,
                            'loan_amount': rec.loan_amount,
                            'loan_type': rec.loan_type,
                            'amount_to_cleared': cl.amount_to_cleared,
                            'remain_loan_amount': rec.remain_loan_amount,
                            'notes': rec.notes,
                        })
                return list_data
        #  for no car but type only ----done
        if data['from_date'] and data['to_date'] and not data['car'] and data['loan_type']:
            if loans:
                for rec in loans.filtered(lambda r: r.loan_type == data['loan_type']):
                    for cl in clearance:
                        list_data.append({
                            'car': rec.car_no.name,
                            'loan_count': rec.loan_count,
                            'doc_num': rec.doc_num,
                            'loan_amount': rec.loan_amount,
                            'loan_type': rec.loan_type,
                            'amount_to_cleared': cl.amount_to_cleared,
                            'remain_loan_amount': rec.remain_loan_amount,
                            'notes': rec.notes,
                        })
                return list_data

                #  for both car and type
        if data['from_date'] and data['to_date'] and data['car'] and data['loan_type']:
            if loans:
                for rec in loans.filtered(lambda r: r.car_no.id == data['car'] and r.loan_type == data['loan_type']):
                    for cl in clearance:
                        list_data.append({
                            'car': rec.car_no.name,
                            'loan_count': rec.loan_count,
                            'doc_num': rec.doc_num,
                            'loan_amount': rec.loan_amount,
                            'loan_type': rec.loan_type,
                            'amount_to_cleared': cl.amount_to_cleared,
                            'remain_loan_amount': rec.remain_loan_amount,
                            'notes': rec.notes,
                        })
                return list_data

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['loan.car'].browse(data)
        docs = data['records']
        loan_details_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_cars_ids')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': loan_details_report.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_car_loan': self._get_car_loan(data),
        }
