from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, AccessError, ValidationError
from dateutil.relativedelta import relativedelta


class HrWageProcess(models.Model):
    """"""
    _name = 'hr.wage.process'
    _inherit = ['mail.thread']

    name = fields.Char(default="Draft")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    type = fields.Selection([('promotion', 'Promotion'),
                             ('increment', 'Increment'), ('redLine', 'Red Line')],
                            default="promotion", required=True)
    contract_id = fields.Many2one(related='employee_id.contract_id', readonly=True, store=True)
    grade_sequence = fields.Integer(related='employee_id.grade_id.sequence')
    level_sequence = fields.Integer(related='employee_id.level_id.sequence')
    grade_id = fields.Many2one('hr.grade', string='Grade', )
    level_id = fields.Many2one('hr.level', string='Degree', )
    wage = fields.Float(string='New Wage', store=True)
    note = fields.Text()
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('approve', 'Approve'),
                              ('refused', 'Refused')], default='draft', track_visibility='onchange')

    current_grade = fields.Many2one('hr.grade', string="Current Grade")
    current_level = fields.Many2one('hr.level', string="Current Level")
    current_wage = fields.Monetary(string="Current Wage", digits=(16, 2))
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    percentages = fields.Integer(string="percentage (%)", default=1)
    red_line_type = fields.Selection([('fix_amount', 'Fix Amount'),
                                      ('percentage', 'Percentage'), ],
                                     default="fix_amount", required=True)
    batch_id = fields.Many2one('hr.wage.process.batch', string='batch', ondelete='set null', )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    def action_set_to_confirm(self):
        """
        A method to confirm wage.
        """
        self.state = 'confirm'

    def action_set_to_approve(self):
        """
        A method to approve wage.
        """
        seq = '/'
        if self.type == 'redLine':

            seq = self.env['ir.sequence'].next_by_code('wage.process.redLine')
            self.employee_id.write({'wage': self.wage})
            self.contract_id.write({'wage': self.wage})

        elif self.type == 'promotion':

            seq = self.env['ir.sequence'].next_by_code('wage.process.promotion')
            self.employee_id.write({'grade_id': self.grade_id.id, 'level_id': self.level_id.id})
            self.contract_id.write({'grade_id': self.grade_id.id, 'level_id': self.level_id.id})

        elif self.type == 'increment':

            seq = self.env['ir.sequence'].next_by_code('wage.process.increment')
            self.employee_id.write({'level_id': self.level_id.id})
            self.contract_id.write({'level_id': self.level_id.id})

        self.write({'state': 'approve', 'name': seq})

    def action_set_to_refused(self):
        """
        A method to refuse wage.
        """
        self.state = 'refused'

    def action_set_to_draft(self):
        """
        A method to reset wage draft.
        """
        self.state = 'draft'

    @api.constrains('wage')
    def _check_new_amount(self):
        """
        A method to check new wage for employee.
        """
        for record in self:
            if record.type == 'redLine' and record.wage < record.employee_id.wage:
                raise ValidationError("New wage must be more than current wage ")

    def unlink(self):
        """Deny unlink when record not in draft state"""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete Record not in draft state"))
            else:
                return super(HrWageProcess, self).unlink()

    @api.model
    def create(self, vals):
        """
        Inherit method to increase wage depend on wage increase type.
        """
        res = super(HrWageProcess, self).create(vals)
        res.current_wage = res.contract_id.wage
        res.current_grade = res.contract_id.grade_id
        res.current_level = res.contract_id.level_id
        if vals.get('type', False) == 'redLine' and vals.get('red_line_type', False) == 'percentage':
            increase_amount = res.current_wage * res.percentages / 100
            res.wage = res.current_wage + increase_amount
        if vals.get('type', False) == 'increment':
            res.grade_id = res.current_grade
        return res

    def write(self, vals):
        """
        Inherit method to update wage in case increase type percentage.
        """
        if vals.get('redLine', False) == 'redLine' or vals.get('red_line_type', False) == 'percentage':
            increase_amount = self.current_wage * self.percentages / 100
            vals['wage'] = self.current_wage + increase_amount
        return super(HrWageProcess, self).write(vals)

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        """
        A method to change wage, grade and level in case contract was change.
        """
        if self.contract_id:
            self.current_wage = self.contract_id.wage
            self.current_grade = self.contract_id.grade_id
            self.current_level = self.contract_id.level_id

    @api.onchange('type')
    def _onchange_type(self):
        """
        A method to change grade in case contract type was change.
        """
        if self.type == 'increment':
            self.grade_id = self.current_grade

    @api.onchange('percentages')
    def _onchange_type_wage(self):
        """
        A method to change wage in case increase type was change.
        """
        if self.red_line_type == 'percentage':
            increase_amount = self.current_wage * self.percentages / 100
            self.wage = self.current_wage + increase_amount
