from odoo import fields, models, api, _

class SrcsPaymentRequest(models.Model):
    _rec_name = 'sequence'
    _name = "payment.request"

    sequence = fields.Char(string='Sequence', readonly=True, copy=False, index=True,
                           default=lambda self: 'New Payment Request')
    date = fields.Date('Request Date',default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='Requestor', default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Journal')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    pay_to = fields.Many2one('res.partner', string='Pay To')
    payment_method = fields.Selection([
        ('cash', 'Cash'),('bank','Bank Transfer'),('check','Check'),
    ], string='Method of Payment')
    total_amount = fields.Float('Total Amount')
    budget_line_ids = fields.One2many('payment.request.lines', 'payment_request_id', string='Budget Lines')
    
    @api.model
    def create(self, vals):
        if vals.get('sequence', 'NEW') == 'NEW':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('payment.request') or 'NEW'
        result = super(SrcsPaymentRequest, self).create(vals)
        return result

class SrcsPaymentLines(models.Model):
    _name = "payment.request.lines"

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    donor_id = fields.Many2one('res.partner', string='Donor', required=True)
    project_id = fields.Many2one('account.analytic.account',string='Project', domain="[('type','=','project')]")
    account_id = fields.Many2one('account.account', string='Account')
    analytic_activity_id = fields.Many2one('account.analytic.account', 'Output/Activity', domain="[('type','=','activity')]")
    payment_request_id = fields.Many2one('payment.request', string='Payment Request')
    request_amount = fields.Float('Requested Amount', required=True)
    budget_balance = fields.Float(compute="_compute_buget_balance", string='Budget Balance')

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
            else:
                rec.budget_balance = 0