from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, AccessError, ValidationError
from dateutil.relativedelta import relativedelta


class HrEmplyee(models.Model):
    """"""
    _inherit = 'hr.employee'

    grade_id = fields.Many2one('hr.grade', string='Grade', store=True)
    level_id = fields.Many2one('hr.level', string='Degree', domain="[('grade_id','=', grade_id)]", store=True)
    wage = fields.Monetary(string='Expected Wage', related='level_id.wage', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
