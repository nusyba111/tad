# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EmployeeRecruitmentPlan(models.Model):
    _name = 'hr.recruitment.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Recruitment Plan Details'

    name = fields.Char(string="Name",readonly=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    plan_ids = fields.One2many('hr.recruitment.plan.line','plan_id')
    state = fields.Selection([('draft','Draft'),
        ('department_manager','Department Manager'),
        ('hr_manager','HR Manager'),
        ('secretary_general','Secretary General'),
        ('approved','Approved')],default='draft',string="State")


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'hr.recruitment.plan') or 'New'
        result = super(EmployeeRecruitmentPlan, self).create(vals)
        return result

    def action_confirm(self):
        self.write({'state':'department_manager'})  


    def action_dept_approve(self):
        self.write({'state':'hr_manager'})   

    def action_hr_manager(self):
        self.write({'state':'secretary_general'})  

    def action_secretary(self):
        self.write({'state':'approved'})
        general_plan = self.env['hr.recruitment.general.plan'].search([('date_from','<=',self.date_from),('date_to','>=',self.date_to)])
        if not general_plan:
            # general = []
            general_plan_new = self.env['hr.recruitment.general.plan'].create({
                'name':'General Plan',
                'date_from':self.date_from,
                'date_to':self.date_to,
                # 'general_plan_ids':general
            
            })    
            for rec in self.plan_ids:
                # vals = (0, 0, 
                self.env['hr.recruitment.general.plan.line'].create({
                    'job_id': rec.job_id.id,
                    'current_number': rec.current_number,
                    'required_number': rec.required_number,
                    'division': rec.division.id,
                    'department': rec.department.id,
                    'section':rec.section.id,
                    'unit':rec.unit.id,
                    'best_period_hring':rec.best_period_hring,
                    'required_year':rec.required_year,
                    'required_qualification':rec.required_qualification,
                    'duites_and_spec':rec.duites_and_spec,
                    'general_plan_id':general_plan_new.id})
        else:
            for rec in self.plan_ids:
                # vals = (0, 0, 
                self.env['hr.recruitment.general.plan.line'].create({
                    'job_id': rec.job_id.id,
                    'current_number': rec.current_number,
                    'required_number': rec.required_number,
                    'division': rec.division.id,
                    'department': rec.department.id,
                    'section':rec.section.id,
                    'unit':rec.unit.id,
                    'best_period_hring':rec.best_period_hring,
                    'required_year':rec.required_year,
                    'required_qualification':rec.required_qualification,
                    'duites_and_spec':rec.duites_and_spec,
                    'general_plan_id':general_plan.id})
                    
                # })
                # general.append(vals)
            


class EmployeeRecruitmentPlanLine(models.Model):
    _name = 'hr.recruitment.plan.line'

    plan_id = fields.Many2one('hr.recruitment.plan')
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
