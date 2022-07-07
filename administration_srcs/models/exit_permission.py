# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import models, fields, api, _


class ExitPermission(models.Model):
    _name = 'exit.permission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Create an Exit Form'
    _rec_name = 'sequence'
    _order = "date,state desc"

    sequence=fields.Char(readonly=True)
    date=fields.Datetime(string='Date',required=True, tracking=True)
    address_to=fields.Many2one('res.partner',string='Address To',required=True, tracking=True)
    employee_id=fields.Many2one('hr.employee',string='Employee Name',required=True, tracking=True)
    department=fields.Many2one('hr.department',string='Department',related='employee_id.department_id')
    asset=fields.Many2one('account.asset',string='Asset Name',required=True, tracking=True)
    from_dept=fields.Many2one('hr.department',string='Come-In(From/To)',related='employee_id.department_id')
    to_dept=fields.Many2one('hr.department',string='Issued(From/To)',related='employee_id.department_id')
    responsible_comment=fields.Text(string='Asset Responsible Comment')
    admin_comment=fields.Text(string='Administration Comment')
    reception_comment=fields.Text(string='Reception Comment')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admin', 'Administration Approve'),
        ('cancel', 'Cancel'),
        ('done', 'Done')], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    @api.model
    def create(self, vals):
        exit = super(ExitPermission, self).create(vals)
        for x in exit:
            x.sequence = self.env['ir.sequence'].next_by_code('exit.no')
        return exit

    def to_admin(self):
        self.write({'state': 'admin'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_done(self):
        self.write({'state': 'done'})




