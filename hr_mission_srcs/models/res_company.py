# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2018-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    mission_journal_id = fields.Many2one('account.journal', string="Journal")
    mission_account_id = fields.Many2one('account.account', string='Account')
