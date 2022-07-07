
from odoo import models, fields, api, _


class ExitPermission(models.Model):
    _name = 'maintainance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Create an Exit Form'
    _rec_name = 'sequence'
    _order = "date,state desc"

    sequence=fields.Char()
    date=fields.Datetime(string='Date')
    employee_id=fields.Many2one('hr.employee',string='Employee')
    department=fields.Many2one('hr.department',string='Department', related='employee_id.department_id')
    report_type=fields.Selection([('plumbing','Plumbing'),('electric','Electricity'),('other','Other(Specify')]
                                , string='Report Type',default='plumbing')
    complain_summary=fields.Text(string='Complain Summary' ,Tracking=True)
    admin_comment=fields.Text(string='Administration Comment' ,Tracking=True)
    service_comment=fields.Text(string='Administration Comment' ,Tracking=True)
    receipt_date=fields.Datetime('Reciept Date',required=True,Tracking=True)
    required_spares=fields.One2many('required.spare','main_id',string='Required Spares')
    required_service=fields.One2many('required.service','main_id',string='Required Services')
    address_to=fields.Many2one('res.partner',string='Addressed To',required=True)
    asset=fields.Many2one('account.asset',string='Asset Name',required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('admin', 'Administration Approve'),
        ('cancel', 'Cancel'),
        ('done', 'Done')], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.model
    def create(self, vals):
        maintainance = super(ExitPermission, self).create(vals)
        for x in maintainance:
            x.sequence = self.env['ir.sequence'].next_by_code('maintainance.no')
        return maintainance
    def to_admin(self):
        self.write({'state': 'admin'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_done(self):
        self.write({'state': 'done'})

    def generate_requisition(self):
        purchase_order_vals = purchase_order_lines_vals = {}
        purchase_order_vals = {
            'user_id': self.env.uid,
            'main_id': self.id
        }

        purchase_id = self.env['purchase.requisition'].create(purchase_order_vals)
        for rec in self.required_spares:
            purchase_order_lines_vals = {
                'product_id': rec.product_id.id,
                'requisition_id': purchase_id.id,
                'product_qty': rec.qty,
                'price_unit': rec.product_id.list_price,

            }
            self.env['purchase.requisition.line'].create(purchase_order_lines_vals)

    def generate_requisition_invoice(self):
        purchase_order_vals = purchase_order_lines_vals = {}
        purchase_order_vals = {
            'user_id': self.env.uid,
            'main_id': self.id
        }

        purchase_id = self.env['purchase.requisition'].create(purchase_order_vals)
        for rec in self:
            purchase_order_lines_vals = {
                'product_id': rec.service_id.id,
                'requisition_id': purchase_id.id,
                'product_qty': 1,
                'price_unit': rec.price,

            }
            self.env['purchase.requisition.line'].create(purchase_order_lines_vals)


class Spares(models.Model):
    _name='required.spare'

    main_id =fields.Many2one('maintainance.request')
    product_id=fields.Many2one('product.product', string='Spare')
    qty=fields.Float(string='Required Quantity', tracking=True)


class Services(models.Model):
    _name='required.service'

    main_id=fields.Many2one('maintainance.request')
    service_id=fields.Many2one('product.product',string='Service')
    technition_name=fields.Many2one('res.partner',string='Technition Name')
    price=fields.Float(string='Price')




class Requisition(models.Model):
    _inherit = "purchase.requisition"

    main_id = fields.Many2one('maintainance.request', 'Maintainance Reference')