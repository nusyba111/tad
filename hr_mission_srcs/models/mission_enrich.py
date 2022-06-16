# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################
from odoo import models, fields, api, _


class MissionEnrich(models.Model):
    _name = 'mission.enrich'
    mission_location = fields.Selection([('internal', 'Internal'),
                                         ('external', 'External')], required=True)

    disipline = fields.Selection([('engineer', 'Engineer'),
                                  ('technical', 'Technical'),
                                  ('nontechnical', 'Non Technical')], required=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=False)
    enrish_line = fields.One2many('mission.enrish.line', 'external_location', string='External Location',
                                  readonly=False)
    amount = fields.Float(string='Amount', required=True)

    def name_get(self):
        result = []
        for miss_loc in self:
            name = str(miss_loc.mission_location)
            result.append((miss_loc.id, name))
        return result


class MissionEnrichLine(models.Model):
    _name = 'mission.enrish.line'
    zone = fields.Selection([('a', 'A'),
                             ('b', 'B'),
                             ('c', 'C')], required=False)
    amount = fields.Float(string='Amount', required=True)
    external_location = fields.Many2one('mission.enrich', string='External Location', readonly=False)
