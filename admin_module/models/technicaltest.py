# -*- coding: utf-8 -*-
# from dateutil.utils import today
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class SaleOrderTest(models.Model):
    _inherit = 'sale.order'
    # _rec_name = 'level_id'

    employee_id = fields.Many2one('hr.employee', string='employee')
    job_pos = fields.Char(string='Job Position', related='employee_id.job_title')
    level_id = fields.Many2one('discount.level', string='Discount Level')
    payment_mode = fields.Selection([('cash', 'Cash'), ('installments', 'Installments')], string='Payment Mode',
                                    default='cash')
    installment_tab_ids = fields.One2many('sale.line', 'line_sale_id', string='installment', )
    total = fields.Float(string='Total', compute='installment_constrain')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('manager_approval', 'Manager Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         res.append((rec.id, '%s from %s' % (rec.job_pos, rec.level_id)))
    #     return res

    def _action_confirm(self):
        return self.write({'state': 'manager_approval'})

    @api.onchange('installment_tab_ids')
    def installment_constrain(self):
        for rec in self:
            sum = 0.0
            for x in self.installment_tab_ids:
                if x.amount:
                    sum += x.amount
                    self.total = sum
                    print(self.total)
            if self.total > rec.amount_total:
                raise UserError(
                    _("Installment Amount is equal to total sale order amount your installment is finished!"))


class SaleOrderLine(models.Model):
    _name = 'sale.line'

    line_sale_id = fields.Many2one('sale.order', string='Installments')
    date = fields.Date(string='Date')
    name = fields.Char(string='Name')
    amount = fields.Float(string='Amount')


class DiscountPolicy(models.Model):
    _name = 'discount.policy'

    active_date = fields.Date(string='Active Date')


class DiscountLevel(models.Model):
    _name = 'discount.level'
    _rec_name = 'level_name'

    level_name = fields.Char(string='Discount Level')
