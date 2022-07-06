# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrMission(models.Model):
	_name = 'hr.mission'
	_description = 'Allow Employee to request mission'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

	name = fields.Char(string='Number', required=True, readonly=True, copy=False, default='/')
	mission_type = fields.Many2one('hr.mission.type', required=True)
	type_of_mission = fields.Selection(related="mission_type.type")
	mission_country = fields.Many2one('res.country',required=True)
	mission_city = fields.Many2one('res.city',string="City")
	start_date = fields.Date(string='Start Date', required=True)
	end_date = fields.Date(string='End Date', required=True)
	mission_days = fields.Integer(string="Days ", compute="_compute_days", readonly=True)
	currency_id = fields.Many2one('res.currency', string="Currency", required=True,readonly=True )
	# allowance_amount = fields.Float('Allowance Amount', required=True)
	# total_amount = fields.Float('Total Amount',compute="_count_total_amount",readonly=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('submit', 'Waiting Department Manager approval'),
		('dept_approve', 'Waiting HR approval'),
		('approve', 'Approved'),
		('public_relation','Public Relation'),
		('canceled', 'Canceled'),
		('stop', 'Stoped'),
	], default='draft',
		track_visibility='always')
	reason = fields.Text(string='Reason', invisible=True, track_visibility='onchange')
	company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
	move_id = fields.Many2one('account.move', string='Receipt', copy=False)
	mission_account_id = fields.Many2one('account.account', string='Account', related='company_id.mission_account_id')
	mission_journal_id = fields.Many2one('account.journal', string='Journal', related='company_id.mission_journal_id')
	mission_line_ids = fields.One2many('hr.mission.line', 'mission_request_id', string="Line")
	responsible_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user)
	description = fields.Text("Reason of Mission",track_visibility='onchange')
	requestor_id = fields.Many2one('res.users', string='Mission Requestor', default=lambda self: self.env.user)
	travel_by = fields.Selection([('air','Air'),('car','Car')])
	stop_reason = fields.Char()
	purpose = fields.Char()
	lodging_type = fields.Selection([('special','Special'),('hotel','Hotel'),('host','Host')])
	stop_date = fields.Date()
	doner = fields.Many2one('res.partner',string="Doner",required=True)
	project = fields.Many2one('account.analytic.account',required=True, domain="[('type','=','project')]",string="Project")
	activity = fields.Many2one('account.analytic.account',required=True,domain="[('type','=','activity')]",string="Activity")
	location = fields.Many2one('account.analytic.account',required=True,domain="[('type','=','location')]",string="Location")
	coverage_ids = fields.One2many('hr.mission.coverage','mission_id')
	work_shop = fields.Boolean(string="Work Shop")
	training = fields.Boolean(string="Training")
	conferences = fields.Boolean(string="Conferences")
	rc_meeting = fields.Boolean(string="RC/RC Movement Meeting")
	attachment = fields.Binary(string="Attachment", required=True)
	air_company = fields.Many2one('res.partner',string="Air Company")
	date_from = fields.Date(string="Date From")
	date_to = fields.Date(string="Date To")

	@api.onchange('mission_type')
	def _get_currency(self):
		for rec in self:
			rec.currency_id = rec.mission_type.currency_id.id

	@api.depends('start_date', 'end_date')
	def _compute_days(self):
		for mission in self:
			if mission.start_date and mission.end_date:
				date1 = datetime.strptime(str(mission.start_date), "%Y-%m-%d")
				date2 = datetime.strptime(str(mission.end_date), "%Y-%m-%d")
				date3 = date2 - date1
				date = int(date3.days)
				mission.mission_days = date
			return mission.mission_days

	@api.onchange('start_date', 'end_date')
	def change_lines(self):
		if self.mission_line_ids:
			for line in self.mission_line_ids:
				line.start_date = self.start_date
				line.end_date = self.end_date

	def action_submit(self):
		self.write({'state': "submit"})

	def action_confirm(self):
		if self.travel_by == 'air':
			self.write({'state':'public_relation'})
		else:
			self.write({'state': "dept_approve"})

	def action_public_approve(self):
	    self.write({'state':'dept_approve'})		

	def action_approve(self):
		# self._create_move()
		self.write({'state': "approve"})

	@api.model
	def create(self, vals):
		"""
		A create method was inherited to create mission request.
		"""
		vals['name'] = self.env['ir.sequence'].get('hr.mission') or ' '
		res = super(HrMission, self).create(vals)
		return res

	def _create_move(self):
		move_obj = self.env['account.move']

		move_obj = self.env['account.move']
		for mission in self:
			if mission.mission_account_id and mission.mission_journal_id:
				lines = []
				for line in mission.mission_line_ids:
					lines.append((0, 0, {
						'name': mission.name,
						'partner_id': line.employee_id.address_home_id.id,
						'account_id': mission.mission_account_id.id,
						'price_unit': line.total_amount,
						'quantity': 1,
					}))
				move_id = move_obj.create({
					'date': fields.date.today(),
					# 'partner_id': mission.partner_id.id,
					'ref': mission.name,
					'currency_id': mission.currency_id.id,
					'move_type': 'in_receipt',
					'invoice_line_ids': lines,
				})

				mission.move_id = move_id
			else:
				raise ValidationError(_("Please configure mission's account and journal in settings"))

	def action_set_to_draft(self):
		self.write({'state': 'draft'})

	# def name_get(self):
	#     result = []
	#     date = fields.Date.today()
	#     for mission in self:
	#         date = str(date)
	#         name = '(' + mission.name + ')' + '(' + date + ')'
	#         result.append((mission.id, name))
	#     return result

	def unlink(self):
		for request in self:
			if not request.state == 'draft':
				raise UserError(_('You cant not delete Request not in draft state.'))
		return super(HrMission, self).unlink()

	@api.constrains('end_date', 'start_date')
	def _check_dates(self):
		"""
		A method to check missions dates.
		"""
		for rec in self:
			if rec.end_date < rec.start_date:
				raise ValidationError(_("The end date should be grater than start date !"))


