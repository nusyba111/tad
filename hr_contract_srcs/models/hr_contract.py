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
    struct_id = fields.Many2one('hr.payroll.structure',string="Structure")
    rule_ids = fields.One2many('hr.salary.rule',related="struct_id.rule_ids")
    forgin_currency_id = fields.Many2one('res.currency',string="Currency",readonly=False)
    wage_per_hour = fields.Float(compute="_get_wage_per_hour",store=True)
    wage = fields.Monetary('Wage', required=True, tracking=True, help="Employee's monthly gross wage.",currency_field='forgin_currency_id')
    coverage = fields.Many2one('account.account.tag',string="Account Tag")

    @api.depends('wage')
    def _get_wage_per_hour(self):
        for rec in self:
            rec.wage_per_hour = 0.0
            if rec.resource_calendar_id:
                rec.wage_per_hour = (rec.wage / 30) / rec.resource_calendar_id.hours_per_day

class SalaryPlan(models.Model):
    _name = 'salary.plan'

    contract_id = fields.Many2one('hr.contract',string="Contract")
    covered_by = fields.Many2one('account.analytic.account',string="Covered By",domain="[('type','=','project')]")
    percentage_of_covering = fields.Float(string="Percentage Of Covering")
    coverage_in_usd = fields.Float(string="Coverage In USD")



class HRPayslip(models.Model):
    _inherit = 'hr.payslip' 


    rate = fields.Float(string="Rate",compute="_compute_usd_rate") 



    def _compute_usd_rate(self):
        today = fields.Date.today()
        self.rate = self.contract_id.forgin_currency_id._get_conversion_rate(
            self.contract_id.forgin_currency_id, self.company_id.currency_id, self.company_id,today)  
        

