# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductHealth(models.Model):
    _name = 'product.health'
    _description = 'product health'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No', )
    date = fields.Date(string='Date')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    product = fields.Many2one('product.template', string='product')
    procedure = fields.Selection([('new', 'New'), ('renewal', 'Renewal')])
    health_card_ids = fields.One2many('health.card.info', 'health_card_id', string='health card ')
    fitness_card_ids = fields.One2many('fitness.card', 'fitness_card_id', string='fitness card')
    car_card_ids = fields.One2many('car.card', 'car_card_id', string='car card')
    hall_health_ids = fields.One2many('hall.health', 'hall_health_id', string='hall health')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Requester'),
                                        ('approve', 'Approve by Department Manager'),
                                        ('approve2', 'Approve by Admin Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
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

    def action_approve2(self):
        return self.write({'state': 'approve2'})

    def action_done(self):
        # self.change_state()
        return self.write({'state': 'done'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'product.health.seq') or 'New'
        return super(ProductHealth, self).create(vals)


class HealthCard(models.Model):
    _name = 'health.card.info'

    health_card_id = fields.Many2one('product.health', string=' health card', readonly=False)
    employee = fields.Many2one('hr.employee', string='Employee')
    dep = fields.Char(string='Department', related='employee.department_id.name')
    job_position = fields.Char(string='Job Position', related='employee.job_title')
    address = fields.Char(string='Address', related='employee.home_address')
    phone_num = fields.Char(string='Phone Number', related='employee.phone')
    worker_type = fields.Selection([('temporary', 'Temporary'), ('permanent', 'Permanent')]
                                   , string='Worker Type', )
    status = fields.Selection([('received', 'Received'), ('not_received', 'Not Received')]
                              , string='status', )
    notes = fields.Char(string='notes')


class FitnessCards(models.Model):
    _name = 'fitness.card'
    _inherit = 'health.card.info'

    fitness_card_id = fields.Many2one('product.health', string=' Fitness card')


class CarsHealth(models.Model):
    _name = 'car.card'

    car_card_id = fields.Many2one('product.health', string=' Car Health Card')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    # car_type = fields.Char(string='car type', related='car_no.type_ol')
    status = fields.Selection([('received', 'Received'), ('not_received', 'Not Received')]
                              , string='status', )
    notes = fields.Char(string='notes')


class HallHealth(models.Model):
    _name = 'hall.health'

    hall_health_id = fields.Many2one('product.health', string='Hall Health ')
    hall_name = fields.Many2one('hall.name', string='hall name')
    ventilation = fields.Boolean('ventilation')
    lighting = fields.Boolean('lighting')
    hall_space = fields.Boolean('hall space')
    cleanness = fields.Boolean('cleanness')
    status = fields.Selection([('received', 'Received'), ('not_received', 'Not Received')]
                              , string='status', )
    notes = fields.Char(string='notes')
