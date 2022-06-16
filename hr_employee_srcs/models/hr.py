# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    code = fields.Char(string="Code")
    signature = fields.Char(string="Signature")
    cv = fields.Binary(string="Employee CV")
    medical_isurance = fields.Char(string="Medical Insurance")
    medical_report = fields.One2many('ir.attachment','emp_id')



class IRAttachment(models.Model):
    _inherit = 'ir.attachment'


    emp_id = fields.Many2one('hr.employee')    

