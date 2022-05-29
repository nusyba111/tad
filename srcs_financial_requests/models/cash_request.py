from odoo import fields, api, models, _
from datetime import date

# class SrcsBudgetLineRequest(models.Model):
#     _inherit = "crossovered.budget.lines"

#     cash_request_id  = fields.Many2one('cash.request', string='Cash Request')

class SrcsCashRequest(models.Model):
    _name = "cash.request"

    name = fields.Char('Name', required=True)
    date = fields.Date('Request Date',default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='Requestor', default=lambda self: self.env.user)
    project_id = fields.Many2one('account.analytic.account', string='Project', domain="[('type','=','project')]")
    donor_id = fields.Many2one('res.partner', string='Donor', required=True)
    source_bank = fields.Many2one('account.journal', string='Source Bank', required=True)
    dest_bank = fields.Many2one('account.journal', string='Destination Bank',required=True)
    budget_line_id = fields.Many2one('crossovered.budget.lines', string='Budget Line', required=True)
    budget_currency = fields.Many2one(related='budget_line_id.currency_budget_line')
    residual_amount = fields.Monetary('Residual amount ',compute='_compute_budget_residual_amount', currency_field='budget_currency')
    requested_amount = fields.Float('Requested Amount')
    is_branch_loans = fields.Boolean('Is Branch Loans')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    state = fields.Selection([
        ('draft','Draft'),
        ('branch_finance', 'Branch Finance Director'),
        ('branch_director','Branch Director'),
        ('secratry_general','Secretary General '),
        ('finance_department','Finance Department'),
        ('program_department','Program Department'),
        ('internal_auditor','Internal Auditor'),
        ('secratry_general_two','Secretary General '),
        ('payment','Payment'),
        ('end','End'),
    ],default="draft", string='field_name')

    def _compute_budget_residual_amount(self):
        # if self.budget_line_id:
        if self.currency_id == self.budget_currency.id:
            self.residual_amount = self.budget_line_id.balance_budget_currency
            print('_______________________reaedual',self.budget_currency.id)
        else:
            self.residual_amount = self.budget_line_id.balance_SDG
            print('++++++++++++++++++++++++++++++++++++++++++++',self.budget_currency.id)

    def confrim_finance(self):
        self.state = "branch_finance"

    def confirm_branch_dir(self):
        self.state = "branch_director"
    
    def approve_secratry(self):
        self.state = "secratry_general"

    def confirm_finance_department(self):
        self.state = "finance_department"

    def approve_program_department(self):
        self.state = "program_department"

    def confirm_internal_auditor(self):
        self.state = "internal_auditor"
    
    def second_approve_secretary(self):
        self.state = "secratry_general_two"

    def submit_payment(self):
        if not self.source_bank:
            raise ValidationError(_('Source Bank should be entered .'))
        else:    
            internal_transfer = self.env['account.payment'].create({
                    'is_internal_transfer':True,
                    'payment_type':'outbound',
                    'journal_id':self.source_bank.id,
                    'destination_journal_id':self.dest_bank.id,
                    'amount':self.requested_amount,
                    'date':self.date,
                    'currency_id':self.currency_id.id,
                    'ref':self.name,
                })
            print('_______________________',internal_transfer)
            if internal_transfer:
                self.state = "payment"

    def end(self):
        self.state = "end"

    def reset_to_draft(self):
        self.state = "draft"

   
