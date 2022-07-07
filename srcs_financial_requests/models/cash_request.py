from odoo import fields, api, models, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class SrcsCashRequest(models.Model):
    _name = "cash.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

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
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', default=lambda self: self.env.company.currency_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    requested_amount = fields.Monetary('Requested Amount', currency_field='currency_id')
    requested_amount_sdg = fields.Monetary(compute='_compute_requested_amount_sdg', string='Requested Amount SDG', currency_field='company_currency_id', store=True )
    description = fields.Html('Description',compute='_compute_description')
    amount_in_words = fields.Char('Amount In Words')
    amount_in_words_sdg = fields.Char('Amount In Words SDG')
    user_lang_id = fields.Selection(related='user_id.lang', string='Lang')
    is_branch_loans = fields.Boolean('Is Branch Loans')
    internal_transfer_id = fields.Many2one('account.payment', string='Internal Transfer')
    is_cleared = fields.Boolean(string="Cleared", readonly=True, copy=False)
    
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
    ],default="draft", string='field_name')

    @api.depends('project_id','donor_id','budget_line_id')
    def _compute_description(self):
        for desc in self:
            if desc.project_id and desc.budget_line_id:
                desc.description = "Khartoum-Sudan" + "\n" + "\n" + "With refrence to the project Agreement that was signed between the Sudanese Red Crescent Society and the" + " " + str(desc.donor_id.name) + " " + "the project" + str('%s' %(desc.project_id.name)) + " " + "as of " +str(desc.budget_line_id.date_from) + "we here by request the following payment for the quartor one in the amount of:"
            else:
                desc.description = " "
                
    @api.depends('requested_amount')
    def _compute_requested_amount_sdg(self):
        for rec in self:
            if rec.requested_amount:
                if self.currency_id == self.company_currency_id:
                    rec.requested_amount_sdg = rec.requested_amount
                else:
                    rec.requested_amount_sdg = rec.requested_amount / rec.currency_id.rate
            else:
                rec.requested_amount_sdg = 0

    @api.onchange('budget_line_id')
    def onchange_budget_line(self):
        self.residual_amount = self.budget_line_id.balance_budget_currency
        self.donor_id = self.budget_line_id.crossovered_budget_id.donor_id.id

    @api.onchange('is_branch_loans','project_id')
    def _onchange_is_branch_loans(self):
        # core_budget_line = self.env['crossovered.budget.lines'].search([('crossovered_budget_id.budget_type','=','core')]).ids
        core_project = self.env['account.analytic.account'].search([('crossovered_budget_line.crossovered_budget_id.budget_type','=','core'),('type','=','project')]).ids
        if self.is_branch_loans:
            print('____________core_project',core_project)
            return{'domain':{'project_id':[('id','in',core_project)]}}
        else:
            print('____________xxxxcore_budget_line',core_project)
            pass 

    def confrim_finance(self):
        self.state = "branch_finance"

    def confirm_branch_dir(self):
        self.state = "branch_director"
    
    def approve_secratry(self):
        self.state = "secratry_general"

    def confirm_finance_department(self):
        self.state = "finance_department"

    def approve_program_department(self):
        if not self.is_branch_loans:
            self.state = "program_department"
            print('___________self.is_branch_loans',self.is_branch_loans)
        else:
            self.state = "internal_auditor"
            print('___________xxxxself.is_branch_loans',self.is_branch_loans)

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
                    'branch_id':self.dest_bank.branch_id.id,
                    'transfer_to':self.source_bank.branch_id.id,
                })
            print('_______________________',internal_transfer)
            if internal_transfer:
                self.internal_transfer_id = internal_transfer.id
                self.state = "payment"


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
                    r.amount_in_words = money_to_text_en.amount_to_text(r.requested_amount, r.currency_id.name)
                    r.amount_in_words_sdg =  money_to_text_en.amount_to_text(r.requested_amount_sdg, r.company_currency_id.name)
                if r.user_lang_id == 'ar_001':
                    print('______________langarabic',r.user_lang_id)
                    r.amount_in_words = money_to_text_ar.amount_to_text_arabic(r.requested_amount, r.currency_id.name)
                    r.amount_in_words_sdg =  money_to_text_ar.amount_to_text_arabic(r.requested_amount_sdg, r.company_currency_id.name)

    @api.constrains('requested_amount')
    def _check_requested_amount(self):
        print('hreeeeeeeeeeeeeeeeeeeeeeeeeeee')
        for rec in self:
            if rec.currency_id == rec.budget_currency.id:
                if rec.requested_amount > rec.residual_amount:
                    print('________________________________requested_amount',rec.requested_amount)
                    raise ValidationError(_('Requested Amount should be less than or equal to Bugdet Residual Amount'))  
            else:
                print("\n\n\n\n\n\n\n\n")
                print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
                request_amount = 0
                budget_amount_company_currency = 0
                request_amount = rec.requested_amount / rec.currency_id.rate 
                budget_amount_company_currency = rec.residual_amount / rec.budget_currency.rate
                if request_amount > budget_amount_company_currency:
                    print('________________________________total_currency',budget_amount_company_currency)
                    raise ValidationError(_('Requested Amount should be less than or equal to Bugdet Residual Amount'))
