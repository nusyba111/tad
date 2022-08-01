# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import pytz
from datetime import datetime, time
# from dateutil.rrule import rrule, DAILY
# from random import choice
# from string import digits
# from werkzeug.urls import url_encode
# from dateutil.relativedelta import relativedelta
# from collections import defaultdict

from odoo import api, fields, models, _
# from odoo.osv.query import Query
from odoo.exceptions import ValidationError, AccessError, UserError
# from odoo.osv import expression
# from odoo.tools.misc import format_date
# import date
import datetime


class CarsWarning(models.Model):
    _name = "cars.warning"
    _description = "Cars Warning"
    _rec_name = "doc_num"

    doc_num = fields.Char(string='Doc No', copy=False, readonly=True, )
    car_cont = fields.Many2one('car.contract')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    driver_name = fields.Many2one('hr.employee', string='Driver Name')
    line = fields.Many2one('adding.worker.to.transport.line', string='Transportation destination',
                           domain="[('line_name', '!=', False)]", )
    total_monthly_amount = fields.Float(string='Total Monthly Amount', related='car_cont.monthly_fees')
    deduction_amount = fields.Integer(compute='_compute_deduction', string='Deduction Amount', store=True)
    warning_reason = fields.Selection([('late', 'Repeating Lateness'), ('absent', 'Repeating Absence')],
                                      string='Warning Reason', required=True)
    deduction_type = fields.Selection(
        [('full', 'Full Day'), ('half Day', 'Half Day'), ('specify amount', 'Specify Amount'),
         ('rent allowance', 'Rent Allowance')],
        string='Deduction Type',
        required=True)
    date = fields.Date('Date')
    notes = fields.Text('Notes')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('done', 'Approve by Administration Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    total_warning = fields.Integer(string='total warning', compute='compute_total_warning')

    @api.onchange('total_monthly_amount')
    def compute_total_warning(self):
        self.total_warning = 0
        for rec in self:
            # rec.total_warning = 0
            total_warning_count = self.env['cars.warning'].search_count([('car_no', '=', rec.car_no.id)])
            rec.total_warning = total_warning_count

    @api.onchange('total_monthly_amount', 'deduction_type')
    def _compute_deduction(self):
        for rec in self:
            if rec.deduction_type == 'full':
                full_day = rec.total_monthly_amount / 26
                rec.deduction_amount = full_day
            elif rec.deduction_type == 'half':
                half_day = rec.total_monthly_amount / (26 * 2)
                rec.deduction_amount = half_day
            elif rec.deduction_type == 'specify_amount':
                rec.deduction_amount = rec.deduction_amount
            # elif rec.deduction_type == 'rent_allowance':
            #     rec.deduction_amount = rec.deduction_type

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'cars.warning') or 'New'
        return super(CarsWarning, self).create(vals)

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


class WarningType(models.Model):
    _name = "warning.type"
    _description = "Warning Type"

    name = fields.Char(string='Warning Type')
