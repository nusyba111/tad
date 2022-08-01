# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class CarFuelCalculation(models.Model):
    _name = 'car.fuel.calculation'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'car fuel calculation'

    doc_num = fields.Char(string='Doc No', copy=False)
    fuel = fields.Many2one('car.fuel', )
    date = fields.Date(string='Date')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    line = fields.Many2one(string='Transportation Destination', related='fuel.line')
    driver_name = fields.Char(string='Driver Name', related='car_no.employee_id.name', )
    normal_fuel_qty = fields.Float(string='Normal Fuel QTY', )
    # related='fuel.normal_fuel_qty')
    total_normal_fuel = fields.Float(string='Total Normal Fuel', related='fuel.total_normal_fuel')
    normal_fuel_price = fields.Float(string='Normal Fuel Price', related='fuel.normal_fuel_price')
    fuel_ids = fields.One2many('car.fuel.info', 'fuel_id', string='Fuel Details')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('done', 'Approve by Administration Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('car_no')
    def car_normal_fuel_qty(self):
        for rec in self:
            normal_fuel_qty = rec.fuel.normal_fuel_qty
            print(normal_fuel_qty, '::::::::::::::::::::::;')

    @api.onchange('normal_fuel_qty', 'normal_fuel_price')
    def _total_normal(self):
        for rec in self:
            rec.total_normal_fuel = rec.normal_fuel_qty * rec.normal_fuel_price

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_done(self):
        return self.write({'state': 'done'})

    # @api.model
    # def create(self, vals):
    #     vals['doc_num'] = self.env['ir.sequence'].next_by_code(
    #         'car.fuel.cal.seq') or 'New'
    #     return super(CarFuelCalculation, self).create(vals)

# class CarFuelDeductionInfo(models.Model):
#     _name = 'car.fuel.info'
#
#     fuel_id = fields.Many2one('car.fuel', )
#     car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
#     fuel_date = fields.Date(string='date')
#     amount = fields.Float(string='amount')
