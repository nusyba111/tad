# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class HRApprsial(models.Model):
    _inherit = 'hr.appraisal'


    def action_view_create_promotion(self):
        return {
            'name': _('Employee Promotion'),
            'view_mode': 'form',
            'res_model': 'hr.wage.process',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_employee_id': self.employee_id.id},
            }


    def action_view_create_incentive(self):
        return {
            'name': _('Employee Incentive'),
            'view_mode': 'form',
            'res_model': 'hr.incentive',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_request_id': self.env.user.id},
            }
                

