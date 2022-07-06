from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, Warning


class SrcsPaymentRequest(models.Model):
    _name = "payment.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    sequence = fields.Char(string='Sequence', readonly=True, copy=False, index=True, default=lambda self: 'New Payment Request')
    date = fields.Date('Request Date',default=fields.Date.today(), required=True)
    user_id = fields.Many2one('res.users', string='Requestor', default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Journal')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    pay_to = fields.Many2one('res.partner', string='Pay To')
    is_working_addvance = fields.Boolean('Is Working Advance')
    payment_method = fields.Selection([
        ('cash', 'Cash'),('bank','Bank Transfer'),('check','Check'),
    ], string='Payment Method')
    Check_no = fields.Char('Check No')
    check_date = fields.Date('Check Date')
    request_currency = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id)
    total_amount = fields.Float('Total Amount', compute="_compute_total_amount")
    reason = fields.Char('Request Reason', required=True)
    fn_req_sg_dp_approval_amount = fields.Float(string="Maximum Amount", required=False, readonly=False)
    budget_line_ids = fields.One2many('payment.request.lines', 'payment_request_id', string='Budget Lines')
    # debit_account_id = fields.Many2one('account.account', string='Expensses Account')
    state = fields.Selection([
        ('draft','Draft'),('department', 'Department/Partner'),('finance','Finance Approval'),('internal','Internal Auditor'),
        ('secretary','Secretary General'),('payment','Payment'),('cleared', 'Cleared'),
    ], default='draft', string='State')
    tot_cleared_amount = fields.Float(string="Cleared Amount", required=False, readonly=True, copy=False)
    un_cleared_amount = fields.Float(string="Uncleared Amount", required=False, compute='compute_un_cleared_amount',copy=False)
    is_cleared = fields.Boolean(string="Cleared", readonly=True, copy=False)

    @api.depends('budget_line_ids', 'tot_cleared_amount')
    def compute_un_cleared_amount(self):
        for rec in self:
            rec.un_cleared_amount = rec.total_amount - rec.tot_cleared_amount
            if rec.un_cleared_amount < 0:
                rec.un_cleared_amount = 0
            if rec.un_cleared_amount == 0:
                rec.is_cleared = True

    @api.constrains('total_amount','budget_line_ids')
    def total_amount_validation(self):
        if self.total_amount == 0:
            raise ValidationError(_("Request Amount Must be greater than zero!"))

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'NEW') == 'NEW':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('payment.request') or 'NEW'
        result = super(SrcsPaymentRequest, self).create(vals)
        return result

    @api.depends('budget_line_ids.request_amount')
    def _compute_total_amount(self):
        self.total_amount = 0
        for request in self: 
            for line in request.budget_line_ids:
                request.total_amount += line.request_amount

    @api.onchange('payment_method')
    def _onchange_payment_method(self):
        if self.payment_method == 'cash':
            print('__________________Sdfndfjb')
            return{'domain':{'journal_id':[('type','=','cash')]}}
        if self.payment_method == 'bank':
            print('__________________9686767')
            return{'domain':{'journal_id':[('type','=','bank')]}}
        if self.payment_method == 'check':
            print('__________________xxx')
            return{'domain':{'journal_id':[('type','in',['cash','bank'])]}}

    def action_department(self):
        approval_amount = self.env['ir.config_parameter'].get_param('srcs_financial_requests.fn_req_sg_dp_approval_amount')
        print('_______________approval_amount',approval_amount)
        if approval_amount:
            self.fn_req_sg_dp_approval_amount = float(approval_amount)
            print('__________',float(approval_amount))
        else:
            self.fn_req_sg_dp_approval_amount = 0
        self.state = 'department'

    def action_finance(self):
        self.state = 'finance'

    def move(self):
        entrys = []
        credit_account = self.journal_id.default_account_id.id
        if self.budget_line_ids:
            if self.is_working_addvance:
                dedit_account = self.pay_to.property_account_receivable_id.id 
                if self.payment_method == 'check':
                    debit_val = {
                        'name': self.reason,
                        # 'partner_id': self.partner_id.id,
                        'account_id': dedit_account,
                        'debit': self.total_amount,
                        'Check_no':self.Check_no,
                        # 'analytic_account_id': line1.analytic_account_id.id,
                        # 'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, debit_val))
                    credit_vals = {
                        'name': self.reason,
                        # 'partner_id': False,
                        'account_id': credit_account,
                        'credit':  self.total_amount,
                        'Check_no':self.Check_no,
                        # 'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, credit_vals))
                
                else:
                    debit_val = {
                        'name': self.reason,
                        # 'partner_id': self.partner_id.id,
                        'account_id': dedit_account,
                        'debit': self.total_amount,
                        # 'analytic_account_id': line1.analytic_account_id.id,
                        # 'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, debit_val))
                    credit_vals = {
                        'name': self.reason,
                        # 'partner_id': False,
                        'account_id': credit_account,
                        'credit':  self.total_amount,
                        # 'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, credit_vals))  

            else:
                if self.payment_method == 'check':
                    for line in self.budget_line_ids: 
                        debit_val = {
                            'name': self.reason,
                            # 'partner_id': self.partner_id.id,
                            'account_id':  line.account_id.id ,
                            'debit': line.request_amount,
                            'Check_no':self.Check_no,
                            # 'analytic_account_id': line1.analytic_account_id.id,
                            # 'company_id': self.company_id.id,
                        }
                        entrys.append((0, 0, debit_val))
                    credit_vals = {
                        'name': self.reason,
                        # 'partner_id': False,
                        'account_id': credit_account,
                        'credit':  self.total_amount,
                        'Check_no':self.Check_no,
                        # 'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, credit_vals))
                
                else:
                    for line in self.budget_line_ids: 
                        debit_val = {
                            'name': self.reason,
                            # 'partner_id': self.partner_id.id,
                            'account_id':  line.account_id.id ,
                            'debit': line.request_amount,
                            # 'analytic_account_id': line1.analytic_account_id.id,
                            # 'company_id': self.company_id.id,
                        }
                        entrys.append((0, 0, debit_val))
                    credit_vals = {
                        'name': self.reason,
                        # 'partner_id': False,
                        'account_id': credit_account,
                        'credit':  self.total_amount,
                        # 'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, credit_vals))
                
            vals = {
                'journal_id': self.journal_id.id,
                'date': self.date,
                'ref': self.sequence,
                'move_type':'entry',
                # 'company_id': self.company_id.id,
                'line_ids': entrys
            }
            move = self.env['account.move'].create(vals)
            self.move_id = move
        else:
            raise ValidationError(_('You must add Budget Lines'))
        return vals

    def action_internal(self):
        approval_amount = self.env['ir.config_parameter'].get_param('srcs_financial_requests.fn_req_sg_dp_approval_amount')
        print('_______________approval_amount',approval_amount)
        if self.user_has_groups('accounting_srcs.group_internal_auditor'):
            if self.total_amount > float(approval_amount):
                
                internal_auditor_approval = self.env['ir.config_parameter'].get_param('srcs_financial_requests.internal_auditor_approval')
                print('_______________internal_auditor_approval',internal_auditor_approval)
                if internal_auditor_approval:
                    self.state = 'internal'
                    print('___________________________________internal',self.state)
                else:
                    print('___________________notinternal')
                    raise ValidationError(_('Internal Auditor Approval Required')) 
            else:
                self.move()
                self.state = 'payment'
                print('___________________________________paymentsss',self.state)
        else:
            raise ValidationError(_('Internal Auditor must confirm'))
        
    def action_secretary(self):
        approval_amount = self.env['ir.config_parameter'].get_param('srcs_financial_requests.fn_req_sg_dp_approval_amount')
        print('_______________approval_amount',approval_amount)
        if self.user_has_groups('accounting_srcs.group_secretary_general'):
            if self.total_amount > float(approval_amount):
                
                secerteray_general_approval = self.env['ir.config_parameter'].get_param('srcs_financial_requests.fn_req_sg_approval')
                print('_______________secerteray_general_approval',secerteray_general_approval)
                if secerteray_general_approval:
                    self.state = 'secretary'
                    print('___________________________________secretary',self.state)
                else:
                    print('___________________notsecretary')
                    raise ValidationError(_('Secretary General Approval Required'))
            else:
                self.move()
                self.state = 'payment'
                print('___________________________________paymentpppp',self.state)
        else:
            raise ValidationError(_('Secretary General must confirm'))
            
    def action_payment(self):
        secerteray_general_approval = self.env['ir.config_parameter'].get_param('srcs_financial_requests.fn_req_sg_approval')
        print('_______________secerteray_general_approval',secerteray_general_approval)
        if self.user_has_groups('accounting_srcs.group_secretary_general'):
            if secerteray_general_approval:
                self.move()
                self.state = 'payment'
                print('___________________________________paymentoooo',self.state)
            else:
                print('___________________notpayment')
                raise ValidationError(_('SG Approval Required'))
        else:
            raise ValidationError(_('Secretary General must confirm'))
        
    def cancel_button(self):
        self.move_id.button_cancel()
        self.move_id.unlink()
        self.state = 'draft'

    def reset_to_draft(self):
        self.state = 'draft'

    
class SrcsPaymentLines(models.Model):
    _name = "payment.request.lines"

    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, compute="_compute_buget_balance", store=True)
    donor_id = fields.Many2one('res.partner', string='Donor', required=True)
    project_id = fields.Many2one('account.analytic.account',string='Project', domain="[('type','=','project')]")
    account_id = fields.Many2one('account.account', string='Account',  domain="[('internal_group','in',['expense','asset'])]")
    analytic_activity_id = fields.Many2one('account.analytic.account', 'Output/Activity', domain="[('type','=','activity')]")
    payment_request_id = fields.Many2one('payment.request', string='Payment Request')
    payment_currency = fields.Many2one(related='payment_request_id.request_currency')
    request_amount = fields.Monetary('Requested Amount', currency_field = "payment_currency", required=True)
    budget_balance = fields.Monetary(compute="_compute_buget_balance", string='Budget Balance', store=True)

    @api.depends('donor_id','project_id','account_id','analytic_activity_id')
    def _compute_buget_balance(self):
        for rec in self:
            rec.budget_balance = 0
            if rec.donor_id and rec.project_id and rec.account_id and rec.analytic_activity_id:
                budget_line = self.env['crossovered.budget.lines'].search([('crossovered_budget_id.donor_id','=', rec.donor_id.id),
                                                                            ('analytic_activity_id','=',rec.analytic_activity_id.id),
                                                                            ('analytic_account_id','=',rec.project_id.id),
                                                                            ('general_budget_id.account_ids','in', rec.account_id.id),
                                                                            ('date_from','<=',rec.payment_request_id.date),('date_to','>=',rec.payment_request_id.date),
                                                                            ('crossovered_budget_id.state','=','validate')])
                if budget_line:
                    rec.budget_balance = budget_line.balance_budget_currency
                    rec.currency_id = budget_line.currency_budget_line.id
                else:
                    raise ValidationError(_('There is No Budget for this %s and %s and %s and %s')%(rec.account_id.name,rec.project_id.name,rec.analytic_activity_id.name,rec.donor_id.name))
            else:
                rec.budget_balance = 0

    
    @api.constrains('request_amount','payment_request_id')
    def _check_request_amount(self):
        print('hreeeeeeeeeeeeeeeeeeeeeeeeeeee')
        for line in self:
            if line.payment_request_id.request_currency == line.currency_id.id:
                if line.request_amount > line.budget_balance:
                    print('________________________________total',line.request_amount)
                    raise ValidationError(_('Requested Amount should be less than or equal to Bugdet Balance'))  
            else:
                print("\n\n\n\n\n\n\n\n")
                print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
                request_amount = 0
                budget_amount_company_currency = 0
                request_amount = line.request_amount / line.payment_request_id.request_currency.rate 
                budget_amount_company_currency = line.budget_balance / line.currency_id.rate
                if request_amount > budget_amount_company_currency:
                    print('________________________________total_currency',budget_amount_company_currency)
                    raise ValidationError(_('Requested Amount should be less than or equal to Bugdet Balance'))

    
class SrcsConfiguration(models.TransientModel):
    _inherit = "res.config.settings"

    fn_req_sg_approval = fields.Boolean(string="SG Approval",
                                        config_parameter='srcs_financial_requests.fn_req_sg_approval', readonly=False)
    internal_auditor_approval = fields.Boolean(string="Internal Auditor Approval",
                                        config_parameter='srcs_financial_requests.internal_auditor_approval', readonly=False)
  
    fn_req_sg_dp_approval_amount = fields.Float(string="Maximum Amount", required=False,
                                            config_parameter='srcs_financial_requests.fn_req_sg_dp_approval_amount',
                                            readonly=False)

    