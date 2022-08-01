# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class WorkerMeal(models.Model):
    _name = 'worker.meal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'worker meals'
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    total = fields.Float(string='Total', compute='compute_total')
    worker_meal_ids = fields.One2many('worker.meal.info', 'worker_meal_id',
                                      string='Workers Attendance ')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('worker_meal_ids', 'worker_meal_ids.total_worker')
    def compute_total(self):
        self.total = 0.0
        for rec in self.worker_meal_ids:
            price = rec.total_worker
            self.total += price

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
            'worker.meal.seq') or 'New'
        return super(WorkerMeal, self).create(vals)


class WorkerMealInfo(models.Model):
    _name = 'worker.meal.info'

    worker_meal_id = fields.Many2one('worker.meal', string='Worker Attendance', )
    dep = fields.Many2one('hr.department', string='Department')
    total_per = fields.Integer(string='Total Permanent', )
    total_temp = fields.Integer(string='Total Temporary', )
    total_worker = fields.Integer(string='Total Workers', compute='compute_total_worker')
    notes = fields.Text(string='Notes', )

    @api.onchange('total_temp', 'total_per')
    def compute_total_worker(self):
        for rec in self:
            rec.total_worker = rec.total_temp + rec.total_per


class WorkerMealSub(models.Model):
    _name = 'worker.meal.subsidy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'worker meals subsidy'
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    requester = fields.Many2one('hr.employee', string='Requester')
    req_department = fields.Char(string='Requesting Department', related='requester.department_id.name')
    reasons = fields.Text(string='Reasons')
    subsidy_meal_info_ids = fields.One2many('worker.meal.subsidy.info', 'subsidy_meal_id',
                                            string='Workers Meals Subsidy List ')
    subsidy_total = fields.Float(string='Subsidy Total', compute='compute_subsidy_total')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Dep Section Head'),
                                        ('approve', 'Approve by Services Section Head'),
                                        ('approve2', 'Approve by Administration Manager'),
                                        ('done', 'Approve by GM/ Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('subsidy_meal_info_ids', 'subsidy_meal_info_ids.subsidy_amount')
    def compute_subsidy_total(self):
        self.subsidy_total = 0.0
        for rec in self.subsidy_meal_info_ids:
            price = rec.subsidy_amount
            self.subsidy_total += price

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
            'worker.meal.subsidy.seq') or 'New'
        return super(WorkerMealSub, self).create(vals)


class WorkerMealSubInfo(models.Model):
    _name = 'worker.meal.subsidy.info'

    subsidy_meal_id = fields.Many2one('worker.meal.subsidy', string='Workers Meals Subsidy List')
    employee = fields.Many2one('hr.employee', string='Employee')
    dep = fields.Char(string='Department', related='employee.department_id.name')
    job_position = fields.Char(string='Job Position', related='employee.job_title')
    subsidy_amount = fields.Float(string='Subsidy Amount')


class WorkerMealCancelSub(models.Model):
    _name = 'worker.meal.cancel.subsidy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'worker meals cancel subsidy'
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    requester = fields.Many2one('hr.employee', string='Requester')
    req_department = fields.Char(string='Requesting Department', related='requester.department_id.name')
    reasons = fields.Text(string='Reasons')
    subsidy_cancel_info_ids = fields.One2many('worker.meal.cancel.subsidy.info', 'subsidy_cancel_id',
                                              string='Workers Meal Subsidy List ')
    subsidy_total = fields.Integer(string='Subsidy Total', compute='compute_subsidy_total')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Section Head'),
                                        ('approve', 'Approve by Administration Manager'),
                                        ('approve2', 'Approve by Dep Section Head'),
                                        ('done', 'Approve by GM/ Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('subsidy_cancel_info_ids', 'subsidy_meal_info_ids.subsidy_daily_amount')
    def compute_subsidy_total(self):
        self.subsidy_total = 0.0
        for rec in self.subsidy_cancel_info_ids:
            price = rec.subsidy_daily_amount
            self.subsidy_total += price

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

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'worker.meal.cancel.subsidy.seq') or 'New'
        return super(WorkerMealCancelSub, self).create(vals)


class WorkerMealCancelSubInfo(models.Model):
    _name = 'worker.meal.cancel.subsidy.info'

    subsidy_cancel_id = fields.Many2one('worker.meal.cancel.subsidy', string='Workers Meals Subsidy List')
    employee = fields.Many2one('hr.employee', string='Employee')
    dep = fields.Char(string='Department', related='employee.department_id.name')
    job_position = fields.Char(string='Job Position', related='employee.job_title')
    subsidy_daily_amount = fields.Integer(string='Subsidy Daily Amount')


