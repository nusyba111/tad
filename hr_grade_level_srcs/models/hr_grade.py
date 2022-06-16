# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
from odoo.exceptions import UserError, AccessError, ValidationError


class HrGrade(models.Model):#
    """"""
    _name = 'hr.grade'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    sequence = fields.Integer(track_visibility='onchange')
    # increment = fields.Integer(default=0, required=True, track_visibility='onchange')
    degrees_no = fields.Integer(string='No of degrees', required=True, track_visibility='onchange')
    # initial_wage = fields.Float(string='Initial Wage', required=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    degree_ids = fields.One2many('hr.level', 'grade_id', string='Degrees')
    line_ids = fields.One2many('grade.allow.deduct', 'grade_id', string='Grade Allowances', copy=False)
    job_id = fields.Many2one('hr.job',string="Job Position")

    @api.constrains('degrees_no', 'sequence')
    def _check_degrees_sequence(self):
        """
        A method to check degree and sequence.
        """
        for record in self:
            if record.degrees_no <= 0:
                raise ValidationError("Number of degrees must be more than zero")

            if record.sequence < 0:
                raise ValidationError("Sequence must be more than zero")

    def calculate_levels(self):
        """
        A method to calculate level.
        """
        for rec in self:
            level_sequence = 1
            name = 'A'
            # wage = rec.initial_wage
            lines = [(0, False, {'name': name + str(level_sequence), 'grade_id': rec.id})]
            degrees_no = rec.degrees_no

            while degrees_no > 1:
                level_sequence = level_sequence + 1
                name = 'A' + str(level_sequence)
                # wage += wage * rec.increment / 100.0
                lines.append((0, False,
                              {
                                  'name': name,
                                  # 'wage': wage,
                                  'grade_id': rec.id}))
                degrees_no = degrees_no - 1

        self.write({'degree_ids': lines})

    # @api.onchange('initial_wage', 'increment')
    # @api.onchange('initial_wage')
    # def update_levels(self):
    #     """
    #     A method to level level.
    #     """
    #     for rec in self:
    #         level_sequence = 1
    #         wage = rec.initial_wage
    #         rec.degree_ids.search([], order='sequence asc', limit=1).write({'wage': rec.initial_wage})
    #         degrees_no = rec.degrees_no

    #         while degrees_no > 1:
    #             level_sequence = level_sequence + 1
    #             wage += wage * rec.increment / 100.0
    #             rec.degree_ids.filtered(lambda x: x.sequence == level_sequence).write({'wage': wage})
    #             degrees_no = degrees_no - 1

    def create_level(self, last_degree_level, no_new_degree):
        """
        A method to create level.
        """
        level_sequence = 1
        new_lines = []
        # last_wage = last_degree_level.wage
        for x in range(no_new_degree):
            # last_wage = last_wage + last_wage * last_degree_level.grade_id.increment / 100
            new_lines.append({
                'name': 'D' + str(last_degree_level.sequence + x + 1),
                'sequence': last_degree_level.sequence + x + 1,
                # 'wage': last_wage,
                'grade_id': last_degree_level.grade_id.id})
        print('new linesssssss', new_lines)
        return self.env['hr.level'].create(new_lines)

    # @api.multi
    def write(self, vals):
        """
        A method to update degree.
        """
        if 'degrees_no' in vals:
            if len(self.degree_ids) > vals['degrees_no']:
                degree_diff = len(self.degree_ids) - vals['degrees_no']

                self.degree_ids.search([], order='sequence desc', limit=degree_diff).unlink()
            elif len(self.degree_ids) < vals['degrees_no']:
                new_degrees = vals['degrees_no'] - len(self.degree_ids)
                rec = self.create_level(self.degree_ids.search([], order='sequence desc', limit=1), new_degrees)
        res = super(HrGrade, self).write(vals)

        return res

    @api.model
    def create(self, vals):
        """
        A method to create sequence and calculate level.
        """
        seq = self.env['ir.sequence'].next_by_code('hr.grade')
        vals['sequence'] = seq
        grade = super(HrGrade, self).create(vals)
        grade.sudo().calculate_levels()
        return grade

    _sql_constraints = [
        ('sequence_uniq', 'unique (sequence,company_id)', "The sequence of grade must be unique per company")]

class DeductAllow(models.Model):
    """"""
    _name = "grade.allow.deduct"

    grade_id = fields.Many2one('hr.grade', string='Grade',ondelete='cascade')
    amount_deduct = fields.Float(string="Amount", required=True)
    allow_deduct = fields.Many2one('hr.salary.rule', domain=[('use_type', '=', 'special',)],string='Allowance')

# class ContractDeductAllow(models.Model):
#     """"""
#     _inherit = "contract.allow.deduct"

#     grade_related = fields.Boolean(string='Grade Related',help='Technical Field')
