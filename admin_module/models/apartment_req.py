# -*- coding: utf-8 -*-
# from dateutil.utils import today
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class ApartRentReq(models.Model):
    _name = 'apartment.rent'
    _description = 'apartment rent request'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Dat')
    requester = fields.Many2one('hr.employee', string='requester')
    requester_dep = fields.Char(string='Requester Department',
                                related='requester.department_id.name')
    priority = fields.Selection([('1', 'low'), ('2', 'medium'), ('3', 'high'), ('4', 'excellent')])
    rent_type = fields.Selection([('temporary', 'Temporary'), ('permanent', 'Permanent')]
                                 , string='Rent Type', )
    rent_for = fields.Selection([('guest', 'Guest'), ('employee', 'Employee')]
                                , string='Rent For', )
    purpose = fields.Text(string='Purpose')
    owner_name = fields.Char(string='Owner Name')
    owner_phone = fields.Integer(string='Owner Phone')
    address = fields.Char(string='Address', )
    payment_date = fields.Date(string='Payment Date')
    payment_method = fields.Integer(string='Payment Method')
    next_payment_date = fields.Date(string='Next Payment Date', compute='action_next_payment_date', )
    emp_guest_ids = fields.One2many('employee.guest.info', 'emp_guest_id', string='employee/guest')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Requester'),
                                        ('approve', 'Approve by GM/ Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    first_date = fields.Date(string='From Date')
    sec_date = fields.Date(string='To date')
    days = fields.Float(compute='_compute_days', string='period')

    @api.onchange('first_date', 'sec_date')
    def _compute_days(self):
        self.days = 0
        self.first_date = None
        self.sec_date = None
        for rec in self:
            if rec.first_date and rec.payment_date:
                rec.days = relativedelta(rec.sec_date, rec.first_date).days
            else:
                print('no record')

    @api.onchange('payment_date', 'payment_method')
    def action_next_payment_date(self):
        self.next_payment_date = None
        for rec in self:
            if rec.payment_method and rec.payment_date:
                rec.next_payment_date = rec.payment_date + relativedelta(months=+int(rec.payment_method))
            else:
                print('no record')

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

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'apr.rent.seq') or 'New'
        return super(ApartRentReq, self).create(vals)


class EmpGuestInfo(models.Model):
    _name = 'employee.guest.info'

    emp_guest_id = fields.Many2one('apartment.rent', string='apartment rent')
    rent_for = fields.Selection([('guest', 'Guest'), ('employee', 'Employee')]
                                , string='Rent For', )
    guest = fields.Char(string='Guest Name')
    employee = fields.Many2one('hr.employee', string='Employee Name')
    dep = fields.Char(string='Department', related='employee.department_id.name')
    job_position = fields.Char(string='Job Position', related='employee.job_title')
    address = fields.Char(string='Address', related='employee.home_address')
    # related='employee.address_home_id.name')
    phone_num = fields.Char(string='Phone Number', related='employee.phone')
    notes = fields.Char(string='notes')
