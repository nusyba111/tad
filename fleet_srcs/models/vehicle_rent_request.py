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

class VehicleRentRequest(models.Model):
    _name = 'fleet.rent.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_no=fields.Char('Repair No:',readonly=True)
    branch=fields.Many2one('res.branch',string='Branch')
    date=fields.Datetime('Date of Request')
    model=fields.Many2one('fleet.vehicle.model',string='Required Car Model',required=True, tracking=True)
    department=fields.Many2one('hr.department',string='Requesting Dept/Project',required=True, tracking=True)
    date_from=fields.Datetime(string='Date From',required=True,tracking=True)
    date_to=fields.Datetime(string='Date To',required=True,tracking=True)
    destination=fields.Char(string='Destination',required=True,tracking=True)
    purpose=fields.Text(string='Purpose',required=True,tracking=True)
    end_date=fields.Datetime(string='End Service Date')
    dept_approve=fields.Char(string='Department Manager Approval',tracking=True)
    date=fields.Datetime(string='Date')
    admin_approve=fields.Char(string='Admin and Gs Approval')
    date_approve=fields.Datetime(string='Date')
    partner=fields.Many2one('res.partner',string='Partner')
    contract_no=fields.Integer(string='Contract No')
    address=fields.Char(string='Address')
    add_phone=fields.Integer(string='Phone')
    car_model=fields.Many2one('fleet.vehicle',string='Car Model',required=True, tracking=True)
    plate=fields.Char(string='License Plate',related='car_model.license_plate')
    date_make=fields.Datetime(string='Make Date')
    fuel_type=fields.Many2one('product.product',string='Fuel Type')
    fuel_amount=fields.Float(string='Fuel Amount')
    leave_date = fields.Datetime(string='Leaving Date')
    back_date=fields.Datetime(string='Back Date')
    days_no=fields.Float(string='No of Days')
    lease_amount=fields.Float(string='Lease Price')
    invoice_no=fields.Many2one('account.move',string='Invoice No')
    invoice_amount=fields.Float(string='Invoice Amount')
    driver=fields.Many2one('res.partner',string='Driver')
    phone=fields.Char('Driver Phone')
    employee=fields.Many2one('hr.employee',string='Admin Employee')
    date_sig=fields.Date('Date')
    requested_days=fields.Float('Requested Days')
    actual_days=fields.Float('Actual Days')
    actual_amount=fields.Float('Actual Amount')
    contract_count=fields.Integer(string='Contracts', compute='_compute_contract_ids',tracking=True)

    def _compute_contract_ids(self):
        for rec in self:
            picking_ids = self.env['fleet.vehicle.log.contract'].search([('rent_id', '=', self.id)])
            rec.contract_count = len(picking_ids)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('fleet_manager','Direct Manager Approve'),
        ('admin_manager','HR Manager Approve'),
        ('manager','Direct Manager'),
        ('operation','Operation Manager'),
        ('cancel','Cancel'),
        ('done', 'Done')], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.model
    def create(self, vals):
        repair = super(VehicleRentRequest, self).create(vals)
        for x in repair:
            x.request_no = self.env['ir.sequence'].next_by_code('request.no')
        return repair

    def to_fleet_manager(self):
        self.write({'state': 'fleet_manager'})
    def to_admin_manager(self):
        self.write({'state': 'admin_manager'})
    def to_manager(self):
        contract_vals = {
            'user_id': self.employee.user_id.id,
            'vehicle_id': self.car_model.id,
            'insurer_id': self.partner.id,
            'cost_generated': self.lease_amount,
            'start_date':self.date_from,
            'expiration_date':self.date_to,
            'rent_id':self.id,
        }
        invoice = self.env['fleet.vehicle.log.contract'].sudo().create(contract_vals)

        self.write({'state': 'manager'})
    def to_operation_manager(self):
        self.write({'state': 'operation_manager'})
    def action_cancel(self):
        self.write({'state': 'cancel'})
    def action_done(self):
        self.write({'state': 'done'})


class Contracts(models.Model):
    _inherit = "fleet.vehicle.log.contract"

    rent_id = fields.Many2one('fleet.rent.request', 'Rent Reference')