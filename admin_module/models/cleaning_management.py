# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime
# from datetime import date, datetime, time
# import calendar
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime


class CleanFollowUp(models.Model):
    _name = 'clean.follow'
    _description = 'cleaning follow up'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No.')
    time = fields.Float(string='Time')
    date = fields.Date(string='Date')
    clean_info_ids = fields.One2many('clean.follow.info', 'clean_id', string='cleaning follow up information')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by services supervisor'),
                                        ('approve', 'Approve by Services Section Head'),
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

    def action_done(self):
        # self.change_state()
        return self.write({'state': 'done'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'clean.follow.seq') or 'New'
        return super(CleanFollowUp, self).create(vals)


class CleanFollowUpInfo(models.Model):
    _name = 'clean.follow.info'

    clean_id = fields.Many2one('clean.follow', string='cleaning follow up')
    dep_area = fields.Many2one('hr.work.location', string='department/Area')
    tools_used = fields.Many2many('clean.tools', 'clean_tool_rel', 'clean_id', string='Tools Used')
    rec_bin_emp = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Recycle Bin emptying')
    res_of_clean = fields.Many2one('hr.employee', string='Responsible of Cleaning')
    res_follow_up = fields.Many2one('hr.employee', string='Responsible of Follow-Up')
    note = fields.Text(string='Notes')


class SanitationFollowUp(models.Model):
    _name = 'sanitation.follow'
    _description = 'sanitation follow up'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No.')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    type_of_well = fields.Selection([('general', 'General'), ('sesame', 'Sesame')]
                                    , string='Type of well')
    # should appear either car_no or Receipt no depend on tanker_type
    car_no = fields.Char(string='Car No')
    receipt_no = fields.Char(string='Receipt No')

    time_in = fields.Float(string='Time In')
    date = fields.Date(string='Date')
    tanker_type = fields.Selection([('commercial', 'Commercial'), ('company', 'Company')]
                                   , string='Tanker Type', required=True)
    driver_name = fields.Many2one('hr.employee', string='Driver Name')
    time_out = fields.Float(string='Time Out')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    total_commercial = fields.Integer(compute='compute_total_commercial')
    total_company = fields.Integer(compute='compute_total_company')
    total = fields.Integer(compute='compute_total')

    @api.onchange('tanker_type')
    def compute_total_commercial(self):
        for rec in self:
            rec.total_commercial = self.env['sanitation.follow'].search_count(
                [('tanker_type', '=', 'commercial'), ])

    @api.onchange('tanker_type')
    def compute_total_company(self):
        for rec in self:
            rec.total_company = self.env['sanitation.follow'].search_count(
                [('tanker_type', '=', 'company'), ])

    @api.onchange('tanker_type')
    def compute_total(self):
        for rec in self:
            rec.total = rec.total_commercial + rec.total_company

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_done(self):
        # self.change_state()
        return self.write({'state': 'done'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'sanitation.follow.seq') or 'New'
        return super(SanitationFollowUp, self).create(vals)


class SanitationCal(models.Model):
    _name = 'sanitation.calculation'
    _description = 'sanitation calculation '
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No.')
    date = fields.Date(string='Date')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total = fields.Float(string='Total', compute='compute_total')
    santi_info_ids = fields.One2many('sanitation.calculation.info', 'santi_id',
                                     string='Sanitation Calculation Information')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Supervisor'),
                                        ('approve', 'Approve by Admin Manager'),
                                        ('approve2', 'Approve by GM/ Executive Manager'),
                                        ('done', 'Approve by Finance Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('santi_info_ids', 'santi_info_ids.total_cost')
    def compute_total(self):
        self.total = 0.0
        for rec in self.santi_info_ids:
            price = rec.total_cost
            self.total += price

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
        # self.change_state()
        return self.write({'state': 'done'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'sanitation.calculation.seq') or 'New'
        return super(SanitationCal, self).create(vals)


class SanitationCalInfo(models.Model):
    _name = 'sanitation.calculation.info'

    santi_id = fields.Many2one('sanitation.calculation', string='sanitation calculation')
    date = fields.Date(string='Date')
    tanker_type = fields.Selection([('commercial', 'Commercial'), ('company', 'Company')]
                                   , string='Tanker Type')
    contractor = fields.Many2one('res.partner', string='Contractor')
    driver = fields.Many2one('res.partner', string='Driver')
    tanker_count = fields.Integer(string='Tanker Count')
    tanker_cost = fields.Float(string='Tanker Cost')
    total_cost = fields.Float(string='Total Cost', compute='compute_total_cost')
    notes = fields.Text(string='Notes')

    @api.onchange('tanker_count', 'tanker_cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.tanker_count * rec.tanker_cost


class GarbageFollowUp(models.Model):
    _name = 'garbage.follow'
    _description = 'Garbage follow up '
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No.')
    collection_date = fields.Date(string='Collection Date')
    car_no = fields.Char(string='Car No.')
    time_in = fields.Float(string='Time In')
    date = fields.Date(string='Date')
    collection_count = fields.Integer(string='Collection Count')
    driver_name = fields.Many2one('hr.employee', string='Driver Name')
    time_out = fields.Float(string='Time Out')
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

    def action_done(self):
        # self.change_state()
        return self.write({'state': 'done'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'garbage.follow.seq') or 'New'
        return super(GarbageFollowUp, self).create(vals)


class GarbageCal(models.Model):
    _name = 'garbage.calculation'
    _description = 'Garbage calculation '
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No.')
    date = fields.Date(string='Date')

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total_all = fields.Float(string='Total')
    payment_number = fields.Many2one('account.payment', string='Payment Number')
    total_cost_total = fields.Float(string='Total', compute='compute_total_cost_total')
    gar_info_ids = fields.One2many('garbage.calculation.info', 'gar_id', string='Garbage Total Information')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Supervisor'),
                                        ('approve', 'Approve by Admin Manager'),
                                        ('approve2', 'Approve by GM/ Executive Manager'),
                                        ('done', 'Approve by Finance Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')
    total_agreed_report = fields.Integer(string='total agreed all', compute='compute_total_agreed')
    total_cost_report = fields.Float(string='total cost all', compute='compute_total_cost_report')

    @api.onchange('gar_info_ids', 'gar_info_ids.total_cost')
    def compute_total_cost_total(self):
        self.total_cost_total = 0.0
        for rec in self.gar_info_ids:
            price = rec.total_cost
            self.total_cost_total += price

    @api.onchange('gar_info_ids', 'gar_info_ids.agreed_count')
    def compute_total_agreed(self):
        for rec in self:
            rec.total_agreed_report = 0.0
            count = 0.0
            for line in self.gar_info_ids:
                count = line.agreed_count
                rec.total_agreed_report += count

    @api.onchange('gar_info_ids', 'gar_info_ids.cost')
    def compute_total_cost_report(self):
        for rec in self:
            rec.total_cost_report = 0.0
            sum_cost = 0.0
            for line in self.gar_info_ids:
                sum_cost = line.cost
                rec.total_cost_report += sum_cost

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

    def action_approve3(self):
        return self.write({'state': 'approve3'})

    def action_done(self):
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'garbage.calculation.seq') or 'New'
        return super(GarbageCal, self).create(vals)


#
#
class GarbageCalInfo(models.Model):
    _name = 'garbage.calculation.info'

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    gar_id = fields.Many2one('garbage.calculation', string='Garbage Total')
    contractor = fields.Many2one('res.partner', string='Contractor')
    total = fields.Float(string='Total', )
    agreed_count = fields.Integer(string='Agreed Count')
    additional_count = fields.Integer(string='Additional Count')
    cost = fields.Float(string='Cost')
    total_cost = fields.Float(string='Total Cost', compute='compute_total_cost')
    notes = fields.Text(string='Notes')

    @api.onchange('total', 'cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.total * rec.cost
