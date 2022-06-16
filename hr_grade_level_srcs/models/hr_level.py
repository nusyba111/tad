# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError, ValidationError


class HrLevel(models.Model):
    """"""
    _name = 'hr.level'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    sequence = fields.Integer(required=True, )
    wage = fields.Monetary(required=False)
    s_insurance = fields.Float(string="S. Insurance 17 %",compute="_compute_social_insurance")
    h_insurance = fields.Float(string="H. Insurance")
    a_s_b = fields.Float(string="A.S.B",compute="_compute_asb")
    leave_allowance = fields.Float(string="Leave allowance",compute="_compute_leave_allowance")
    trans = fields.Float(string="TRANS")
    eid_bonus = fields.Float(string="Eid bonus",compute="_compute_eid_bouns")
    total_job_cost = fields.Float(string="Total Job Cost",compute="_compute_total_job_cost")
    grade_id = fields.Many2one('hr.grade', string='Grade')
    company_id = fields.Many2one('res.company', string='Company', related='grade_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    
    def _compute_social_insurance(self):
        for rec in self:
            rec.s_insurance = rec.wage * 0.17

    def _compute_asb(self):
        for rec in self:
            rec.a_s_b = rec.wage * 0.05     

    def _compute_leave_allowance(self):
        for rec in self:
            rec.leave_allowance = rec.wage / 12   

    def _compute_eid_bouns(self):
        for rec in self:
            rec.eid_bonus = (rec.wage / 12) * 2   


    def _compute_total_job_cost(self):
        for rec in self:
            rec.total_job_cost = rec.wage + rec.h_insurance + rec.s_insurance + rec.a_s_b + rec.leave_allowance + rec.trans + rec.eid_bonus                     


    @api.constrains('sequence')
    def _check_levels_sequence(self):
        """
        A method to check level sequence.
        """
        for record in self:
            if record.sequence < 0:
                raise ValidationError("Sequence must be more than zero")

    @api.model
    def create(self, vals):
        """
        A method to create level sequence.
        """
        seq = self.env['ir.sequence'].next_by_code('hr.level')
        vals['sequence'] = seq
        level = super(HrLevel, self).create(vals)
        return level

    def unlink(self):
        """
        A method to delete level before assign to employee.
        """
        for level in self:
            if self.env['hr.employee'].filtered('level_id'):
                raise UserError(_('You can not delete level  assigned to employee'))
        return super(HrLevel, self).unlink()

    _sql_constraints = [
        ('sequence_uniq', 'unique (sequence,company_id)', "The sequence of level must be unique per company")]
