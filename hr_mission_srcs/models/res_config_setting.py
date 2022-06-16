# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2018-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from odoo import api, fields, models, _


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mission_journal_id = fields.Many2one('account.journal', string="Journal", related='company_id.mission_journal_id',
                                         readonly=False)
    mission_account_id = fields.Many2one('account.account', string='Account', related='company_id.mission_account_id',
                                         readonly=False)
