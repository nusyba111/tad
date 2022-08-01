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


class TransportationLineRequest(models.Model):
    _name = "transportation.line.request"
    _description = "Transportation line Request"
    _rec_name = "destination"

    doc_num = fields.Char(string='Doc No', copy=False, readonly=True, )
    requester = fields.Many2one('hr.employee', string='Requester')
    department = fields.Char(string='Department', related='requester.department_id.name')
    date_time = fields.Date('Date')
    destination = fields.Char('Destination', )
    new_destination = fields.Char('New Destination')
    current_destination = fields.Many2one('destination.name', string='Current Destination',
                                          domain="[('destination_name', '!=', False)]")
    employee_transport_list_ids = fields.One2many('employee.transport.list', 'transportation_line_request_id',
                                                  string='Employee Transport List')
    line_type = fields.Selection(
        [('new', 'New'),
         ('extension', 'Extension')],
        string='Line Type', required=True)
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Requester'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('approve2', 'Approve by Admin Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')
    reason_adding_extending = fields.Text(string='Reason for Adding or Extending Line')

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'transportation.line.request') or 'New'
        return super(TransportationLineRequest, self).create(vals)

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_approve2(self):
        return self.write({'state': 'approve2'})

    def action_done(self):
        return self.write({'state': 'done'})


class EmployeeTransportList(models.Model):
    _name = "employee.transport.list"
    _description = "Transportation line Request"

    employee = fields.Many2one('hr.employee', string='Name')
    department = fields.Char(string='Department', related='employee.department_id.name')
    transportation_line_request_id = fields.Many2one('transportation.line.request',
                                                     string='Transportation line Request')
    adding_transport_line_request_id = fields.Many2one('adding.worker.to.transport.line',
                                                       string='Adding Transportation line Request')
    position = fields.Char(string='Position', related='employee.job_title')
    phone_number = fields.Char(string='Phone Number', related='employee.phone')
    address = fields.Char(string='Address', related='employee.home_address')
