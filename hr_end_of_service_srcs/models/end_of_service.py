# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class EndOfService(models.Model):
    _name = 'end_of.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    date = fields.Date(string="Date",
                       required=False,
                       default=fields.Date.context_today)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=False, )
    job_position_id = fields.Many2one(comodel_name="hr.job", string="Job Position", required=False, )
    employee_number = fields.Char(string="Employee Number", required=False, )
    start_training_date = fields.Date(string="Start Training Date", required=False)
    end_training_date = fields.Date(string="End Training Date", required=False)
    training_period = fields.Char(string="Training Period", required=False,
                                  compute='get_training_period', default='')
    working_years = fields.Char(string="Working Years", required=False,
                                compute='get_working_years', store=True)
    date_of_hiring_date = fields.Date(string="Date of Hiring", required=False)
    end_of_service_date = fields.Date(string="Date End of Service", required=False)
    basic_salary = fields.Float(string="Basic Salary", required=False, )
    comprehensive_wage = fields.Float(string="Wage", required=False, )

    reason = fields.Many2one(comodel_name="reasons.end_of.service", string="Reason", required=False, )

    financial_dues_ids = fields.One2many(comodel_name="financial.dues",
                                         inverse_name="end_of_service_id", string="", required=False, )

    pay_for_working_days = fields.Float(string="Pay For Working Days", required=False, )
    month_of_warning = fields.Float(string="Month of Warning", required=False, )
    leave_entitlement = fields.Float(string="Leave Entitlement", required=False, )
    leave_transportation_allowance = fields.Float(string="Leave Transportation Allowance", required=False, )
    end_of_service_gratuity = fields.Float(string="End of Service Gratuity", required=False, )
    extra_pay = fields.Float(string="Extra Pay", required=False, )
    grants_and_incentives = fields.Float(string="Grants & Incentives", required=False, )
    other = fields.Float(string="Other", required=False, )
    compensation = fields.Float(string="Compensation(Basic * 6 months)", required=False, )

    month_of_warning_deduction = fields.Float(string="Month Of Warning", required=False, )
    absence_deduction = fields.Float(string="Absence", required=False, )
    loan_deduction = fields.Float(string="Loans", required=False, )
    work_days_paid_with_salary_deduction = fields.Float(string="Work days paid with salary", required=False, )
    violations_and_fines_deduction = fields.Float(string="Violations and fines", required=False, )
    grants_and_incentives_deduction = fields.Float(string="Grants and incentives", required=False, )
    total_deduction = fields.Float(string="Total Deduction", required=False, )

    # Check Invisible
    pay_for_working_days_boolean = fields.Boolean(string="Pay For Working Days", required=False
                                                  , related='reason.pay_for_working_days')
    month_of_warning_boolean = fields.Boolean(string="Month of Warning", required=False,
                                              related='reason.month_of_warning')
    leave_entitlement_boolean = fields.Boolean(string="Leave Entitlement", required=False,
                                               related='reason.leave_entitlement')
    leave_transportation_allowance_boolean = fields.Boolean(string="Leave Transportation Allowance",
                                                            related='reason.leave_transportation_allowance',
                                                            required=False, )
    end_of_service_gratuity_boolean = fields.Boolean(string="End of Service Gratuity",
                                                     related='reason.end_of_service_gratuity',
                                                     required=False, )
    extra_pay_boolean = fields.Boolean(string="Extra Pay", required=False,
                                       related='reason.extra_pay')
    grants_and_incentives_boolean = fields.Boolean(string="Grants & Incentives",
                                                   related='reason.grants_and_incentives',
                                                   required=False, )
    other_boolean = fields.Boolean(string="Other", required=False,
                                   related='reason.other')
    compensation_boolean = fields.Boolean(string="compensation(Basic * 6 months)", required=False,
                                          related='reason.compensation'
                                          )

    total_benefits = fields.Float(string="Total Benefits", required=False, readonly=True)

    @api.onchange('employee_id')
    def get_employee_data(self):
        for rec in self:
            rec.job_position_id = rec.employee_id.job_id.id
            rec.comprehensive_wage = rec.employee_id.contract_id.wage
            # rec.basic_salary = rec.employee_id.pin
            rec.basic_salary = rec.comprehensive_wage * 60 / 100

    @api.depends('start_training_date', 'end_training_date')
    def get_training_period(self):
        for rec in self:
            if rec.start_training_date or rec.end_training_date:
                days = relativedelta(rec.end_training_date, rec.start_training_date).days
                months = relativedelta(rec.end_training_date, rec.start_training_date).months
                years = relativedelta(rec.end_training_date, rec.start_training_date).years
                rec.training_period = " Years: " + str(years) + " Months : " + str(months) + " Days : " + str(days)
            else:
                rec.training_period = ""

    @api.depends('employee_id', 'end_of_service_date')
    def get_working_years(self):
        for rec in self:
            if rec.employee_id:

                # contract = self.env['hr.contract'].search([
                #     ('employee_id', '=', rec.employee_id.id),
                #     ('state', '=', 'open')
                # ])

                rec.date_of_hiring_date = rec.employee_id.contract_id.date_start
                if rec.employee_id.contract_id.date_end:
                    rec.end_of_service_date = rec.employee_id.contract_id.date_end
                res = self.env['indemnity.config.line'].search([])
                days = relativedelta(rec.end_of_service_date, rec.date_of_hiring_date).days
                months = relativedelta(rec.end_of_service_date, rec.date_of_hiring_date).months
                years = relativedelta(rec.end_of_service_date, rec.date_of_hiring_date).years

                rec.working_years = " Years: " + str(years) + " Months : " + str(months) + " Days : " + str(days)
            else:
                rec.working_years = ''

                # print('------------res', res)
                # print('------------days', days)
                # for line in res:

    # @api.onchange('reason')
    # def create_FinancialDues(self):
    #     for rec in self:
    #         if rec.reason:
    #             res = self.env['reasons.end_of.service'].search([('reason', '=', rec.reason)],limit=1)
    #             if res:
    #                 for reason in res:
    #                     if reason.pay_for_working_days:
    #                         rec.pay_for_working_days_boolean = True
    #                     else:
    #                         rec.pay_for_working_days_boolean = False
    #
    #                     if reason.month_of_warning:
    #                         rec.month_of_warning_boolean = True
    #                     else:
    #                         rec.month_of_warning_boolean = False
    #
    #                     if reason.leave_entitlement:
    #                         rec.leave_entitlement_boolean = True
    #                     else:
    #                         rec.leave_entitlement_boolean = False
    #
    #                     if reason.leave_transportation_allowance:
    #                         rec.leave_transportation_allowance_boolean = True
    #                     else:
    #                         rec.leave_transportation_allowance_boolean = False
    #
    #                     if reason.end_of_service_gratuity:
    #                         rec.end_of_service_gratuity_boolean = True
    #                     else:
    #                         rec.end_of_service_gratuity_boolean = False
    #
    #                     if reason.extra_pay:
    #                         rec.extra_pay_boolean = True
    #                     else:
    #                         rec.extra_pay_boolean = False
    #
    #                     if reason.grants_and_incentives:
    #                         rec.grants_and_incentives_boolean = True
    #                     else:
    #                         rec.grants_and_incentives_boolean = False
    #
    #                     if reason.other:
    #                         rec.other_boolean = True
    #                     else:
    #                         rec.other_boolean = False
    #
    #                     if reason.compensation:
    #                         rec.compensation_boolean = True
    #                     else:
    #                         rec.compensation_boolean = False

    def action_compute(self):
        for rec in self:

            years = relativedelta(rec.end_of_service_date, rec.date_of_hiring_date).years
            if rec.employee_id:
                total_benefits = 0.0
                res_payslip = self.env['hr.payslip'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', 'not in', ['done', 'paid']),
                ], order='date_to desc', limit=1)
                print('----------res_payslip', res_payslip)
                if res_payslip:
                    rec.pay_for_working_days = res_payslip.net_wage
                    rec.compensation = rec.basic_salary * 6
                    res_config = self.env['indemnity.config'].search([], order='date desc',
                                                                     limit=1)
                for line in res_config.indemnity_config_ids:
                    if years >= line.from_year and years <= line.to_year:
                        if line.month_count == '1':
                            rec.end_of_service_gratuity = 1 * rec.basic_salary * years
                        if line.month_count == '2':
                            rec.end_of_service_gratuity = 1.5 * rec.basic_salary * years

                        if line.month_count == '3':
                            rec.end_of_service_gratuity = 2 * rec.basic_salary * years

                        if line.month_count == '4':
                            rec.end_of_service_gratuity = 2.5 * rec.basic_salary * years

                        if line.month_count == '5':
                            rec.end_of_service_gratuity = 3 * rec.basic_salary * years

                rec.leave_transportation_allowance = (rec.comprehensive_wage / 30) * rec.employee_id.remaining_leaves
                total_benefits = rec.pay_for_working_days + rec.month_of_warning + rec.leave_entitlement + rec.leave_transportation_allowance + rec.end_of_service_gratuity + rec.extra_pay + rec.grants_and_incentives + rec.other + rec.compensation
                rec.total_benefits = total_benefits

                # print('------------res', res_config)


class FinancialDues(models.Model):
    _name = 'financial.dues'

    name = fields.Char(string="Name", required=False, )
    amount = fields.Float(string="Amount", required=False, )
    note = fields.Text(string="Note", required=False, )

    end_of_service_id = fields.Many2one(comodel_name="end_of.service", string="", required=False, )
