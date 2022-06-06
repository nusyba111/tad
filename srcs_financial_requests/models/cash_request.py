from odoo import fields, api, models, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

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
    residual_amount = fields.Monetary('Residual amount ', currency_field='budget_currency')
    requested_amount = fields.Monetary('Requested Amount', currency_field='budget_currency')
    requested_amount_sdg = fields.Monetary(compute='_compute_requested_amount_sdg', string='Requested Amount SDG', currency_field='currency_id', store=True )
    description = fields.Html('Description',compute='_compute_description')
    amount_in_words = fields.Char('Amount In Words')
    amount_in_words_sdg = fields.Char('Amount In Words SDG')
    user_lang_id = fields.Selection(related='user_id.lang', string='Lang')
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

    @api.depends('project_id','donor_id','budget_line_id')
    def _compute_description(self):
        for desc in self:
            if desc.project_id and desc.donor_id and desc.budget_line_id:
                desc.description = "Khartoum-Sudan" + "\n" + "\n" + "With refrence to the project Agreement that was signed between the Sudanese Red Crescent Society and the" + " " + str(desc.donor_id.name) + " " + "the project" + str('%s' %(desc.project_id.name)) + " " + "as of " +str(desc.budget_line_id.date_from) + "we here by request the following payment for the quartor one in the amount of:"
            else:
                desc.description = " "
                
    @api.depends('requested_amount')
    def _compute_requested_amount_sdg(self):
        for rec in self:
            if rec.requested_amount:
                rec.requested_amount_sdg = rec.requested_amount / rec.budget_currency.rate
            else:
                rec.requested_amount_sdg = 0

    @api.onchange('budget_line_id')
    def onchange_budget_line(self):
        self.residual_amount = self.budget_line_id.balance_budget_currency
       
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
            raise UserError(_('Source Bank should be entered .'))
        else:    
            internal_transfer = self.env['account.payment'].create({
                    'is_internal_transfer':True,
                    'type_internal_transfer':'branch',
                    'payment_type':'outbound',
                    'project_id':self.project_id.id,
                    'journal_id':self.source_bank.id,
                    'destination_journal_id':self.dest_bank.id,
                    'amount':self.requested_amount,
                    'date':self.date,
                    'currency_id':self.currency_id.id,
                    'ref':self.name,
                    'branch_id':self.branch_id.id,
                })
            print('_______________________',internal_transfer)
            if internal_transfer:
                self.state = "payment"

    def end(self):
        self.state = "end"

    def reset_to_draft(self):
        self.state = "draft"

   
    @api.onchange('requested_amount', 'currency_id')
    def _compute_amount_in_words(self):
        from . import money_to_text_en
        from . import money_to_text_ar
        for r in self:
            if r.requested_amount:
                if r.user_lang_id == 'en_US':
                    print('______________lang',r.user_lang_id)
                    r.amount_in_words = money_to_text_en.amount_to_text(r.requested_amount, r.budget_currency.name)
                    r.amount_in_words_sdg =  money_to_text_en.amount_to_text(r.requested_amount_sdg, r.currency_id.name)
                if r.user_lang_id == 'ar_001':
                    print('______________langarabic',r.user_lang_id)
                    r.amount_in_words = money_to_text_ar.amount_to_text_arabic(r.requested_amount, r.budget_currency.name)
                    r.amount_in_words_sdg =  money_to_text_ar.amount_to_text_arabic(r.requested_amount_sdg, r.currency_id.name)

    @api.constrains('requested_amount')
    def _constrains_requested_amount(self):
        for record in self:
            if record.requested_amount > record.residual_amount:
                raise UserError(_('Requested Amount should be less than or equal to Residual Amount'))
