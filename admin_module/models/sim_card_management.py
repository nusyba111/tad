# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class SimCard(models.Model):
    _name = 'sim.card'
    _description = 'SIM Card Ceiling Increase Request'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doc_num = fields.Char(string='Doc No.')
    requester = fields.Many2one('hr.employee', string='Requester')
    new_date_inc = fields.Date(string='New Date of Increase')
    date = fields.Date(string='Date')
    requester_dep = fields.Char(string='Requester Department',
                                related='requester.department_id.name')
    reasons = fields.Text(string='Reasons')
    mang_dec = fields.Text(string='Management Decision')
    sim_info_ids = fields.One2many('sim.card.info', 'sim_id', string='SIM Cards')
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

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'sim.card.seq') or 'New'
        return super(SimCard, self).create(vals)


class SimCardInfo(models.Model):
    _name = 'sim.card.info'

    sim_id = fields.Many2one('sim.card', string='SIM Card')
    emp_name = fields.Many2one('hr.employee', string='Employee Name')
    dep = fields.Char(string='Department', related='emp_name.department_id.name')
    sim_card_type = fields.Selection([('prepaid', 'Prepaid'), ('postpaid', 'PostPaid'), ('data', 'Data')],
                                     string='SIM Card Type')
    comp_name = fields.Selection([('zain', 'Zain'), ('mtn', 'MTN'), ('sudani', 'Sudani')],
                                 string='Company Name')
    phone_num = fields.Integer(string='Phone No')
    cur_cred_giga = fields.Integer(string='Current Credit/Giga')
    pro_cred_giga = fields.Integer(string='Proposed Credit/Giga')
    app_cred_giga = fields.Integer(string='Approved Credit/Giga')
