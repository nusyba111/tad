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

    # @api.onchange('leaves')
    # def adjust_leaves(self):
    #     # print('##################3leaves!')
    #     for plan in self:
    #         for leave in plan.leaves:
    #             # leave.is_plan = True
    #             leave.holiday_status_id = plan.leave_type.id
                # leave.employee_id = plan.employee_id.id
                # leave.state = 'planned'

                # leave.write({'is_plan': True})
                # print('#################lp',leave.is_plan)

    # @api.onchange('order_line')
    # def link_leaves_to_planning(self):
    #     for rec in self:
    #         for line in rec.order_line:
    #             line.leave.leave_planning=rec.id
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
    # notification_days_before_leave = fields.Integer("Notification Days Before Leave")


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
    # is_plan = fields.Boolean("Is Plan",compute='_compute_is_plan')
    state = fields.Selection(selection_add=[('planned', 'Planned')])
    linked_leave_planning = fields.Many2one('hr.leave.planning', 'Linked Leave Planning')

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

            # rec.message_post(subject="subject", body="body", partner_ids= partner_ids)
            # self.env['mail.message'].create({'email_from': self.env.user.partner_id.email,
            #                                  'author_id': self.env.user.partner_id.id,
            #                                  'model': 'mail.channel',
            #                                  'subtype_id': self.env.ref('mail.mt_comment').id,
            #                                  'body': "hgdd",
            #                                  # 'channel_ids': [(4, self.env.ref(
            #                                  #     'payment_request.channel_accountant_group').id)],
            #                                  # 'res_id': self.env.ref(
            #                                  #     'payment_request.channel_accountant_group').id,
            #                                  # 'recipient_ids': [(4, 3)]
            #                                  })



        # mail_values = {
        #     'email_from': self.email_from,
        #     'author_id': self.author_id.id,
        #     'model': None,
        #     'res_id': None,
        #     'subject': "subject",
        #     'body_html': "body",
        #     'auto_delete': True,
        # }
        # mail_values['recipient_ids'] = [(4, 3)]
        #
        # return self.env['mail.mail'].sudo().create(mail_values)




        # for leave in planned_leaves:
        #     if datetime.now().date() + relativedelta(
        #             days=leave.holiday_status_id.notification_days_before_leave) >= leave.request_date_from:
        #         print('###############################partner')
        #         # partners = []
        #         # partners.append(leave.employee_id.user_id.partner_id.id)
        #         # # self.message_post(body="your message", partner_ids=3)
        #         #
        #         # self.message_post(
        #         #     body=(_("E-Invoice is generated on %s by %s") % (fields.Datetime.now(), leave.employee_id.user_id.display_name))
        #         # )
        #         partner_ids = self.env['res.partner'].search([('id','=',leave.employee_id.user_id.partner_id.id)]).ids
        #         self.message_post(subject="subject", body="body", partner_ids=[(4, [partner_ids])])
                # @api.model
    # def _get_default_holiday_status(self):
    #     print(self.linked_leave_planning.id,'#######################gf')
    #     if self.linked_leave_planning:
    #         print('#######################gf22')
    #
    #         return self.linked_leave_planning.leave_type

    # state = fields.Selection([
    #     ('draft', 'To Submit'),
    #     ('planned', 'Planned'),
    #     ('cancel', 'Cancelled'),  # YTI This state seems to be unused. To remove
    #     ('confirm', 'To Approve'),
    #     ('refuse', 'Refused'),
    #     ('validate1', 'Second Approval'),
    #     ('validate', 'Approved')
    # ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False,
    #     help="The status is set to 'To Submit', when a time off request is created." +
    #          "\nThe status is 'To Approve', when time off request is confirmed by user." +
    #          "\nThe status is 'Refused', when time off request is refused by manager." +
    #          "\nThe status is 'Approved', when time off request is approved by manager.")

    # leave_planning = fields.Many2one('hr.leave.planning', 'Leave Planning')
    # holiday_status_id = fields.Many2one(
    #     "hr.leave.type", compute='_compute_from_employee_id', store=True, string="Time Off Type", required=True,
    #     readonly=False,
    #     default=_get_default_holiday_status,
    #     states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
    #             'validate': [('readonly', True)]},
    #     domain=[('valid', '=', True)])
    # line_id = fields.Many2one('hr.leave.planning.line', 'Leave Planning Line')

    # leave_line = fields.One2many('hr.leave.planning.line', 'leave')

    # @api.model
    # def create(self, vals):
    #     # linked_order_line=self.env['hr.leave.planning.line'].search([('leave.id', '=', vals['line_id'])])
    #     # print(vals,self._context.get('active'),'################################vals')
    #     result = super(HrLeave, self).create(vals)
    #     return result

    def action_show_leave(self):
        # action = self.env.ref('hr_holiday_planning.hr_leave_planning_action_window2').read()[0]
        # action['domain'] = [('id', '=', self.id)]
        # # print(self.id,'###################################id')
        # action['context'] = {
        #     'active_id': self._context.get('active'),
        #     'active_model': 'hr.leave',
        # }
        # return action

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_type': 'form',
            'view_mode': 'form',
            # 'views': [(view_id, 'form')],
            'target': 'current',
            'res_id': self.id,
            'context': dict(self._context),
        }

    def action_set_as_plan(self):
        self.state = 'planned'

    def action_set_as_draft(self):
        self.state = 'draft'

    def action_replan(self):
        action = self.env.ref('hr_holiday_planning.hr_leave_planning_action_window21').read()[0]
        # action['domain'] = [('id', '=', self.leave.id)]
        # print(self.date_from, '################df')
        # linked_line = self.env['hr.leave.planning.line'].search([('leave.id', '=', self.id)])
        # print(linked_line.id,'#############################id')
        action['context'] = {
            # 'active_id': self._context.get('active'),
            'active_model': 'hr.leave',
            'default_linked_leave_planning': self.linked_leave_planning.id,

            'default_date_from': self.date_from,
            'default_date_to': self.date_to,
            'default_is_plan': True,
            'default_holiday_status_id': self.holiday_status_id.id,

            'default_employee_id': self.employee_id.id,
            'default_request_date_from': self.date_from,
            'default_request_date_to': self.date_to,
            # 'default_leave_planning': vals['order_id'],
            # 'default_state': 'planned',
            # 'default_line_id': linked_line.id,

        }
        self.state = 'cancel'
        # self.unlink()
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

    '''
    @api.depends('holiday_type')
    def _compute_from_holiday_type(self):
        for holiday in self:
            # if holiday.linked_leave_planning:
            #     holiday.employee_id = holiday.linked_leave_planning.employee_id.id
            #     continue
            if holiday.holiday_type == 'employee':
                if not holiday.employee_id:
                    holiday.employee_id = self.env.user.employee_id
                holiday.mode_company_id = False
                holiday.category_id = False
            elif holiday.holiday_type == 'company':
                holiday.employee_id = False
                if not holiday.mode_company_id:
                    holiday.mode_company_id = self.env.company.id
                holiday.category_id = False
            elif holiday.holiday_type == 'department':
                holiday.employee_id = False
                holiday.mode_company_id = False
                holiday.category_id = False
            elif holiday.holiday_type == 'category':
                holiday.employee_id = False
                holiday.mode_company_id = False
            else:
                holiday.employee_id = self.env.context.get('default_employee_id') or self.env.user.employee_id
    '''

    '''
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for holiday in self:
            # if holiday.linked_leave_planning:
            #     holiday.holiday_status_id = holiday.linked_leave_planning.leave_type.id
            #     continue
            holiday.manager_id = holiday.employee_id.parent_id.id
            if holiday.employee_id.user_id != self.env.user and self._origin.employee_id != holiday.employee_id:
                holiday.holiday_status_id = False
    '''

    # @api.depends('holiday_status_id')
    # def _compute_state(self):
    #     # print('############0')
    #     for holiday in self:
    #         # print('############1')
    #         if holiday.linked_leave_planning:
    #             # print('############2')
    #
    #             holiday.state = 'planned'
    #             continue
    #         if self.env.context.get('unlink') and holiday.state == 'draft':
    #             # Otherwise the record in draft with validation_type in (hr, manager, both) will be set to confirm
    #             # and a simple internal user will not be able to delete his own draft record
    #             holiday.state = 'draft'
    #         else:
    #             holiday.state = 'confirm' if holiday.validation_type != 'no_validation' else 'draft'
    #
    # def _compute_is_plan(self):
    #     for holiday in self:
    #         if holiday.linked_leave_planning:
    #             holiday.is_plan = True
    #         else:
    #             holiday.is_plan = False

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
                    # type_id = self.env['hr.leave.planning'].search([('id','=',values.get('linked_leave_planning'))]).leave_type.id
                    # values['holiday_status_id'] = type_id
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



