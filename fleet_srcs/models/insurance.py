from datetime import timedelta


from odoo import api, fields, models, _

class Insurance(models.Model):
    _name='insurance.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    serial_no=fields.Char(string="Serial NO:")
    branch=fields.Many2one('res.branch')
    cust_info=fields.Char('info')
    date=fields.Date(string='Date',tracking=True,required=True)
    supplier=fields.Many2one('res.partner',string='Supplier/Provider')
    order_no=fields.Float(string='Order#/Contract#')
    order_title=fields.Char(string='Order Title')
    requester=fields.Many2one('hr.employee',string='Requested By')
    department=fields.Many2one('hr.department',string='Department')
    service=fields.Char('test')
    insurance_request=fields.Boolean(string='1-Third Party Insurance Request طلب تأمين إجباري ')
    full_insurance=fields.Boolean(string='2-Full Insurance (Comprehensive) request طلب تامين شامل')
    current_price=fields.Boolean(string='3- Current Market Price Determining طلب تحديد سعر العربة الحالي بالسوق ')
    price_change=fields.Boolean(string='4- Vehicle Price Change Request طلب تعديل سعر العربة لعرض تأمين')
    other_service=fields.Text(string='5- Other Services (To Be Mentioned Here)')
    license_plate=fields.Char(string='Licence Plate',required=True)
    chassis_no = fields.Char(string='Chassis No', required=True)
    cost=fields.Char('test')
    start=fields.Date(string='Start',required=True)
    finish=fields.Date(string='Finish',required=True)
    estimated=fields.Float(string='Estimated Cost in SDG')
    state = fields.Selection([
        ('requester', 'Requester'),
        ('finance', 'Finance'),
        ('cancel','Cancel')
    ], default='requester', string='State',readonly=True)
    invoice_count=fields.Integer(string='Invoices', compute='_compute_invoices_ids',tracking=True)
    attachment = fields.Binary(string="Attachment", required=True)

    @api.model
    def create(self, vals):
        repair = super(Insurance, self).create(vals)
        for x in repair:
            x.repair_no = self.env['ir.sequence'].next_by_code('insurance.no')
        return repair

    def _compute_invoices_ids(self):
        for rec in self:
            invoice_ids = self.env['stock.picking'].search([('insurance_id', '=', self.id)])
            rec.invoice_count = len(invoice_ids)

    def to_finance(self):
        invoice_vals = {
            'partner_id': self.partner,
            'state': 'draft',
            'fuel_id':self.id,
            'invoice_date': self.date,
            'move_type':'out_invoice',
            'invoice_line_ids': [0, 0, {
                'product_id': self.fuel_type,
                'quantity': self.quantity,
                'price_unit': self.cost,
            }]
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)
        self.write({'state': 'finance'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

