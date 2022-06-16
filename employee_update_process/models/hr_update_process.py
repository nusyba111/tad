# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError



class HrUpdateProcess(models.Model):
    _name = 'hr.update.process'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Department Manager Approve'),
         ('hr_approve', 'HR Manager Approve'),
         ('finance_approve', 'Finance Manager Approve'),
         ('approve','Approved'),
         ('cancel', 'Cancel')], readonly=True, default='draft', copy=False, string="Status", track_visibility='onchange')
    name = fields.Char(readonly=True, default=lambda self: _('New'))
    date = fields.Date(string="Date", default=fields.Date.context_today)
    approve_date = fields.Date(string="Approve Date")
    type = fields.Selection([('all', 'All Employee'), ('employee', 'Employee'), ('select_employees', 'Select Employees')], string="Type")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    update_type = fields.Selection([('salary', 'Salary'),
                                    ('department', 'Department'),
                                    ('job_position', 'Job Position'),
                                    ('position_and_salary','Job Position & Salary')], string="Update Type")
    grade_id = fields.Many2one('hr.grade',string="Grade")
    level_id = fields.Many2one('hr.level',string="Level")
    wage = fields.Float(string="Wage")
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Jop Position")
    update_reason = fields.Text(string="Update Reason", required=True)
    update_lines = fields.One2many('hr.update.line', 'update_process_id', string="Update Line", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)


    @api.model
    def create(self, vals):
        rec = super(HrUpdateProcess, self).create(vals)
        rec.name = self.env['ir.sequence'].get('employee.update.process') or 'New'
        return rec

    def confirm(self):
        self.state = 'confirm'
        self.update_line()

    # def approve(self):
    #     self.state = 'approve'
    #     self.approve_date = datetime.now()
    #     if self.type == 'employee':
    #         self.update_employees(self.employee_id)
    #     if self.type == 'select_employees':
    #         self.update_employees(self.employee_ids)
    #     if self.type == 'all':
    #         self.update_employees(self.get_employees())

    # def cancel(self):
    #     self.state = 'cancel'

    # def set_to_draft(self):
    #     self.write({'state': 'draft'})

    # def update_line(self):
    #     if self.type == 'employee':
    #         self.create_update_line(self.employee_id)
    #     if self.type == 'select_employees' or self.type == 'all':
    #         employees = self.get_employees()
    #         for employee_id in employees:
    #             self.create_update_line(employee_id)

    # def create_update_line(self, employee_id):
    #     x = self.env['hr.update.line'].create({
    #         'employee_id': employee_id.id,
    #         'contract_id': employee_id.contract_id.id,
    #         'update_process_id': self.id,
    #         'old_salary': employee_id.contract_id.wage,
    #         'old_department_id': employee_id.contract_id.department_id.id,
    #         'old_job_id': employee_id.contract_id.job_id.id,
    #         'salary': self.wage,
    #         'department_id': self.department_id.id,
    #         'job_id': self.job_id.id,
    #     })

    # def update_employees(self, employees):
    #     for rec in employees:
    #         if self.wage:
    #             rec.contract_id.wage = self.wage
    #         if self.department_id:
    #             rec.contract_id.department_id = self.department_id.id
    #             rec.department_id = self.department_id.id 
    #         if self.job_id:
    #             rec.contract_id.job_id = self.job_id.id
    #             rec.job_id = self.job_id.id

    # def get_employees(self):
    #     if self.type == 'select_employees':
    #         return self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids)])
    #     return self.env['hr.employee'].search([])

    # def unlink(self):
    #     """
    #     A method to delete update process record.
    #     """
    #     for record in self:
    #         if record.state not in ('draft',):
    #             raise UserError(_('You can not delete record not in draft state.'))
    #     return super(HrUpdateProcess, self).unlink()


class HrUpdateLine(models.Model):
    _name = 'hr.update.line'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Current Contract")
    update_process_id = fields.Many2one('hr.update.process', string="Update Process")
    update_type = fields.Selection(related="update_process_id.update_type", string="Update Type")
    old_grade = fields.Many2one('hr.grade',string="Old Grade")
    old_level = fields.Many2one('hr.level',string="Old Level")
    old_salary = fields.Float(string="Old Salary")
    old_department_id = fields.Many2one('hr.department', string="Old Department")
    old_job_id = fields.Many2one('hr.job', string="Old Jop Position")
    salary = fields.Float(string="Current Salary")
    department_id = fields.Many2one('hr.department', string="Current Department")
    job_id = fields.Many2one('hr.job', string="Current Jop Position")
