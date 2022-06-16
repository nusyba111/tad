# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReasonsEndOfService(models.Model):
    _name = 'reasons.end_of.service'
    _rec_name = 'reason'

    reason = fields.Selection(string="Reason",
                              selection=[
                                  ('segregation', 'Segregation'),
                                  ('resignation', 'Resignation'),
                                  ('end_of_contract', 'End Of Contract'),
                                  ('obstruction', 'Obstruction'),
                                  ('death', 'Death'),
                                  ('other', 'Other'),
                              ], required=False, )

    pay_for_working_days = fields.Boolean(string="Pay for working days", required=False, )
    month_of_warning = fields.Boolean(string="Month of Warning", required=False, )
    leave_entitlement = fields.Boolean(string="Leave Entitlement", required=False, )
    leave_transportation_allowance = fields.Boolean(string="Leave transportation allowance", required=False, )
    end_of_service_gratuity = fields.Boolean(string="End of Service Gratuity", required=False, )
    extra_pay = fields.Boolean(string="Extra Pay", required=False, )
    grants_and_incentives = fields.Boolean(string="Grants & Incentives", required=False, )
    other = fields.Boolean(string="Other", required=False, )
    compensation = fields.Boolean(string="compensation(Basic * 6 months)", required=False, )
