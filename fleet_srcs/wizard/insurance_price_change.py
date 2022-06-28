# -*- coding: utf-8 -*-
###########
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from odoo.tools import *

class Insurance(models.Model):
    _name = 'insurance.price.change'
    _description = 'Create Invoice for new price'

    new_price=fields.Float('New Price' , required=True)
    date=fields.Datetime('Date')
    insurance=fields.Many

    def _compute_task_id(self):
        self.task = self.env['project.task'].browse(self.env.context.get('active_ids'))

    def create_invoice(self):
        invoice_vals = {
            'partner_id': self.supplier,
            'state': 'draft',
            'insurance_id': self.id,
            'invoice_date': self.date,
            'move_type': 'in_invoice',
            'invoice_line_ids': [0, 0, {
                'product_id': self.service,
                'quantity': 1,
                'price_unit': self.cost,
            }]
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)
