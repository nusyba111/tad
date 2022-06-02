# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import models, fields, api, _


class FleetContractCustom(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    # ## page Finance codes #
    account = fields.Many2one('account.account', 'Account')
    project = fields.Many2one('account.analytic.account', 'Project')
    activity = fields.Many2one('account.analytic.account', 'Activity')
    m_code = fields.Char('M code')
    is_check = fields.Boolean('Is check')

    # create invoice
    def btn_create_invoice(self):
        # form values (data will pass to account.move)
        for rec in self:
            invoice = rec.env['account.move'].create({
                'move_type': 'out_invoice',  #
                'partner_id': self.insurer_id.id,  # purchaser_id
                'name': self.name,
                'invoice_date': self.date,
                'currency_id': self.env.ref('base.SDG').id,
                'payment_reference': 'invoice to client',
                'contract_id': self.id,

                # line values,data pass to (account.move.line)
                'invoice_line_ids': [(0, 0, {
                    'quantity': 1,
                    'price_unit': self.amount,
                    'date': self.date,
                    'partner_id': self.insurer_id.id,
                    'name': self.name,  # sequence of invoice is contract name
                })],
            })
            rec.is_check = True
        return invoice

    def open_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('contract_id', '=', self.id)]
        return action
        # for rec in self:
        #     rec.ensure_one()
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': _('Fleet invoice'),
        #         'res_model': 'account.move',
        #         'view_mode': 'form',
        #         'target': 'new',
        #         'res_id': self.id,
        #         'context': {'active_model': 'account.move',
        #                     'active_ids': self.ids},
        #     }


class Conn(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one('fleet.vehicle.log.contract', readonly=True)  # inverse conn invoice line