class WorkerCostMeal(models.Model):
    _name = 'worker.meal.cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'worker meals cost calculations '
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total = fields.Float(string='Total', compute='compute_total')
    worker_meal_cost_ids = fields.One2many('worker.meal.cost.info', 'worker_meal_cost_id',
                                           string='Worker Meal Details ')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Service Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('approve2', 'Approve by Administration Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    def compute_total(self):
        self.total = 0.0
        for rec in self.worker_meal_cost_ids:
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
            'worker.meal.cost.seq') or 'New'
        return super(WorkerCostMeal, self).create(vals)


class WorkerCostMealInfo(models.Model):
    _name = 'worker.meal.cost.info'

    worker_meal_cost_id = fields.Many2one('worker.meal.cost', string='Worker Meal Details')
    dep = fields.Many2one('hr.department', string='Department')
    total_per_att = fields.Integer(string='Total Permanent Attendance', )
    total_temp_att = fields.Integer(string='Total Temporary Attendance', )
    total_worker_att = fields.Integer(string='Total Worker Attendance', compute='compute_total_worker_att')
    meal_price = fields.Float(string='Meal Price', )
    total_cost = fields.Float(string='Total Cost', compute='compute_total_cost')
    notes = fields.Text(string='Notes', )

    @api.onchange('total_per_att', 'total_temp_att')
    def compute_total_worker_att(self):
        for rec in self:
            rec.total_worker_att = rec.total_temp_att + rec.total_per_att

    @api.onchange('total_worker_att', 'meal_price')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.total_worker_att * rec.meal_price


class EmpCostMeal(models.Model):
    _name = 'employee.meal.cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'employee meals cost calculations '
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    emp_meal_info_ids = fields.One2many('employee.meal.cost.info', 'emp_meal_id', string='Employee Meal Details ')
    total = fields.Float(string='Total')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Service Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('approve2', 'Approve by Administration Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('emp_meal_info_ids', 'emp_meal_info_ids.total_meal_price')
    def _compute_total(self):
        self.total = 0.0
        for rec in self.emp_meal_info_ids:
            price = rec.total_meal_price
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
            'employee.meal.cost.seq') or 'New'
        return super(EmpCostMeal, self).create(vals)


class EmpCostMealInfo(models.Model):
    _name = 'employee.meal.cost.info'

    emp_meal_id = fields.Many2one('employee.meal.cost', string='Employee Meal Details')
    employee = fields.Many2one('hr.employee', string='Employee')
    dep = fields.Char(string='Department', related='employee.department_id.name')
    job_position = fields.Char(string='Job Position', related='employee.job_title')
    total_meal_price = fields.Float(string='Total Meal Price', )
    notes = fields.Text(string='Notes', )


class MealCostCal(models.Model):
    _name = 'meal.cost.cal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'meals cost calculations '
    _rec_name = 'doc_num'

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total = fields.Float(string='Total Subsidy Amount', compute='compute_total')
    meal_cost_info_ids = fields.One2many('meal.cost.cal.info', 'meal_cost_info_id',
                                         string='Meal Cost Calculation Information')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Service Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('approve2', 'Approve by Administration Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('meal_cost_info_ids', 'meal_cost_info_ids.subsidy_amount')
    def compute_total(self):
        self.total = 0.0
        for rec in self.meal_cost_info_ids:
            price = rec.subsidy_amount
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
            'meal.cost.cal.seq') or 'New'
        return super(MealCostCal, self).create(vals)


class MealCostCalInfo(models.Model):
    _name = 'meal.cost.cal.info'

    meal_cost_info_id = fields.Many2one('meal.cost.cal', string='Meal Cost Calculation')
    # #### item is Many2one field should be selected from other model
    item = fields.Many2one('meal.item', string='Item')
    meal_count = fields.Integer(string='Meals Count', )
    subsidy_amount = fields.Float(string='Subsidy Amount', )
    meal_price = fields.Float(string='Meal Price', )
    total_meal_amount = fields.Float(string='Total Meal Amount', compute='compute_total_meal_amount')
    notes = fields.Text(string='Notes', )

    @api.onchange('meal_count', 'meal_price')
    def compute_total_meal_amount(self):
        for rec in self:
            rec.total_meal_amount = rec.meal_count * rec.meal_price
