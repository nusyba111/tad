# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, AccessDenied
from datetime import datetime
from json import dumps

import ast
import json


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['check_followup'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res


class Move(models.Model):
    _inherit = 'account.move'

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids \
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('payment_id.check_rejected', '=', False),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True


class MoveLine(models.Model):
    _inherit = 'account.move.line'

    Check_no = fields.Char(string='Check No', redonly=False, store=True)

    # def create(self, vals):
    #     res = super(MoveLine, self).create(vals)
    #     for rec in res:
    #         # description = rec.name
    #         check_no = rec.check_no
    #         payment_id = rec.id
    #         # rec.update({'desc': description})
    #         if payment_id:
    #             rec.update({'check_no': check_no})
    #         # check_no = vals.get('check_no')
    #         # print(description,check_no,'CHECK')
    #         # if check_no and description:
    #         #     if 'Chq' not in description:
    #         #         name = 'Chq ' + check_no + ': '+ description
    #         #         rec.update({'name':name})
    #     return res
   
    @api.model
    def compute_amount_fields(self, amount, src_currency, company_currency, invoice_currency=False):
        """ Method kept for compatibility reason """
        return self._compute_amount_fields(amount, src_currency, company_currency)

    @api.model
    def _compute_amount_fields(self, amount, src_currency, company_currency):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = False
        currency_id = False
        if src_currency and src_currency != company_currency:
            amount_currency = amount
            amount = src_currency.with_context(self._context).compute(amount, company_currency)
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        return debit, credit, amount_currency, currency_id


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    amount_sdg = fields.Monetary('Amount In SDG',compute="_compute_amount_sdg", currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    # check_type = fields.Selection([('direct', 'Direct'), ('indirect', 'indirecting')], 'Check type', default='direct')
    check_type = fields.Selection([('direct', 'Direct'), ('indirect', 'PDC')], string="Check Type",
                                  default='direct')
    check_rejected = fields.Boolean(string="Check Rejected", readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
    payment_method_code = fields.Char(related='payment_method_id.code')
    return_check_move_id = fields.Many2one('account.move', 'Check clearance move', readonly=True)
    clearance_date = fields.Date('Check Clearance Date')
    ####################################################
    # check_line_ids = fields.One2many('account.payment.check.line', 'payment_id', 'Check(s)')
    check_ids = fields.One2many('check_followups.check_followups', 'payment_id', 'Check(s)')
    partner_bank_account = fields.Many2one('partner.bank.account', 'Partner Account', store=False)
    Account_No = fields.Char(string='Account No')
    Check_no = fields.Char('Check No')
    Bank_id = fields.Char(string='Partner Bank')
    check_date = fields.Date('Check Date')
    check_amount_in_words = fields.Char('Amount In Words')

    @api.depends('amount')
    def _compute_amount_sdg(self):
        for rec in self:
            if rec.amount:
                rec.amount_sdg = rec.amount / rec.currency_id.rate
            else:
                rec.amount_sdg = 0

    # def create(self, vals):
    #     res = super(AccountPayment, self).create(vals)
    #     for rec in res:
    #         # description = rec.name
    #         check_no = rec.check_no
    #         payment_id = rec.id
    #         # rec.update({'desc': description})
    #         if payment_id:
    #             rec.update({'check_no': check_no})
    #         # check_no = vals.get('check_no')
    #         # print(description,check_no,'CHECK')
    #         # if check_no and description:
    #         #     if 'Chq' not in description:
    #         #         name = 'Chq ' + check_no + ': '+ description
    #         #         rec.update({'name':name})
    #     return res
    @api.depends('move_id.line_ids.amount_residual', 'move_id.line_ids.amount_residual_currency',
                 'move_id.line_ids.account_id')
    def _compute_reconciliation_status(self):
        ''' Compute the field indicating if the payments are already reconciled with something.
        This field is used for display purpose (e.g. display the 'reconcile' button redirecting to the reconciliation
        widget).
        '''
        for pay in self:
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
            if not pay.currency_id or not pay.id:
                pay.is_reconciled = False
                pay.is_matched = False
            elif pay.currency_id.is_zero(pay.amount):
                pay.is_reconciled = True
                pay.is_matched = True
            else:
                residual_field = 'amount_residual' if pay.currency_id == pay.company_id.currency_id else 'amount_residual_currency'
                if pay.journal_id.default_account_id and pay.journal_id.default_account_id in liquidity_lines.account_id:
                    # Allow user managing payments without any statement lines by using the bank account directly.
                    # In that case, the user manages transactions only using the register payment wizard.
                    pay.is_matched = True
                elif pay.payment_method_code == 'check_followup' and all(
                        check.state in ['donev', 'donec'] for check in pay.check_ids):
                    pay.is_matched = True
                else:
                    pay.is_matched = pay.currency_id.is_zero(sum(liquidity_lines.mapped(residual_field)))

                reconcile_lines = (counterpart_lines + writeoff_lines).filtered(lambda line: line.account_id.reconcile)
                pay.is_reconciled = pay.currency_id.is_zero(sum(reconcile_lines.mapped(residual_field)))

    # Modify indirecting account to be direct
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
        if self.check_type != 'indirect' or not self.check_type:
            res[0].update({'account_id': self.journal_id.default_account_id.id})
        if self.check_type:
            res[0].update({'Check_no':self.Check_no})
            res[1].update({'Check_no':self.Check_no})
            print('________________check',self.Check_no)
        return res

    # Modify move when check_type change
    def _synchronize_to_moves(self, changed_fields):
        for rec in self:
            res = super(AccountPayment, self)
            res._synchronize_to_moves(changed_fields)
            if any(field_name in changed_fields for field_name in (
                    'check_type', 'payment_method_id')):
                for pay in res.with_context(skip_account_move_synchronization=True):
                    liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
                    line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=None)
                    line_ids_commands = [(1, liquidity_lines.id, line_vals_list[0])]
                    pay.move_id.write({
                        'line_ids': line_ids_commands,
                    })
        return res

    ######################################
    @api.onchange('amount', 'currency_id')
    def _compute_amount_in_words(self):
        from . import money_to_text_ar
        for r in self:
            r.check_amount_in_words = money_to_text_ar.amount_to_text_arabic(r.amount, r.currency_id.name)

    @api.returns('check_followups.check_followups')
    def _create_check(self):
        self.ensure_one()
        for rec in self:
            # if self.payment_type == 'outbound':
            check_dict = {
                'payment_id': rec.id,
                'type': rec.payment_type,
                'amount': rec.amount,
                'Date': rec.check_date,
                'bank_id': False,
                'partner_bank': rec.Bank_id,
                # 'check_no': rec.Check_no,
                'check_no': rec.Check_no,
                'currency_id': rec.currency_id.id,
                'communication': rec.ref,
                'company_id': rec.company_id.id,

            }
            log_args = {
                'Move_id': rec.move_id.id,
                'payment_id': rec.id,
                'date': rec.date,
            }
            if rec.payment_type == 'inbound':
                check_dict.update({
                    'state': 'under_collection',
                })

                log_args.update({
                    'Description': 'Customer Check Creation',
                })
            elif rec.payment_type in ['outbound', 'transfer']:
                check_dict.update({
                    'state': 'out_standing',
                    'bank_id': rec.journal_id.bank_id.id,
                })
                log_args.update({
                    'Description': 'Vendor Check Creation',
                })

            check = self.env['check_followups.check_followups'].create(check_dict)
            rec.payment_reference = check.name
            check.WriteLog(**log_args)
        return check

    def action_post(self):
        for r in self:
            inbound_check = r.env.ref('ii_simple_check_management.account_payment_method_check_in')
            outbound_check = r.env.ref('ii_simple_check_management.account_payment_method_check_out')

            if r.payment_method_id in [inbound_check, outbound_check]:
                if not r._context.get('check_payment', False):
                    # no check_payment means this payment is the first payment for the check, and it is not a returning
                    # payment (returning an already existing check to customer or to us)
                    payment_context = {
                        'check_payment': True,
                        'check_last_state': False,
                    }
                    if r.payment_method_id == inbound_check:
                        payment_context.update(dict(check_state='under_collection'))
                    elif r.payment_method_id == outbound_check:
                        r.journal_id.sudo().Check_no = r.Check_no
                        payment_context.update(dict(check_state='out_standing'))

                    r = r.with_context(payment_context)
                    super(AccountPayment, r).action_post()
                    if r.check_type == 'indirect':

                        check = r._create_check()
                        for line in r.move_id.line_ids:
                            if not line.ref:
                                line.ref = check.name
                    # return
            else:
                super(AccountPayment, r).action_post()

    def action_cancel(self):
        for record in self:
            super(AccountPayment, record).action_cancel()
            if record.check_ids:

                for ch in record.check_ids:
                    print('--------ch', ch.state)
                if record.check_ids.filtered(
                        lambda check: check.state not in (
                                'out_standing', 'rdv', 'under_collection', 'rdc', 'cancel', 'return_acv',
                                'return_acc')):
                    raise UserError(_("Payment Cannot be cancelled, check should be either unused or rejected"))
                else:
                    record.check_ids.state = 'cancel'

    def action_draft(self):
        for record in self:
            super(AccountPayment, record).action_draft()
            if record.check_ids:
                if record.check_ids.filtered(
                        lambda check: check.state not in (
                                'out_standing', 'rdv', 'under_collection', 'rdc', 'cancel', 'return_acc',
                                'return_acv')):
                    raise UserError(_("Payment Cannot be rest, check should be either unused or rejected"))
                else:
                    record.check_ids.state = 'cancel'

    def action_view_checks(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        if self.payment_type == 'inbound':
            action = self.env.ref(
                'ii_simple_check_management.check_followups_customer').read()[0]
        elif self.payment_type == 'outbound':
            action = self.env.ref(
                'ii_simple_check_management.check_followups_vendor').read()[0]
        # action = self.env.ref('is_pm_az.action_contract_qty_work').read()[0]

        checks = self.mapped('check_ids')
        if len(checks) > 1:
            action['domain'] = [('id', 'in', checks.ids)]
        elif checks:
            if self.payment_type == 'inbound':
                action['views'] = [
                    (self.env.ref('ii_simple_check_management.check_followups_customerformview').id, 'form')]
            elif self.payment_type == 'outbound':
                result = self.env.ref(
                    'ii_simple_check_management.check_followups_form')
                action['views'] = [(self.env.ref('ii_simple_check_management.check_followups_form').id, 'form')]
            action['res_id'] = checks.id
        return action


class account_payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
    payment_method_code = fields.Char(related='payment_method_id.code')
    check_type = fields.Selection([('direct', 'Direct'), ('indirect', 'PDC')], string="Check Type",
                                  default='direct')
    clearance_date = fields.Date('Check Date')
    check_no = fields.Char('Check No.')
    partner_bank = fields.Char(string="Partner Bank", required=False, )

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(account_payment_register, self)._create_payment_vals_from_wizard()
        payment_vals.update(
            {
                'check_type': self.check_type,
                'check_date': self.clearance_date,
                'Check_no': self.check_no,
                'Bank_id': self.partner_bank,
            }
        )
        return payment_vals
