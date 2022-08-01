# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import pytz
# from datetime import datetime, time
# from dateutil.rrule import rrule, DAILY
# from random import choice
# from string import digits
# from werkzeug.urls import url_encode
# from dateutil.relativedelta import relativedelta
# from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from datetime import datetime

# from odoo.osv.query import Query
from odoo.exceptions import ValidationError, AccessError, UserError


# from odoo.osv import expression
# from odoo.tools.misc import format_date
# import date


class TransportationCarsAttendance(models.Model):
    _name = "transportation.cars.attendance"
    _description = "Transportation line Request"
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', copy=False, readonly=True, )
    date = fields.Date(string='Date')
    cars_transport_list_ids = fields.One2many('transportation.cars.attendance.line', 'transportation_car_attendance_id',
                                              string='Employee Transport List')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", )
    # is_driver = fields.Boolean(related='car_no.is_company_car')
    # is_owner = fields.Boolean(related='car_no.is_outsource_car')
    # print(is_driver)
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'car.att') or 'New'
        return super(TransportationCarsAttendance, self).create(vals)


class TransportationCarsAttendanceLine(models.Model):
    _name = "transportation.cars.attendance.line"
    _description = "transportation cars attendance line"

    fleet = fields.Many2one('fleet.vehicle')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", )
    absent_reasons = fields.Many2one('car.status', string='absent reasons', )
    transport_line_id = fields.Many2one('transportation.line.request', string='Line', )
    transportation_car_attendance_id = fields.Many2one('transportation.cars.attendance',
                                                       string='Transportation line Request')
    attend_time = fields.Float(string='Attend Time')
    leave_time = fields.Float(string='Leave Time')
    driver_name = fields.Char(string='Driver Name', related='car_no.employee_id.name', )
    car_owner = fields.Char(related='car_no.car_owner.name', string='Car Owner Name')
    is_driver = fields.Boolean(related='car_no.is_company_car')
    is_owner = fields.Boolean(related='car_no.is_outsource_car')
    notes = fields.Text(string='Notes')

    @api.onchange('cars_transport_list_ids')
    def car_no_owner(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
