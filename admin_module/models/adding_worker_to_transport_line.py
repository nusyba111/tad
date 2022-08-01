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


class AddingWorkerTransportLine(models.Model):
    _name = "adding.worker.to.transport.line"
    _description = "Adding Worker to Transport Line"
    _rec_name = "line_name"

    doc_num = fields.Char(string='Doc No', copy=False, readonly=True, )
    requester = fields.Many2one('hr.employee', string='Requester')
    department = fields.Char(string='Department', related='requester.department_id.name')
    date_time = fields.Date('Date')
    line_name = fields.Many2one('transportation.line.request', string='Line Name',
                                domain="[('destination', '!=', False)]")
    line_select = fields.Many2one('transportation.line.request', string='Select Line',
                                  domain="[('destination', '!=', False)]"
                                  )
    previous_address = fields.Char(string='Previous Address')
    current_address = fields.Char(string='Current Address')
    adding_transport_list_ids = fields.One2many('employee.transport.list', 'adding_transport_line_request_id',
                                                string='adding Transport List')
    addition_type = fields.Selection(
        [('new_worker', 'New Worker'),
         ('change_address', 'Change Address')],
        string='Addition Type', required=True)
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Requester'),
                                        ('approve', 'Approve by Services Section Head'),
                                        ('done', 'Approve by Administration Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('line_name')
    def all_workers(self):
        for rec in self:
            rec.adding_transport_list_ids = [(5, 0, 0)]
            counter = 0
            line_id = self.env['transportation.line.request'].search([('id', '=', self.line_name.id)])
            if line_id:
                emp_transport = self.env['employee.transport.list'].search(
                    [('transportation_line_request_id.id', '=', line_id.id)])
                for emp in emp_transport:
                    vals = {
                        'employee': emp.employee,
                    }
                    self.update({'adding_transport_list_ids': [(0, 0, vals)]})
                    counter += 1

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'adding.worker.to.transport.line') or 'New'
        return super(AddingWorkerTransportLine, self).create(vals)

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
