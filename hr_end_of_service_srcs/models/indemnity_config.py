# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IndemnityConfig(models.Model):
    _name = 'indemnity.config'
    _rec_name = 'date'

    date = fields.Date(string="Date", required=False, default=fields.Date.context_today)

    indemnity_config_ids = fields.One2many(comodel_name="indemnity.config.line",
                                           inverse_name="indemnity_config_id", string="", required=False, )


class IndemnityConfigLine(models.Model):
    _name = 'indemnity.config.line'

    from_year = fields.Integer(string="From Year", required=False, )
    to_year = fields.Integer(string="To Year", required=False, )
    month_count = fields.Selection(string="Months Count",
                                   selection=[
                                       ('1', '1'),
                                       ('2', '1.5'),
                                       ('3', '2'),
                                       ('4', '2.5'),
                                       ('5', '3'),
                                   ], required=False, )
    indemnity_config_id = fields.Many2one(comodel_name="indemnity.config", string="", required=False, )
