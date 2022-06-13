# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrApplicant(models.Model):
    """"""
    _inherit = 'hr.applicant'

    def prepare_employee_date(self, applicant, contact_name='', address_id=False):
        """
        A method to prepare employee data.
        """
        rec = super(HrApplicant, self).prepare_employee_date(self)
        rec.update({
            'grade_id': applicant.grade_id.id,
            'level_id': applicant.level_id.id,
            'wage': applicant.wage,
        })
        return rec