class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    
    annual_leave = fields.Boolean(string='Annual Leave')        



#
# class HrLeavePlanningLine(models.Model):
#     _name = 'hr.leave.planning.line'
#     _description = 'Hr Leave Planning Line'
#
#     date_from = fields.Datetime(
#         'Start Date', store=True, readonly=False, copy=False,
#         required=True, )
#     date_to = fields.Datetime(
#         'End Date', store=True, readonly=False, copy=False, required=True,
#
#     )
#     number_of_days = fields.Float(
#         'Duration (Days)', store=True, readonly=False, copy=False,related="leave.number_of_days"
#     )
#
#     name = fields.Text(string='Description')
#     # leave = fields.Many2one('hr.leave', string='Leave',ondelete='cascade')
#     leave = fields.Many2one('hr.leave', string='Leave')
#     order_id = fields.Many2one('hr.leave.planning', string='Order Reference', index=True, required=True,
#                                ondelete='cascade')
#     def unlink(self):
#         if self.leave:
#             self.leave.unlink()
#
#         return super(HrLeavePlanningLine, self).unlink()
#     # @api.constrains('date_from', 'date_to')
#     # def _check_rule_date_from(self):
#     #     print('############################3crdf')
#     #
#     #     if any(applicability for applicability in self
#     #            if applicability.date_to and applicability.date_from
#     #               and applicability.date_to < applicability.date_from):
#     #         raise ValidationError(_('The start date must be before the end date'))
#     @api.depends('leave')
#     def recalculate_leave(self):
#         print('#####################depends')
#         for rec in self:
#             if not rec.leave:
#                 linked_leave = self.env['hr.leave'].search([('line_id.id', '=', rec.id)])
#                 rec.leave=linked_leave.id
#
#     @api.onchange('date_from', 'date_to')
#     def link_leaves_to_planning(self):
#         # print('############################3')
#
#         # for line in self:
#         if self.date_to and self.date_from and self.date_to < self.date_from:
#             raise ValidationError(_('The start date must be before the end date'))
#         self.leave.date_from = self.date_from
#         self.leave.date_to = self.date_to
#         # print('#################dft', self.date_from, self.date_to)
#
#     @api.model
#     def create(self, vals):
#         # print(vals, '###########################')
#         #
#         # vals_array = []
#         # vals_array.append((0, 0, {
#         #     'date_from': self.date_from,
#         #     'date_to': self.date_to,
#         # }))
#         # print(vals['date_from'],'###################')
#         # print(self.date_from,'###################')
#         # print(self.date_from,'###################')
#         linked_order=self.env['hr.leave.planning'].search([('id', '=', vals['order_id'])])
#         leave_1 = self.env['hr.leave'].create({
#             'name': 'Doctor Appointment',
#             'employee_id': self.env.user.employee_id.id,
#             'date_from': vals['date_from'],
#             'request_date_from': vals['date_from'],
#             'date_to': vals['date_to'],
#             'request_date_to': vals['date_to'],
#             'leave_planning': vals['order_id'],
#             'is_plan': True,
#             'state': 'planned',
#             'holiday_status_id': linked_order.leave_type.id,
#
#             # 'number_of_days': 1,
#         })
#         # vals['number_of_days']= 8
#         vals['leave'] = leave_1.id
#         # print(leave_1.leave_planning.name, '################l')
#         result = super(HrLeavePlanningLine, self).create(vals)
#
#         # result.update({'leave': (0, 0, {
#         #     'date_from': self.date_from,
#         #     'date_to': self.date_to,
#         # })})
#         return result
#
#     def action_show_leave(self):
#         action = self.env.ref('hr_holiday_planning.hr_leave_planning_action_window2').read()[0]
#         action['domain'] = [('id', '=', self.leave.id)]
#         # print(self.id,'###################################id')
#         action['context'] = {
#             'active_id': self._context.get('active'),
#             'active_model': 'hr.leave',
#         }
#         return action
#
