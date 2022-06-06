from datetime import timedelta


from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, AccessError
from collections import defaultdict

from odoo.tools import float_compare, get_lang, format_date

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS

class Fueling(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    service_type_id=fields.Selection([('fuel','Refueling')],string='Refueling',default='fuel')
    fuel_type=fields.Many2one('product.product',string='Fuel Type',domain="[('detailed_type','=','service')]")
    quantity=fields.Float(string='Quantity')
    uom=fields.Many2one('uom.uom',string='UoM',related='fuel_type.uom_id')
    state = fields.Selection([
        ('requester', 'Requester'),
        ('fleet_user', 'Fleet User'),
        ('fleet_manager', 'Fleet Manager'),
        ('finance', 'Finance'),
        ('cancel','Cancel')
    ], default='requester', string='State',readonly=True)
    transfer_count=fields.Integer(string='Stock Transfers', compute='_compute_transfers_ids',tracking=True)


    def _compute_transfers_ids(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('fuel_id', '=', self.id)])
            rec.transfer_count = len(picking_ids)

    def to_user(self):
        self.write({'state': 'fleet_user'})

    def to_manager(self):
        self.write({'state': 'fleet_manager'})

    def to_finance(self):
        self.write({'state': 'finance'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def stock_request(self):
        # Stock Picking order entry
        stock_picking_vals = {'partner_id': self.create_uid.partner_id.id,
                              'location_id': self.source_warehouse_id.lot_stock_id.id,
                              'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                              'scheduled_date': self.date,
                              'picking_type_id': self.source_warehouse_id.int_type_id.id,
                              'repair_id': self.id,
                              }
        picking = self.env['stock.picking'].create(stock_picking_vals)

        stock_move_vals = {
            'product_id': self.fuel_type.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.uom.id,
            'location_id': self.source_warehouse_id.lot_stock_id.id,
            'name': self.fuel_type.name,
            'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
            'picking_id': picking.id,
        }
        move = self.env['stock.move'].create(stock_move_vals)

class Picking(models.Model):
    _inherit = 'stock.picking'

    fuel_id = fields.Many2one('fleet.vehicle.log.services', 'Fuel Reference', readonly=True)

class FuelOdo(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    fuel_quantity=fields.Float(string='Fuel Quantity')
    fuel_uom=fields.Many2one('uom.uom',string='Fuel UOM')