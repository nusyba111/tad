from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError, ValidationError
from odoo.tools.translate import html_translate


class HrWageProcessBatch(models.Model):
    _name = 'hr.wage.process.batch'
    _inherit = ['mail.thread']
    _description = "HR Wage Process Batch"

    name = fields.Char(default="Draft")
    batch_type = fields.Selection([('all_staff', 'All Staff'),('employee', 'Employee'),
        ('selected_employee', 'Selected Employees')],
        string="Batch Type", default='all_staff', track_visibility='onchange', copy=False, )
    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_wage_process_batch_rel', 'employee_id', 'batch_id', string="Employees")
    contract_id = fields.Many2one(related='employee_id.contract_id', readonly=True, store=True)

    type = fields.Selection([('promotion', 'Promotion'),
                             ('increment', 'Increment'), ('redLine', 'Red Line')],
                            default="redLine")
    # red_line_type = fields.Selection([('fix_amount', 'Fix Amount'),
    #                                   ('percentage', 'Percentage'), ],
    #                                  default="fix_amount", required=True)
    wage = fields.Float(string='New Wage', store=True)
    percentages = fields.Integer(string="percentage (%)", default=1)
    wage_process_ids = fields.One2many('hr.wage.process','batch_id',string='process batch')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('approve', 'Approve'),
                              ('refused', 'Refused')], default='draft', track_visibility='onchange')

    def action_set_to_confirm(self):
        """
        A method to confirm batch wage.
        """
        self.write({'state': 'confirm'})
        for rec in self.wage_process_ids:
            rec.action_set_to_confirm()

    def action_set_to_approve(self):
        """
        A method to approve batch wage.
        """
        self.write({'state': 'approve'})
        for rec in self.wage_process_ids:
            rec.action_set_to_approve()

    @api.model
    def create(self, values):
        """
        Inherit method to increase batch wage depend on wage increase type.
        """
        values['name'] = self.env['ir.sequence'].get('wage.process.redLine.batch') or 'NEW'
        res = super(HrWageProcessBatch, self).create(values)
        wage_batch = self.search([('id', '=', res.id)])
        # if self.red_line_type == 'percentage':
        #     increase_amount = wage_batch.current_wage * self.percentages / 100
        #     self.wage = wage_batch.current_wage + increase_amount
        if wage_batch.batch_type == 'employee':

            self.env['hr.wage.process'].create({'batch_id': wage_batch.id, 'employee_id': wage_batch.employee_id.id, 'contract_id': wage_batch.contract_id.id,
                    'current_grade': wage_batch.contract_id.grade_id.id, 'current_level': wage_batch.contract_id.level_id.id,
                    'current_wage': wage_batch.contract_id.wage,
                    'type': wage_batch.type,
                    'percentages': wage_batch.percentages,
                    'wage': wage_batch.wage,
                    })
        elif wage_batch.batch_type == 'all_staff':
            employees = self.env['hr.employee'].search([])
            for emp in employees:
                self.env['hr.wage.process'].create({'batch_id':wage_batch.id, 'employee_id': emp.id,
                                                    'contract_id': emp.contract_id.id,
                                                    'current_grade': emp.contract_id.grade_id.id,
                                                    'current_level': emp.contract_id.level_id.id,
                                                    'current_wage': emp.contract_id.wage,
                                                    'type': wage_batch.type,
                                                    'percentages': wage_batch.percentages,
                                                    'wage': wage_batch.wage,
                                                    })

        elif wage_batch.batch_type == 'selected_employee':
            for rec in wage_batch.employee_ids:
                self.env['hr.wage.process'].create({'batch_id': wage_batch.id, 'employee_id': rec.id,
                                                    'contract_id': rec.contract_id.id,
                                                    'current_grade': rec.contract_id.grade_id.id,
                                                    'current_level': rec.contract_id.level_id.id,
                                                    'current_wage': rec.contract_id.wage,
                                                    'type': wage_batch.type,
                                                    'percentages': wage_batch.percentages,
                                                    'wage': wage_batch.wage,
                                                    })

        return res

    def action_set_to_refused(self):
        """
        A method to refuse batch wage.
        """
        self.write({'state': 'refused'})
        for rec in self.wage_process_ids:
            rec.action_set_to_refused()

    def action_set_to_draft(self):
        """
        A method to reset wage draft.
        """
        self.write({'state': 'draft'})
        for rec in self.wage_process_ids:
            rec.action_set_to_draft()

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        """
        A method to change batch wage, grade and level in case contract was change.
        """
        for rec in self.wage_process_ids:
            if rec.contract_id:
                rec.current_wage = rec.contract_id.wage
                rec.current_grade = rec.contract_id.grade_id
                rec.current_level = rec.contract_id.level_id

    def unlink(self):
        """
        Deny unlink when record not in draft state.
        """
        for rec in self:
            if rec.state not in ('draft',):
                raise UserError(_('You can not delete record not in draft state.'))
        return super(HrWageProcessBatch, self).unlink()













