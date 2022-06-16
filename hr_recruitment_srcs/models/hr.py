# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import Warning, UserError


class HRRecuritmentApplication(models.Model):
    _inherit = 'hr.applicant'

    

    @api.constrains('job_id')
    def _check_employee_job_paln(self):
        recutment_plan = self.env['hr.recruitment.plan'].search([('date_from','<=',self.create_date),
            ('date_to','>=',self.create_date)])
        for line in recutment_plan.plan_ids:
            if line.job_id == self.job_id and line.current_number == line.required_number:
                raise UserError(_("Plan Current number for this job is equal to required number"))


