from datetime import timedelta


from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, AccessError
from collections import defaultdict
from odoo.exceptions import UserError, AccessError, ValidationError

from odoo.tools import float_compare, get_lang, format_date

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS

class Fueling(models.Model):
    _name='fuel.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='description'

    description=fields.Char(string="Description")
    branch=fields.Many2one('res.branch',string='Branch')
    date=fields.Date(string='Date',tracking=True,required=True)
    request_type=fields.Selection([('hq','HQ'),('employee','Employee'),('branch','Branch'),('partner','Partner')],
                                  string='Request Type',required=True,tracking=True)
    employee=fields.Many2one('hr.employee',string='Employee')
    partner=fields.Many2one('res.partner',string='Partner')
    vehicle=fields.Many2one('fleet.vehicle',string='Vehicle',required=True,tracking=True)
    department=fields.Many2one('hr.department',string='Department')
    fuel_id=fields.One2many('fuel.type','service_id','Fuel')
    driver=fields.Many2one('res.partner',string='Driver')
    odo_meter=fields.Float('Odometer',required=True)
    location=fields.Many2one('stock.location',string='Stock Location')
    state = fields.Selection([
        ('requester', 'Requester'),
        ('fleet_user', 'Fleet User'),
        ('fleet_manager', 'Fleet Manager'),
        ('finance', 'Finance'),
        ('cancel','Cancel')
    ], default='requester', string='State',readonly=True)
    transfer_count=fields.Integer(string='Stock Transfers', compute='_compute_transfers_ids',tracking=True)
    invoice_count=fields.Integer(string='Invoices', compute='_compute_invoices_ids',tracking=True)
    # new fields
    approve_name_id = fields.Many2one('res.users', string='Manager', readonly=True)
    fleet_user_id = fields.Many2one('res.users', string='HR Admin', readonly=True)
    total_amount = fields.Float(string="Total")
    analytic_activity_id = fields.Many2one('account.analytic.account', 'Output/Activity',
                                           domain="[('type','=','activity')]")
    account_id = fields.Many2one('account.account', string='Account', domain="[('internal_group','in',['expense','asset'])]")
    project_id = fields.Many2one('account.analytic.account', string='Project', domain="[('type','=','project')]")

    @api.onchange('fuel_id')
    def call_total(self):
        sum = 0.0
        for rec in self.fuel_id:
            sum += rec.total
            self.total_amount = sum

    # @api.depends('qty', 'price')
    # def compute_total(self):
    #     for line in self:
    #         line.total = line.qty * line.price


    @api.constrains('odo_meter')
    def odometer_constrains(self):
        if self.vehicle.odometer > self.odo_meter:
            raise ValidationError(_('Odometer value should be bigger than last odometer entered'))

    def _compute_transfers_ids(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('fuel_id', '=', self.id)])
            rec.transfer_count = len(picking_ids)

    def _compute_invoices_ids(self):
        for rec in self:
            invoice_ids = self.env['stock.picking'].search([('fuel_id', '=', self.id)])
            rec.invoice_count = len(invoice_ids)

    def to_user(self):
        self.vehicle.write({'odometer': self.odo_meter})
        self.write({'state': 'fleet_user'})
        self.fleet_user_id = self.env.user.id

    def to_manager(self):
        self.write({'state': 'fleet_manager'})
        self.approve_name_id = self.env.user.id

    def to_finance(self):
        if self.request_type == 'hq':
            self.write({'state': 'finance'})
        else:
            invoice_vals = {
                'partner_id': self.partner,
                'state': 'draft',
                'fuel_id':self.id,
                'invoice_date': self.date,
                'move_type':'out_invoice',
                'invoice_line_ids': [0, 0, {
                    'product_id': self.fuel_type,
                    'account_id':self.account_id,
                    'analytic_account_id':self.project_id,
                    'activity_id':self.analytic_activity_id,
                    'quantity': self.quantity,
                    'price_unit': self.cost,
                }]
            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            self.write({'state': 'finance'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def stock_request(self):

        stock_picking_vals = {'partner_id': self.create_uid.partner_id.id,
                              'location_id': self.location.id,
                              'location_dest_id': self.location.warehouse_id.wh_output_stock_loc_id.id,
                              'scheduled_date': self.date,
                              'picking_type_id': self.location.warehouse_id.out_type_id.id,
                              'fuel_id': self.id,
                              }
        picking = self.env['stock.picking'].create(stock_picking_vals)


        # Stock Move
        for line in self.fuel_id:
            stock_move_vals = {
                'product_id': line.fuel_type.id,
                'product_uom_qty': line.qty,
                'product_uom': line.fuel_type.product_tmpl_id.uom_id.id,
                'location_id': self.location.id,
                'name': line.fuel_type.name,
                'location_dest_id': self.location.warehouse_id.wh_output_stock_loc_id.id,
                'picking_id': picking.id,
                'spare_line_id': line.id,
            }
            move = self.env['stock.move'].create(stock_move_vals)



class FuelType(models.Model):
    _name='fuel.type'

    service_id=fields.Many2one('fuel.service')
    fuel_type = fields.Many2one('product.product', string='Fuel Type')
    onhand = fields.Float(string='On Hand', compute='compute_qty')
    qty = fields.Float(string='Quantity')
    uom = fields.Many2one('uom.uom', string='UoM', related='fuel_type.uom_id')
    price=fields.Float(string="Price",related='fuel_type.list_price',required=True)
    total = fields.Float(string='Total', compute='compute_total')

    @api.depends('qty','price')
    def compute_total(self):
        for line in self:
            line.total=line.qty*line.price

    @api.depends('fuel_type')
    def compute_qty(self):
        self.onhand = 0.0
        qty = 0
        for rec in self:
            quant_ids = self.env['stock.quant'].search(
                [('location_id', '=', rec.service_id.location.id),
                 ('product_id', '=', rec.fuel_type.id)])
            for quantity in quant_ids:
                qty += quantity.quantity
                rec.onhand = qty


class Picking(models.Model):
    _inherit = 'stock.picking'

    fuel_id = fields.Many2one('fuel.service', 'Fuel Reference', readonly=True)

class Invoice(models.Model):
    _inherit = 'account.move'

    fuel_id = fields.Many2one('fuel.service', 'Fuel Reference', readonly=True)
    insurance_id = fields.Many2one('insurance.service', 'Insurance Reference', readonly=True)

class FuelOdo(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    fuel_quantity=fields.Float(string='Fuel Quantity')
    fuel_uom=fields.Many2one('uom.uom',string='Fuel UOM')

class FuelTy(models.Model):
    _inherit = 'fleet.service.type'

    fuel=fields.Boolean(string='Fuel Service?')
