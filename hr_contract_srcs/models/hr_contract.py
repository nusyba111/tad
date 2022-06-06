# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayrollStructre(models.Model):
    _inherit = 'hr.payroll.structure'

    @api.model
    def _get_default_rule_ids(self):
        return []

    rule_ids = fields.One2many(
        'hr.salary.rule', 'struct_id',
        string='Salary Rules', default=_get_default_rule_ids)

class HRContract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection([('permanent','Permanent Contracts'),
                                    ('temporary','Temporary Contracts'),
                                    ('consultancy','Consultancy Contracts')],string="Type")
    salary_plan = fields.One2many('salary.plan','contract_id',string="Salary Plan")


class SalaryPlan(models.Model):
    _name = 'salary.plan'

    contract_id = fields.Many2one('hr.contract',string="Contract")
    covered_by = fields.Many2one('account.analytic.account',string="Covered By",domain="[('type','=','project')]")
    percentage_of_covering = fields.Float(string="Percentage Of Covering")
    coverage_in_usd = fields.Float(string="Coverage In USD")
        

