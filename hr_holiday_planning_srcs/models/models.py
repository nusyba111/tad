# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.fields import datetime
from dateutil.relativedelta import relativedelta

class HrLeavePlanning(models.Model):
    _name = 'hr.leave.planning'

    @api.model
    def _get_first_annual_leave(self):
        return self.env['hr.leave.type'].search([('annual_leave', '=', True)], limit=1)

    name = fields.Char()
    leave_type = fields.Many2one('hr.leave.type', 'Leave Type',default=_get_first_annual_leave)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=False,
                                  default=lambda self: self.env.user.employee_id.id)
    date_from = fields.Date(string='Date from', store=True,default=lambda self: datetime.now().date().replace(month=1, day=1))
    date_to = fields.Date(string='Date To', store=True,default=lambda self: datetime.now().date().replace(month=12, day=31))
    # order_line = fields.One2many('hr.leave.planning.line', 'order_id')
    leaves = fields.One2many('hr.leave', 'linked_leave_planning')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'hr.leave.planning') or 'New'
        result = super(HrLeavePlanning, self).create(vals)
        return result


    state = fields.Selection([
        ('draft', 'Submit'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('validated', 'Validated'),
        ('canceled', 'Canceled'),
    ], string='Status', readonly=True, default='draft', )

    def action_set_to_draft(self):
        self.write({'state': "draft"})

    def action_set_to_canceled(self):
        self.write({'state': "canceled"})

    def action_set_to_confirmed(self):
        self.write({'state': "confirmed"})

    def action_set_to_approved(self):
        self.write({'state': "approved"})

    def action_set_to_validated(self):
        self.write({'state': "validated"})


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    need_planning = fields.Boolean("Need Planning")
    annual_leave = fields.Boolean(string='Annual Leave')


class LeaveReportCalendar(models.Model):
    _inherit = "hr.leave.report.calendar"
    holiday_status_id = fields.Many2one(
        "hr.leave.type")
    def init(self):
        tools.drop_view_if_exists(self._cr, 'hr_leave_report_calendar')
        self._cr.execute("""CREATE OR REPLACE VIEW hr_leave_report_calendar AS
        (SELECT 
            row_number() OVER() AS id,
            CONCAT(em.name, ': ', hl.duration_display) AS name,
            hl.date_from AS start_datetime,
            hl.date_to AS stop_datetime,
            hl.employee_id AS employee_id,
            hl.holiday_status_id AS holiday_status_id,
            hl.state AS state,
            em.company_id AS company_id,
            CASE
                WHEN hl.holiday_type = 'employee' THEN rr.tz
                ELSE %s
            END AS tz
        FROM hr_leave hl
            LEFT JOIN hr_employee em
                ON em.id = hl.employee_id
            LEFT JOIN resource_resource rr
                ON rr.id = em.resource_id
        WHERE 
            hl.state IN ('confirm', 'validate', 'validate1','planned')
        ORDER BY id);
        """, [self.env.company.resource_calendar_id.tz or self.env.user.tz or 'UTC'])


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    is_plan = fields.Boolean("Is Plan")
    state = fields.Selection(selection_add=[('planned', 'Planned'),('finance_approve','Finance Approve'),('cancel','Cancel')])
    linked_leave_planning = fields.Many2one('hr.leave.planning', 'Linked Leave Planning')
    coverage_ids = fields.One2many('hr.leave.coverage','leave_id',)
    annual_leave = fields.Boolean(related="holiday_status_id.annual_leave")
    payment_request_id = fields.Many2one('payment.request')
    journal_id = fields.Many2one('account.journal')



    @api.onchange('employee_id')
    def _get_coverage_ids(self):
        for coverag in self.employee_id.contract_id.salary_plan:
            coverag_vals = {
                'project':coverag.covered_by.id,
                'activity':coverag.activity.id,
                'location':coverag.location.id,
                'doner_id':coverag.doner_id.id,
                'leave_id':self.id
            }
            the_coverage = self.env['hr.leave.coverage'].create(coverag_vals)




    @api.constrains('request_date_from', 'request_date_to')
    def _check_rule_date_from(self):
        for line in self:
            if line.linked_leave_planning:
                if line.request_date_from < line.linked_leave_planning.date_from \
                        or line.request_date_to > line.linked_leave_planning.date_to:
                    raise ValidationError(_('Dates of lines should be in between parent dates!'))

    def notify_before_leave(self):

        manager_group = self.env.ref("hr_holidays.group_hr_holidays_manager")
        hr_managers = []
        for user in manager_group[0].users:
            if user:
                hr_managers.append(user.partner_id.id)

        planned_leaves = self.env['hr.leave'].search([('state', '=', 'planned')])
        for leave in planned_leaves:
            if datetime.now().date() + relativedelta(
                    days=leave.holiday_status_id.notification_days_before_leave) >= leave.request_date_from:

                leave_partner = leave.employee_id.user_id.partner_id
                leave_partner_manager = leave.employee_id.parent_id.user_id.partner_id
                ids = hr_managers.copy()
                # print(ids, '###############################ids')

                if leave_partner.id and leave_partner.id not in hr_managers:
                    ids.append(leave_partner.id)
                if leave_partner_manager.id and leave_partner_manager.id not in hr_managers:
                    ids.append(leave_partner_manager.id)

                sender = leave.env.user.partner_id
                # print(ids,'###############################ids')
                leave.message_post(subject="Leave alert", body="This Leave request planned to start at "+str(leave.request_date_from), partner_ids= ids,message_type='email',author_id=sender.id)

                for receipt_partner_id in ids:
                    previous_channel_list = self.env['mail.channel'].search(
                        [('name', '=', 'Chat with: ' + str(receipt_partner_id))])
                    channel = previous_channel_list[0] if len(previous_channel_list) > 0 else self.env[
                        'mail.channel'].create({
                        'name': 'Chat with: ' + str(receipt_partner_id),
                        'channel_partner_ids': [(4, receipt_partner_id)]
                    })
                    # print('###############receipt_partner_id',receipt_partner_id)
                    leave.message_post(
                        subject='Leave alert',
                        message_type='notification',
                        body="This Leave request planned to start at "+str(leave.request_date_from),
                        channel_ids=channel.ids)

            

    def action_show_leave(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id,
            'context': dict(self._context),
        }

    def action_set_as_plan(self):
        self.state = 'planned'

    def action_set_as_draft(self):
        self.state = 'draft'

    def action_replan(self):
        action = self.env.ref('hr_holiday_planning_srcs.hr_leave_planning_action_window21').read()[0]
        action['context'] = {
            'active_model': 'hr.leave',
            'default_linked_leave_planning': self.linked_leave_planning.id,

            'default_date_from': self.date_from,
            'default_date_to': self.date_to,
            'default_is_plan': True,
            'default_holiday_status_id': self.holiday_status_id.id,

            'default_employee_id': self.employee_id.id,
            'default_request_date_from': self.date_from,
            'default_request_date_to': self.date_to,

        }
        self.state = 'cancel'
        return action

    def action_confirm(self):
        if self.state == 'planned':
            self.state = 'draft'
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Time off request must be in Draft state ("To Submit") in order to confirm it.'))
        self.write({'state': 'confirm'})
        holidays = self.filtered(lambda leave: leave.validation_type == 'no_validation')
        if holidays:
            # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
            holidays.sudo().action_validate()
        self.activity_update()
        return True

        

    def action_finance_approval(self):
        self.write({'state':'finance_approve'})
        line_list = []
        for line in self.coverage_ids:
            request_line = {
              'project_id':line.project.id,
              'analytic_activity_id':line.activity.id,
              'donor_id':line.doner_id.id,
              'request_amount':self.employee_id.level_id.leave_allowance,
            }
            line_list.append((0, 0, request_line))
        payment_request = self.env['payment.request'].create({
            'journal_id':self.journal_id.id,
            'total_amount':self.employee_id.level_id.leave_allowance,
            'Check_no':'',
            'check_date':fields.Date.today(),
            'reason':'Annual Leave Allowance',
            'budget_line_ids':line_list
            })
        self.payment_request_id = payment_request.id     

    def unlink(self):
        for rec in self:
            if rec.state == 'planned':
                rec.state = 'draft'
        error_message = _('You cannot delete a time off which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if not self.user_has_groups('hr_holidays.group_hr_holidays_user'):
            if any(hol.state != 'draft' and hol.state != 'planned' for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        else:
            for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm']):
                raise UserError(error_message % (state_description_values.get(holiday.state),))
        return super(HrLeave, self.with_context(leave_skip_date_check=True, unlink=True)).unlink()


    @api.model_create_multi
    def create(self, vals_list):
        """ Override to avoid automatic logging of creation """
        # print( '############################vals_list', vals_list)

        if not self._context.get('leave_fast_create'):
            leave_types = self.env['hr.leave.type'].browse(
                [values.get('holiday_status_id') for values in vals_list if values.get('holiday_status_id')])
            mapped_validation_type = {leave_type.id: leave_type.leave_validation_type for leave_type in leave_types}

            for values in vals_list:
                employee_id = values.get('employee_id', False)
                leave_type_id = values.get('holiday_status_id')
                # print(values.get('linked_leave_planning'),'################################llp',leave_types)
                # print(leave_type_id,'############################',mapped_validation_type)

                # Handle automatic department_id
                if not values.get('department_id'):
                    values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})

                # Handle no_validation
                # print()
                if mapped_validation_type[leave_type_id] == 'no_validation':
                    values.update({'state': 'confirm'})

                if 'state' not in values:
                    # To mimic the behavior of compute_state that was always triggered, as the field was readonly
                    values['state'] = 'confirm' if mapped_validation_type[leave_type_id] != 'no_validation' else 'draft'

                # Handle double validation
                if mapped_validation_type[leave_type_id] == 'both':
                    self._check_double_validation_rules(employee_id, values.get('state', False))
                if values.get('linked_leave_planning'):
                    values['state'] = 'planned'
        holidays = super(HrLeave, self.with_context(mail_create_nosubscribe=True)).create(vals_list)

        for holiday in holidays:
            if not self._context.get('leave_fast_create'):
                # Everything that is done here must be done using sudo because we might
                # have different create and write rights
                # eg : holidays_user can create a leave request with validation_type = 'manager' for someone else
                # but they can only write on it if they are leave_manager_id
                holiday_sudo = holiday.sudo()
                holiday_sudo.add_follower(employee_id)
                if holiday.validation_type == 'manager':
                    holiday_sudo.message_subscribe(partner_ids=holiday.employee_id.leave_manager_id.partner_id.ids)

                if holiday.validation_type == 'no_validation':
                    # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
                    holiday_sudo.action_validate()
                    holiday_sudo.message_subscribe(partner_ids=[holiday._get_responsible_for_approval().partner_id.id])
                    holiday_sudo.message_post(body=_("The time off has been automatically approved"),
                                              subtype_xmlid="mail.mt_comment")  # Message from OdooBot (sudo)
                elif not self._context.get('import_file'):
                    holiday_sudo.activity_update()
        return holidays


class LeaveCoverage(models.Model):
    _name = 'hr.leave.coverage'

    leave_id = fields.Many2one('hr.leave',string="Leave")
    project = fields.Many2one('account.analytic.account',string="Project",domain="[('type','=','project')]")
    activity = fields.Many2one('account.analytic.account',domain="[('type','=','activity')]",string="Activity")
    location = fields.Many2one('account.analytic.account',domain="[('type','=','location')]",string="Location")    
    doner_id = fields.Many2one('res.partner',string="Doner")

    
