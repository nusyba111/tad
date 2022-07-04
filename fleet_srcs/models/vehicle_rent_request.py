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
    _rec_name = 'request_no'

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
    new_odometer=fields.Float('New Odometer')
    kilo_price=fields.Float('Kilo Price')
    total=fields.Float('Total Amount',compute='compute_total')
    type = fields.Selection([('short','Short Rent'),('long','Long Rent')] , string='Rent Type',required=True)
    invoice_type = fields.Selection([('day','By Day'),('kilo','By Kilometer')] , string='Invoicing Type',required=True)
    contract_count=fields.Integer(string='Contracts', compute='_compute_contract_ids',tracking=True)
    no_days=fields.Float('No.Days',tracking=True)
    day_price=fields.Float('Day Price',tracking=True)
    odometer=fields.Float('Odometer',required=True,tracking=True)
    handover_id=fields.One2many('handover','rent_id',string='Handover')
    service = fields.Many2one('product.product',string='Service',required=True,domain=[('detailed_type','=','service')])
    invoice_reference=fields.Many2one('account.move',string='Invoice Reference')

    @api.depends('kilo_price','new_odometer')
    def compute_total(self):
        odo=self.new_odometer - self.odometer
        self.total=self.kilo_price*odo

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
        ('on_rent','On Rent'),
        ('handover','Handover'),
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
        if self.car_model.on_rent == True:
            raise ValidationError(_('Car is already On Rent'))
        else:
            self.write({'state': 'admin_manager'})

    def to_manager(self):
        if self.car_model.on_rent == True:
            raise ValidationError(_('Car is already On Rent'))
        else:
            self.write({'state': 'manager'})

    def to_operation_manager(self):
        self.write({'state': 'operation'})
    def to_rent(self):
        if self.car_model.on_rent == True:
            raise ValidationError(_('Car is already On Rent'))
        else:
            if self.invoice_type=='day':
                invoice_vals = {
                    'partner_id': self.partner.id,
                    'invoice_date': self.date_from,
                    'rent_id': self.id,
                    'invoice_line_ids': [0, 0, {
                        'product_id': self.service,
                        'quantity': 1,
                        'price_unit': self.invoice_amount,
                    }]
                }
                invoice = self.env['account.move'].sudo().create(invoice_vals)
                self.invoice_reference = invoice
                self.car_model.write({'on_rent':True})
                self.write({'state': 'on_rent'})
            else:
                self.write({'state': 'on_rent'})
    def handover(self):
        self.write({'state': 'handover'})

    def create_invoice(self):
        invoice_vals = {
            'partner_id': self.partner.id,
            'invoice_date': self.date_from,
            'rent_id': self.id,
            'invoice_line_ids': [0, 0, {
                'product_id': self.service,
                'quantity': 1,
                'price_unit': self.invoice_amount,
            }]
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)
        self.invoice_reference=invoice

    def action_cancel(self):
        self.write({'state': 'cancel'})
    def action_done(self):
        self.write({'state': 'done'})


class Contracts(models.Model):
    _inherit = "fleet.vehicle.log.contract"

    rent_id = fields.Many2one('fleet.rent.request', 'Rent Reference')

class Invoice(models.Model):
    _inherit = "account.move"

    rent_id = fields.Many2one('fleet.rent.request', 'Rent Reference')



class RentPolicy(models.Model):
    _name='rent.policy'
    type = fields.Selection([('short','Short Rent'),('long','Long Rent')],string='Rent Type',required=True)
    name=fields.Text('Policy Name',required=True)

class HandOver(models.Model):
    _name = 'handover'

    rent_id=fields.Many2one('fleet.rent.request',string='HandOver')
    question=fields.Many2one('rent.handover',string='Checklist')
    checked=fields.Boolean('Done')

class RentHandver(models.Model):
    _name = 'rent.handover'

    sequence=fields.Integer('Sequence')
    name=fields.Char('Check List')
