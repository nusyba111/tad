from datetime import timedelta


from odoo import api, fields, models, _

class Insurance(models.Model):
    _name='insurance.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='serial_no'

    serial_no=fields.Char(string="Serial NO:",readonly=True)
    branch=fields.Many2one('res.branch')
    cust_info=fields.Char('info')
    date=fields.Date(string='Date',tracking=True,required=True)
    supplier=fields.Many2one('res.partner',string='Supplier/Provider')
    order_no=fields.Float(string='Order#/Contract#')
    order_title=fields.Char(string='Order Title')
    requester=fields.Many2one('hr.employee',string='Requested By')
    department=fields.Many2one('hr.department',string='Department')
    service=fields.Char('test')
    insurance_request=fields.Boolean(string='1-Third Party Insurance Request ')
    full_insurance=fields.Boolean(string='2-Full Insurance (Comprehensive) request')
    vehicle=fields.Many2one('fleet.vehicle',string='Fleet')
    service=fields.Many2one('product.product',string='Service',required=True,domain="[('detailed_type','=','service')]")
    license_plate=fields.Char(string='Licence Plate',related='vehicle.license_plate',readonly=True)
    chassis_no = fields.Char(string='Chassis No',related='vehicle.vin_sn', readonly=True)
    cost=fields.Char('test')
    start=fields.Date(string='Start',required=True)
    finish=fields.Date(string='Finish',required=True)
    estimated=fields.Float(string='Estimated Cost in SDG')
    state = fields.Selection([
        ('requester', 'Requester'),
        ('finance', 'Finance'),
        ('cancel','Cancel')
    ], default='requester', string='State',readonly=True)
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoices_ids',tracking=True)
    attachment = fields.Binary(string="Attachment", required=True)
    analytic_activity_id = fields.Many2one('account.analytic.account', 'Output/Activity',
                                           domain="[('type','=','activity')]")
    account_id = fields.Many2one('account.account', string='Account',
                                 domain="[('internal_group','in',['expense','asset'])]")
    project_id = fields.Many2one('account.analytic.account', string='Project', domain="[('type','=','project')]")

    @api.model
    def create(self, vals):
        repair = super(Insurance, self).create(vals)
        for x in repair:
            x.serial_no = self.env['ir.sequence'].next_by_code('insurance.no')
        return repair

    def _compute_invoices_ids(self):
        for rec in self:
            invoice_ids = self.env['account.move'].search([('insurance_id', '=', self.id)])
            print('ttttt')
            rec.invoice_count = len(invoice_ids)

    def to_finance(self):
        invoice_vals = {
             'partner_id': self.supplier,
             'state': 'draft',
             'insurance_id':self.id,
             'invoice_date': self.date,
             'move_type':'in_invoice',
             'invoice_line_ids': [0, 0, {
                 'product_id': self.service,
                 'account_id': self.account_id,
                 'analytic_account_id': self.project_id,
                 'activity_id': self.analytic_activity_id,
                 'quantity': 1,
                 'price_unit': self.cost,
             }]
         }
        invoice = self.env['account.move'].sudo().create(invoice_vals)
        print('iiiiii',invoice)
        self.write({'state': 'finance'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

class Invoice(models.Model):
    _inherit = 'account.move'

    insurance_id = fields.Many2one('insurance.service', 'Insurance Reference', readonly=True)