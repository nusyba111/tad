# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################
from datetime import timedelta


from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, AccessError
from collections import defaultdict
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare, get_lang, format_date

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS

class Repair(models.Model):
    _name = 'repair'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Create a job order'
    _order = "date,state desc"

    repair_no=fields.Char('Repair No:',readonly=True)
    fleet=fields.Many2one('fleet.vehicle',string='vehicle',required=True, tracking=True)
    branch=fields.Many2one('res.branch',string='Branch')
    date=fields.Date(string='Request Date',required=True, tracking=True)
    licence_plate=fields.Char(string='Licence Plate',related='fleet.license_plate',required=True,tracking=True)
    shassis_no=fields.Char(string='Shassis No',related='fleet.vin_sn',required=True,tracking=True)
    complain=fields.Text(string='Complain',required=True,tracking=True)
    service_id=fields.One2many('services','repair_id')
    hour=fields.Float(string='Working Hour')
    warehouse=fields.Many2one('stock.warehouse',string='Warehouse')
    spare_id=fields.One2many('spare.parts','repairid')
    source_warehouse_id = fields.Many2one('stock.warehouse', 'From Warehouse')
    backorder_count = fields.Integer(string='Back Order', compute='_compute_backorder_ids')
    picking_id = fields.Many2many('stock.picking', 'job_pickind_ids', string='Picking Reference')
    return_picking_id = fields.Many2one('stock.picking', 'Return Picking Reference', readonly=True)
    purchase_req_id = fields.Many2one('purchase.requisition', 'Purchase Requisition Reference', readonly=True)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('repair','Workshop Admin'),
        ('stock','Stock'),
        ('requisition','Purchase Requisition'),
        ('cancel','Cancel'),
        ('done', 'Done')], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    transfer_count=fields.Integer(string='Stock Transfers', compute='_compute_transfers_ids',tracking=True)

    def _compute_transfers_ids(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('repair_id', '=', self.id)])
            rec.transfer_count = len(picking_ids)

    @api.model
    def create(self, vals):
        repair = super(Repair, self).create(vals)
        for x in repair:
            x.repair_no = self.env['ir.sequence'].next_by_code('repair.no')
        return repair

    def to_admin(self):
        self.write({'state': 'repair'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
    def action_done(self):
        self.write({'state': 'done'})

    def _compute_backorder_ids(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search(
                [('repair_id', '=', rec.id), ('backorder_id', '!=', rec.picking_id.id)])
            rec.backorder_count = len(picking_ids)
            print()

    def generate_purchase_requsition(self):
        self.write({'state': 'requisition'})
        purchase_order_vals = purchase_order_lines_vals = {}
        purchase_order_vals = {
            'user_id':self.env.uid,
            'repair_id':self.id
        }

        purchase_id = self.env['purchase.requisition'].create(purchase_order_vals)
        for line in self.spare_id:
            if line.delivered_qty < line.ordered_qty:
                purchase_order_lines_vals = {
                    'product_id': line.spare.id,
                    'requisition_id': purchase_id.id,
                    'product_qty': line.ordered_qty,
                    'price_unit': line.spare.list_price,

                }
            self.env['purchase.requisition.line'].create(purchase_order_lines_vals)
        self.purchase_req_id = purchase_id

    def generate_picking(self):
        if not self.spare_id:
            raise ValidationError(_('Spare part details must be added'))
        else:
            spares_list = duplicated_list = []
            for item in self.spare_id:
                if item.picking_id.id == False:
                    spares_list.append(item.spare.id)
            duplicated_list = [x for n, x in enumerate(spares_list) if x in spares_list[:n]]
            if duplicated_list:
                for item in duplicated_list:
                    product = self.env['product.product'].search([('id', '=', item)])
                    raise ValidationError(
                        _('Item %s ordered twice you can change the ordered quantity') % (product.default_code))

            # Stock Picking order entry
            stock_picking_vals = {'partner_id': self.create_uid.partner_id.id,
                                  'location_id': self.source_warehouse_id.lot_stock_id.id,
                                  'location_dest_id': self.source_warehouse_id.wh_output_stock_loc_id.id,
                                  'scheduled_date': self.date,
                                  'picking_type_id': self.source_warehouse_id.out_type_id.id,
                                  'repair_id': self.id,
                                  }
            picking = self.env['stock.picking'].create(stock_picking_vals)

            # Stock Move
            for line in self.spare_id:
                if line.picking_id.id == False:
                    stock_move_vals = {
                        'product_id': line.spare.id,
                        'product_uom_qty': line.ordered_qty,
                        'product_uom': line.spare.product_tmpl_id.uom_id.id,
                        'location_id': self.source_warehouse_id.lot_stock_id.id,
                        'name': line.spare.name,
                        'location_dest_id': self.source_warehouse_id.wh_output_stock_loc_id.id,
                        'picking_id': picking.id,
                        'spare_line_id': line.id,
                    }
                    move = self.env['stock.move'].create(stock_move_vals)
                    line.picking_id = picking
                    self.write({'state': 'stock'})

class Service(models.Model):
    _name = 'services'
    repair_id=fields.Many2one('repair','Repair', ondelete='cascade')
    service=fields.Many2one('product.product',string='Service',domain="[('detailed_type','=','service')]")
    hour=fields.Float(string='Working Hour')

class SpareParts(models.Model):
    _name = 'spare.parts'

    repairid=fields.Many2one('repair','Repair', ondelete='cascade')
    spare=fields.Many2one('product.product',string='Spares',domain="[('detailed_type','=','product')]")
    ordered_qty=fields.Float(string='Ordered Quantity')
    delivered_qty=fields.Float(string='Delivered Quantity',compute='_compute_supply')
    uom=fields.Many2one('uom.uom',string='UoM',related='spare.uom_id')
    picking_id = fields.Many2many('stock.picking', 'repair_id', string='Picking Reference')
    return_picking_id = fields.Many2one('stock.picking', 'Return Picking Reference', readonly=True)
    back_picking_ids = fields.Many2many('stock.picking', 'stock_picking_rel', copy=False, string='Back Order Pickings',
                                        compute='_compute_supply')
    available_qty=fields.Float(string='Available Qty', compute='compute_qty')

    @api.depends('spare')
    def compute_qty(self):
        self.available_qty = 0.0
        qty = 0
        for rec in self:
            quant_ids = self.env['stock.quant'].search(
                [('location_id', '=', rec.repairid.source_warehouse_id.lot_stock_id.id), ('product_id', '=', rec.spare.id)])
            for quantity in quant_ids:
                qty += quantity.quantity
                rec.available_qty = qty

    def _compute_supply(self):
        self.delivered_qty = 0
        for rec in self:
            delivered = returned = suply = 0
            rec.back_picking_ids = []
            # if rec.state == 'done':
            move_line_ids = self.env['stock.move.line'].search(
                [('picking_id.repair_id', '=', rec.repairid.id),('picking_id', '=', rec.picking_id.id), ('product_id', '=', rec.spare.id), ('state', '=', 'done')])
            print(move_line_ids,'move_line_ids')
            for move in move_line_ids:
                delivered += move.qty_done
            print('delivered',delivered)

            if rec.repairid.backorder_count > 0:
                location_id =  self.repairid.source_warehouse_id.out_type_id.id
                print(location_id, 'location_id')
                location_dest_id =  self.repairid.source_warehouse_id.wh_output_stock_loc_i.id
                print(location_dest_id,'location_dest_id')
                back_order_ids = self.env['stock.move'].search(
                    [('picking_id.backorder_id', '!=', False), ('picking_id.location_id', '=', location_id),
                     ('picking_id.location_dest_id', '=', location_dest_id),
                     ('picking_id.job_id', '=', rec.repairid.id),('picking_id', '=', rec.picking_id.id),
                     ('state', '=', 'done')])
                print('back_order_ids',back_order_ids)
                for order in back_order_ids:
                    delivered += order.quantity_done
                # print('lines',back_order_ids.mapped('picking_id').ids)
                rec.back_picking_ids = [(6, _, back_order_ids.mapped('picking_id').ids)]
            if rec.return_picking_id.state == 'done':
                r_move_line_ids = self.env['stock.move.line'].search(
                    [('picking_id', '=', rec.return_picking_id.id), ('product_id', '=', rec.name.id),
                     ('state', '=', 'done')])
                for r_move in r_move_line_ids:
                        returned += r_move.qty_done
            suply = delivered - returned
            print('sssssssssssss',suply)

            rec.delivered_qty = suply




class Picking(models.Model):
    _inherit = 'stock.picking'

    repair_id = fields.Many2one('repair', 'Repair Reference', readonly=True)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    spare_line_id = fields.Many2one('spare.part', 'Spare Part Reference')


class StockMove(models.Model):
    _inherit = "stock.move"

    spare_line_id = fields.Many2one('spare.part', 'Spare Part Reference')

class Requisition(models.Model):
    _inherit = "purchase.requisition"

    repair_id = fields.Many2one('repair', 'Repair Reference')


