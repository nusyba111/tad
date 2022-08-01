# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class InventoryScrap(models.TransientModel):
    _name = 'inventory.scrap.wiz'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    product = fields.Many2one('product.template', string='product')

    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['product'] = self.product.name

        return self.env.ref('admin_module.report_inventory_scrap').report_action([], data=data)


class InventoryScrapReport(models.AbstractModel):
    _name = 'report.admin_module.template_report_scrap_ids'

    # to print header
    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        product = data['product']
        return {
            'from_date': from_date,
            'to_date': to_date,
            'product': product,
        }

    def _get_scrap(self, data):
        list_data = []
        scrap = self.env['stock.scrap.order'].search([
            ('date_order', '>=', data['from_date']),
            ('date_order', '<=', data['to_date']),
        ])
        scrap_line = scrap.mapped('scrap_ids')
        if data['from_date'] and data['to_date'] and not data['product']:
            if scrap_line:
                for sc in scrap:
                    for rec in sc.scrap_ids:
                        list_data.append({
                            'product': rec.product_id.name,
                            'date_order': sc.date_order,
                            'unit_product': rec.unit_product.name,
                            'qty_product': rec.qty_product,
                            'note': rec.note,
                        })
                return list_data
            #      for product only  --done
        if data['from_date'] and data['to_date'] and data['product']:
            if scrap_line:
                for sc in scrap:
                    for rec in scrap_line.filtered(lambda r: r.product_id.name == data['product']):
                        list_data.append({
                            'product': rec.product_id.name,
                            'date_order': sc.date_order,
                            'unit_product': rec.unit_product.name,
                            'qty_product': rec.qty_product,
                            'note': rec.note,
                        })
                    return list_data

    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['stock.scrap.order'].browse(data)
        docs = data['records']
        scrap_report = self.env['ir.actions.report']._get_report_from_name(
            'admin_custom.template_report_scrap_ids')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': scrap_report.model,
            'docs': data,
            'get_header_info': self._get_header_info(data),
            'get_scrap': self._get_scrap(data),
        }
