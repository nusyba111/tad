from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, AccessError, ValidationError
from dateutil.relativedelta import relativedelta


class Contracts(models.Model):
    """"""
    _inherit = 'hr.contract'

    grade_id = fields.Many2one('hr.grade', string='Grade', related='employee_id.grade_id', store=True,readonly=False,
                               ondelete='restrict')
    level_id = fields.Many2one('hr.level', string='Degree', domain="[('grade_id','=', grade_id)]", store=True,readonly=False,
                               related='employee_id.level_id', ondelete='restrict')
    wage = fields.Monetary(related='level_id.wage', readonly=True, store=True, required=False)

    # @api.onchange('grade_id')
    # def _onchange_grade_id(self):
    #     line_ids =[]
    #     for l in self.line_ids.filtered(lambda line: line.grade_related):
    #         line_ids.append((2,l._origin.id))
    #     if self.grade_id and self.grade_id.line_ids:
    #         for line in self.grade_id.line_ids:
    #         	line_ids.append(
    #                         (0, 0, {
    #                             'amount_deduct': line.amount_deduct,
    #                             'allow_deduct': line.allow_deduct.id,
    #                             'grade_related': True,
    #                         }))
    #     self.line_ids = line_ids

