from odoo import fields, api, models, _

class custody_clearance(models.Model):
    _name = 'custody.clearance'
    _description = 'A model for tracking custody clearance.'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'clearance_no'
    _order = 'id desc'

    clearance_no = fields.Char('Clearance No.', help='Auto-generated Clearance No. for custody clearances')
    # name = fields.Char('Details', compute='_get_description', store=True, readonly=True)
    cc_date = fields.Date('Date', default=fields.Date.today(), )
    requester = fields.Char('Requester', required=True, default=lambda self: self.env.user.name)
    is_partially_clearance = fields.Boolean(string="Partially Clearance", )
    payment_request_id = fields.Many2one('payment.request', 'Payment Request',domain="[('state', '=', 'payment'),('is_cleared','=',False),('user_id','=',requester),('is_working_addvance','=',True)]")
    branch_laons_id = fields.Many2one('cash.request', 'Branch Loan', domain="[('is_branch_loans','=',True),('state', '=', 'payment'),('user_id','=',requester),('is_cleared','=',False)]")
    is_branch_loans = fields.Boolean('Is Branch Loans')
    # clearance_amount_new = fields.Float(compute='approval_reference', string='Requested Amount', store=True, )
    requested_amount = fields.Float('Requested Amount', readonly=True)
    un_cleared_amount = fields.Float('Uncleared Amount', readonly=True)
    clearance_amount = fields.Float('Clearance Amount', required=True)
    clearance_currency = fields.Many2one('res.currency', 'Currency')
    # difference_amount = fields.Float('Difference Amount', readonly=True, compute='compute_tot_cleared_amount')
    # clearance_amount_words = fields.Char(string='Amount in Words', readonly=True, default=False, copy=False,
    #                                      compute='_compute_text', translate=True)
    reason = fields.Char('Reason')
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'),
                              ('fm_app', 'Financial Approval'),
                              ('gm_app', 'General Manager Approval'),
                              ('reject', 'Rejected'),
                              ('validate', 'Validated')],
                             string='Custody Clearance Status', default='draft', track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', 'Bank/Cash Journal',
                                 help='Payment journal.',
                                 domain=[('type', 'in', ['bank', 'cash'])])
    clearance_journal_id = fields.Many2one('account.journal', 'Clearance Journal', help='Clearance Journal')
    cr_account = fields.Many2one('account.account', string="Credit Account")
    pay_from = fields.Many2one('res.partner', string='Pay From')
    move_id = fields.Many2one('account.move', 'Clearance Journal Entry', readonly=True, copy=False)

    # overriding create to save number with commit
    @api.model
    def create(self, vals):
        res = super(custody_clearance, self).create(vals)
        # get custody clearance sequence no.
        next_seq = self.env['ir.sequence'].get('custody.clearance.sequence')
        res.update({'clearance_no': next_seq})
        return res

    @api.onchange('payment_request_id','branch_laons_id')
    def _onchange_payment_request_id_branch_laons_id(self):
        for rec in self:
            if rec.payment_request_id:
                rec.requested_amount = rec.payment_request_id.total_amount
                rec.clearance_currency = rec.payment_request_id.request_currency.id
                rec.reason = rec.payment_request_id.reason
                rec.journal_id = rec.payment_request_id.journal_id.id
                rec.cr_account = rec.payment_request_id.pay_to.property_account_receivable_id.id 
                rec.pay_from = rec.payment_request_id.pay_to.id
                rec.un_cleared_amount = rec.requested_amount

            if rec.branch_laons_id:
                rec.requested_amount = rec.branch_laons_id.requested_amount
                rec.clearance_currency = rec.branch_laons_id.currency_id.id
                rec.reason = rec.branch_laons_id.description
                rec.journal_id = rec.branch_laons_id.source_bank.id
                rec.clearance_journal_id = rec.branch_laons_id.dest_bank.id
                rec.un_cleared_amount = rec.requested_amount


    def clear(self):
        entrys = []
        for cl in self:
            if cl.payment_request_id:
                credit_account = cl.cr_account.id
                dedit_account = cl.journal_id.default_account_id.id
    
            if cl.branch_laons_id:
                credit_account = cl.clearance_journal_id.default_account_id.id
                dedit_account = cl.journal_id.default_account_id.id
                
            debit_val = {
                'name': cl.reason,
                # 'partner_id': self.partner_id.id,
                'account_id': dedit_account,
                'debit': cl.clearance_amount,
                # 'analytic_account_id': line1.analytic_account_id.id,
                # 'company_id': self.company_id.id,
            }
            entrys.append((0, 0, debit_val))
            credit_vals = {
                'name': cl.reason,
                # 'partner_id': False,
                'account_id': credit_account,
                'credit':  cl.clearance_amount,
                # 'company_id': self.company_id.id,
            }
            entrys.append((0, 0, credit_vals))
            
            vals = {
                'journal_id': cl.journal_id.id,
                'date': cl.cc_date,
                'ref': cl.clearance_no,
                'move_type':'entry',
                # 'company_id': self.company_id.id,
                'line_ids': entrys
            }
            move = cl.env['account.move'].create(vals)
            cl.move_id = move
            if cl.payment_request_id: 
                cl.payment_request_id.is_cleared = True
            if cl.branch_laons_id:
                cl.branch_laons_id.is_cleared = True

