# -*- coding: utf-8 -*-

from odoo import api, fields, models
from collections import defaultdict
from odoo.tools import float_compare, float_is_zero, plaintext2html
from markupsafe import Markup



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
    

    @api.depends('wage')
    def _get_wage_per_hour(self):
        for rec in self:
            rec.wage_per_hour = 0.0
            if rec.resource_calendar_id:
                rec.wage_per_hour = (rec.wage / 30) / rec.resource_calendar_id.hours_per_day

class SalaryPlan(models.Model):
    _name = 'salary.plan'

    contract_id = fields.Many2one('hr.contract',string="Contract")
    covered_by = fields.Many2one('account.analytic.account',string="Project",domain="[('type','=','project')]")
    percentage_of_covering = fields.Float(string="Percentage Of Covering")
    coverage_in_usd = fields.Float(string="Coverage In USD")
    activity = fields.Many2one('account.analytic.account',domain="[('type','=','activity')]",string="Activity")
    location = fields.Many2one('account.analytic.account',domain="[('type','=','location')]",string="Location")
    doner_id = fields.Many2one('res.partner',string="Doner")


class HRPayslipHelal(models.Model):
    _inherit = 'hr.payslip' 


    rate = fields.Float(string="Rate",compute="_compute_usd_rate") 

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip
        for journal_id in slip_mapped_data: # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
                    move_dict['narration'] += Markup('<br/>')
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = line.total
                        if line.code == 'NET': # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id: # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0


                            debit_line = self._get_existing_lines(
                                    line_ids, line, debit_account_id, debit, credit)  

                            if not debit_line:
                                debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit

                        if credit_account_id: # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            credit_line = self._get_existing_lines(
                                line_ids, line, credit_account_id, debit, credit)

                            if not credit_line:
                                credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids: # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                acc_id = slip.sudo().journal_id.default_account_id.id
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].sudo().create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True


    # def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
    #     print("\n\n\n\n\n\n\n\n")
    #     print("**********************************************_get_existing_lines",line.salary_rule_id.account_debit.user_type_id.type)
    #     existing_lines = (
    #         line_id for line_id in line_ids if
    #         line_id['name'] == line.name
    #         and line_id['account_id'] == account_id
    #         and (line.salary_rule_id.account_debit.user_type_id.type == 'other') or (line.salary_rule_id.account_credit.user_type_id.type == 'other')
    #         and line_id['analytic_account_id'] == (line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id)
    #         and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
    #     return next(existing_lines, False)


    # def _prepare_line_values(self, line, account_id, date, debit, credit):
    #     res = super(HRPayslipHelal,self)._prepare_line_values(line, account_id, date, debit, credit)
    #     if line.salary_rule_id.account_debit.user_type_id.type == 'other' or line.salary_rule_id.account_credit.user_type_id.type == 'other':
    #         res['analytic_tag_ids'] = [(6,0,[line.slip_id.contract_id.coverage.id])]
    #     return res    



    def _compute_usd_rate(self):
        today = fields.Date.today()
        self.rate = self.contract_id.forgin_currency_id._get_conversion_rate(
            self.contract_id.forgin_currency_id, self.company_id.currency_id, self.company_id,today)  
        



# class AccountAnalyticTagHelal(models.Model):
#     _inherit = 'account.analytic.tag'

#     is_coverage = fields.Boolean(string="Is Coverage",default=False)