class HrMissionLine(models.Model):
	_name = 'hr.mission.line'

	employee_id = fields.Many2one('hr.employee', "Employee", required=True)
	department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
									store=True, readonly=True)
	name = fields.Text(string='Description')
	job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Position', store=True, readonly=True)
	mission_request_id = fields.Many2one('hr.mission', 'Mission')
	start_date = fields.Date(string='Start Date', required=True)
	end_date = fields.Date(string='End Date', required=True)
	mission_days = fields.Integer(string="Days ", compute="_compute_days_line", readonly=True)
	allowance_amount = fields.Float('Allowance Amount', compute="_get_amount",required=True)
	total_amount = fields.Float('Total Amount', compute="_compute_total_amount", readonly=True)

	@api.depends('mission_request_id.mission_type')
	def _get_amount(self):
		for rec in self:
			print("hi")
			rec.allowance_amount = 0
			if rec.mission_request_id.mission_type.Per_Dem == "fix_amount":
				rec.allowance_amount = rec.mission_request_id.mission_type.amount
			if rec.mission_request_id.mission_type.Per_Dem == "fix_job":
				if not rec.mission_request_id.mission_type.amount_job_id.mapped('amount'):
					raise UserError("Please Add Amount")
				rec._get_employee_amount()
			if rec.mission_request_id.mission_type.Per_Dem == "formula":
				rec.allowance_amount = rec.mission_request_id.mission_type.formula.compute_rule_amount(rec.employee_id)
	
	def _get_employee_amount(self):
		if self.employee_id:
			employee_job = self.employee_id.job_id
			amount_job = self.mission_request_id.mission_type.amount_job_id.search([('job_id','=',employee_job.id)])
			self.allowance_amount = amount_job.amount if amount_job else 0
		
	@api.depends('start_date', 'end_date')
	def _compute_days_line(self):
		for line in self:
			if line.start_date and line.end_date:
				date1 = datetime.strptime(str(line.start_date), "%Y-%m-%d")
				date2 = datetime.strptime(str(line.end_date), "%Y-%m-%d")
				date3 = date2 - date1
				date = int(date3.days)
				line.mission_days = date + 1
			return line.mission_days

	@api.depends('mission_days', 'allowance_amount')
	def _compute_total_amount(self):
		for line in self:
			if line.mission_days and line.allowance_amount:
				totalamount = line.mission_days * line.allowance_amount
				line.total_amount = totalamount
			else:
				line.total_amount = 0.0
		return line.total_amount




class StopMission(models.TransientModel):
	_name = 'hr.mission.stop'

	stop_date = fields.Date(default=fields.Date.today())
	stop_reason = fields.Text(required=True)
	mission_id = fields.Many2one('hr.mission')

	def action_stop_apply(self):
		if self.stop_date:
			self.mission_id.write({
				'stop_date':self.stop_date,
				'stop_reason':self.stop_reason,
				'state': 'stop',
			})


class MissionCoverage(models.Model):
	_name = 'hr.mission.coverage'

	mission_id = fields.Many2one('hr.mission')
	product = fields.Many2one('product.product',string="Service",domain="[('type','=','service')]")
	partial_coverage = fields.Boolean(string="Partial Coverage")
	complete_coverage = fields.Boolean(string="Completely Coverage")
	uncoverage = fields.Boolean(string="UnCoverage")
	amount = fields.Float(string="Amount")





