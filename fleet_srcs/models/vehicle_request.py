# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################
from datetime import timedelta


from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, AccessError
from collections import defaultdict
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare, get_lang, format_date

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS

class VehicleRequest(models.Model):
    _name = 'fleet.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'request_no'

    request_no=fields.Char('Repair No:',readonly=True)
    branch=fields.Many2one('res.branch',string='Branch')
    employee=fields.Many2one('hr.employee',string='Employee',required=True, tracking=True)
    department=fields.Many2one('hr.department',string='Department',required=True, tracking=True)
    date_from=fields.Datetime(string='Date From',required=True,tracking=True)
    date_to=fields.Datetime(string='Date To',required=True,tracking=True)
    purpose=fields.Text(string='Purpose',required=True,tracking=True)
    car=fields.Many2one('fleet.vehicle',string='Car')
    licence_plate=fields.Char(string='License Plate',related='car.license_plate')
    mission=fields.Boolean(string='Mission?')
    fund=fields.Many2one('res.partner',string='Fund')
    driver=fields.Many2one('res.partner',string='Driver', related='car.driver_id')
    recommndation=fields.Text(string='Fleet Manager Recommendation')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('direct_manager','Direct Manager Approve'),
        ('hr_manager','HR Manager Approve'),
        ('fleet','Fleet Manager Approve'),
        ('cancel','Cancel'),
        ('done', 'Done')], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.model
    def create(self, vals):
        repair = super(VehicleRequest, self).create(vals)
        for x in repair:
            x.request_no = self.env['ir.sequence'].next_by_code('request.no')
        return repair

    def to_direct_manager(self):
        self.write({'state': 'direct_manager'})
        template_rec = self.env.ref('fleet_srcs.new_task')
        template_rec.write({'email_to': self.driver.email})
        template_rec.send_mail(self.id, force_send=True)

    def to_hr_manager(self):
        self.write({'state': 'hr_manager'})
    def to_fleet(self):
        self.write({'state': 'fleet'})
    def action_cancel(self):
        self.write({'state': 'cancel'})
    def action_done(self):
        self.write({'state': 'done'})

