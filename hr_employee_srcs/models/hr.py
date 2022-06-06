# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    code = fields.Char(string="Code")
    signature = fields.Char(string="Signature")

