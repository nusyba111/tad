# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from odoo import fields, models,api,_

class wizardMission(models.TransientModel):
    _name = 'wizard.mission'
    description = fields.Char(string='Reason', required=True)
        
    def wizard_mission(self):
        if self._context.get('active_model') == 'hr.mission':
            rec = self.env['hr.mission'].browse(self._context.get('active_ids', []))
            rec.write({'reason': self.description})
            if self._context.get("cancel") == True:
                rec.write({'state': 'canceled'})
            elif  self._context.get("draft") == True:
                rec.write({'state': 'draft'})
            

