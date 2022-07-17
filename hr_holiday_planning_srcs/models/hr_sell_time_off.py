# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class SellTimeOff(models.Model):
	_name = 'sell.time.off'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'sequence'

	def _get_default_company_id(self):
		return self._context.get('force_company', self.env.user.company_id.id)

	sequence = fields.Char(string='Code', readonly=True)
	request_date = fields.Date(string="Request Date",default=fields.Date.today())
	employee_id = fields.Many2one('hr.employee',string="Employee Name")
	department_id = fields.Many2one('hr.department',string="Department")
	job_id = fields.Many2one('hr.job',string="Job Title")
	address = fields.Char(string="Home Address",compute='_get_employee_data', readonly=False)
	contract_start_date = fields.Date('Contract Start Date', compute="_get_employee_data", tracking=True,
		help="Start date of the contract.")

	total_time_off = fields.Float(string="Remaining Days",compute="_compute_total_timeoff",store=True)
	days_to_sell = fields.Float(string="Days To Sell")
	total_amount = fields.Float(string="Total Amount",compute="_compute_total_amount")
	company_id = fields.Many2one('res.company', string='Company',default=_get_default_company_id)
	state = fields.Selection([
		('draft', 'Draft'),
		('hr_manager','HR Manager'),
		('finance','Finance Manager'),
		# ('wait_dept_approve', 'Waiting Department Manager Approval'),
		# ('wait_hr_approve', 'Waiting HR Approval'),
		# ('wait_gm_approve', 'Waiting GM Approval'),
		('approve', 'Approved'),
		('cancel','Cancel'),],default='draft')
	paid = fields.Boolean(default=False)
	payslip_id = fields.Many2one('hr.payslip')
	sell_coverage = fields.One2many('leave.sell.coverage','leave_sell_id',string="Sell Coverage")
	
	@api.model
	def create(self, vals):
		record = super(SellTimeOff, self).create(vals)
		record.sequence =  self.env['ir.sequence'].get('hr.leave.sell') or ' '
		return record

	@api.onchange('employee_id')
	def _get_employee_data(self):
		for rec in self:
			if rec.employee_id:
				rec.job_id = rec.employee_id.job_id
				rec.department_id = rec.employee_id.department_id
				rec.contract_start_date = rec.employee_id.contract_id.date_start
				rec.address = rec.employee_id.address_home_id.name
			else:
				rec.job_id = False
				rec.department_id = False
				rec.contract_start_date = False
				rec.address = False

	@api.depends('employee_id','days_to_sell')
	def _compute_total_amount(self):
		for rec in self:
			amount = 0.0
			if rec.employee_id and rec.days_to_sell > 0.0:
				day_wage = rec.employee_id.contract_id.wage /30
				amount =  day_wage * rec.days_to_sell
				rec.total_amount = amount
			else:
				rec.total_amount = 0

	@api.depends('employee_id')
	def _compute_total_timeoff(self):
		for rec in self:
			rec.total_time_off = 0.0
			if rec.employee_id:
				alloaction = self.env['hr.leave.allocation'].search([('employee_id','=',rec.employee_id.id),
					('holiday_status_id.can_be_sold','=',True)])
				if alloaction:
					for alloc in alloaction:
						rec.total_time_off += alloc.number_of_days_display - alloc.leaves_taken
				else:
					rec.total_time_off = 0.0
			else:
				rec.total_time_off = 0.0
	
	def action_submit(self):
		self.write({'state':'hr_manager'})    

	def action_finance_approve(self):
		self.write({'state':'finance'})

	def action_draft(self):
		self.write({'state':'draft'})    

	def action_approve(self):
		self.state = 'approve'
					

class HolidayAllocation(models.Model):
	_inherit = "hr.leave.allocation"

	@api.depends('employee_id', 'holiday_status_id', 'taken_leave_ids.number_of_days', 'taken_leave_ids.state')
	def _compute_leaves(self):
		for allocation in self:
			allocation.max_leaves = allocation.number_of_hours_display if allocation.type_request_unit == 'hour' else allocation.number_of_days
			allocation.leaves_taken = sum(taken_leave.number_of_hours_display if taken_leave.leave_type_request_unit == 'hour' else taken_leave.number_of_days\
				for taken_leave in allocation.taken_leave_ids\
				if taken_leave.state == 'validate')

			if allocation.holiday_status_id.can_be_sold:
				sell_leaves = self.env['sell.time.off'].search([('employee_id','=',allocation.employee_id.id),
				('state','=','approve')])

				days_to_sell = 0.0
				if sell_leaves:
					for sell in sell_leaves:
						days_to_sell += sell.days_to_sell

				allocation.leaves_taken = sum(taken_leave.number_of_hours_display if taken_leave.leave_type_request_unit == 'hour' else taken_leave.number_of_days\
					for taken_leave in allocation.taken_leave_ids\
					if taken_leave.state == 'validate')

				if days_to_sell > 0.0:
					allocation.leaves_taken = allocation.leaves_taken + days_to_sell



class LeaveSellCovarge(models.Model):
    _name = 'leave.sell.coverage'

    leave_sell_id = fields.Many2one('sell.time.off',string="Sell Time Off")
    project = fields.Many2one('account.analytic.account',string="Project",domain="[('type','=','project')]")
    activity = fields.Many2one('account.analytic.account',domain="[('type','=','activity')]",string="Activity")
    location = fields.Many2one('account.analytic.account',domain="[('type','=','location')]",string="Location")
    doner_id = fields.Many2one('res.partner',string="Doner")
    percentage_of_covering = fields.Float(string="Percentage Of Covering")