# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################
from odoo import models, fields, api, _


class HrMissionType(models.Model):
    _name = 'hr.mission.type'
    
    name = fields.Char(required=True,string="Name",track_visibility='onchange')
    type = fields.Selection([('internal', 'Internal'),
                                  ('external', 'External')],string= "Type",track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency',track_visibility='onchange', default=lambda self: self.env.user.company_id.currency_id.id)
    Per_Dem = fields.Selection([('fix_amount', 'Fix amount'),
                             ('fix_job', 'Fix amount per job '),('formula', 'Formula')], default="fix_amount",string="Per-Dem", track_visibility='onchange')
    amount = fields.Float(string='Amount', required=True,track_visibility='onchange')
    amount_job_id = fields.One2many('hr.mission.type.line','mission_type_line_id',track_visibility='onchange')
    formula = fields.Many2one('hr.salary.rule',track_visibility='onchange')



class MissionEnrichLine(models.Model):
    _name = 'hr.mission.type.line'

    mission_type_line_id = fields.Many2one('hr.mission.type', 'Mission Type')
    amount = fields.Float(string='Amount', required=True,track_visibility='onchange')
    job_id = fields.Many2one('hr.job', string='HR Job',track_visibility='onchange')
