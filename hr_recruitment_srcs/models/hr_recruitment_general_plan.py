# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EmployeeRecruitmentGeneralPlan(models.Model):
    _name = 'hr.recruitment.general.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'General Recruitment Plan Details'

    name = fields.Char(string="Name",readonly=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    general_plan_ids = fields.One2many('hr.recruitment.general.plan.line','general_plan_id')





class EmployeeRecruitmentGeneralPlanLine(models.Model):
    _name = 'hr.recruitment.general.plan.line'

    general_plan_id = fields.Many2one('hr.recruitment.general.plan')
    job_id = fields.Many2one('hr.job')
    current_number = fields.Float(string="Current Number",compute="_compute_current_number")
    required_number = fields.Float(string="Required Number Hired")
    division = fields.Many2one('hr.department',domain="[('parent_id','=',False)]",string="Division")
    department = fields.Many2one('hr.department',domain="[('parent_id','=',division)]",string="Department")
    section = fields.Many2one('hr.department',domain="[('parent_id','=',department)]",string="Section")
    unit = fields.Many2one('hr.department',domain="[('parent_id','=',section)]",string="Unit")
    best_period_hring = fields.Date(string="Best Period For Hiring")
    required_year = fields.Float(string="Required Years For Experience")
    required_qualification = fields.Float(string="Required Qualification")
    duites_and_spec = fields.Html(compute="_compute_duites",readonly=False)


    def _compute_duites(self):
        for rec in self:
            rec.duites_and_spec = rec.job_id.description


    def _compute_current_number(self):
        for rec in self:
            count_emp = self.env['hr.employee'].search_count([('job_id','=',rec.job_id.id)])
            rec.current_number = count_emp    

