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
    date=fields.Datetime('Date',required=True)
    insurance=fields.Many2one('insurance.service',compute='_compute_insurance_id')

    def _compute_insurance_id(self):
        self.insurance = self.env['insurance.service'].browse(self.env.context.get('active_ids'))

    def create_invoice(self):
        invoice_vals = {
            'partner_id': self.insurance.supplier,
            'state': 'draft',
            'insurance_id': self.insurance.id,
            'invoice_date': self.date,
            'move_type': 'in_invoice',
            'invoice_line_ids': [0, 0, {
                'product_id': self.insurance.service,
                'quantity': 1,
                'price_unit': self.new_price,
            }]
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)
