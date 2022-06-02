# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import models, fields, api, _


class FleetSrcsCustom(models.Model):
    # _name = 'fleet.srcs.custom'
    _inherit = 'fleet.vehicle'

    owner = fields.Many2one('res.partner', 'Owner/Donor')
    project = fields.Many2one('account.analytic.account', 'Project')
    base_location = fields.Many2one('account.analytic.account', 'Base location')
    driver_id = fields.Many2one('res.partner', compute='compute_default', store=False)  # compute to come auto

    def compute_default(self):
        for record in self:
            if not record.driver_id:
                res = self.env['fleet.vehicle.assignation.log'].search([
                    ('date_start', '<', fields.Date.today()),
                    ('date_end', '>', fields.Date.today()),
                    ('vehicle_id', '=', record.id)
                ], limit=1)
        if not res:
            # if it doesn't find value in date range , then driver_id should be empty
            record.driver_id = False
            # print("*************", self.driver_id)
        else:
            record.driver_id = res.driver_id.id
        # print("888888888888888", self.driver_id)

    # ################# Services page ###################################################

    services_list = fields.One2many('fleet.service', 'vehicle_id', string='Services List')


class FleetServices(models.Model):
    _name = 'fleet.service'
    vehicle_id = fields.Many2one('fleet.vehicle')  # inverse of O2m
    service = fields.Many2one('product.template', domain=[('detailed_type', '=', 'service')], string='Service')
    minimum_odometer = fields.Float('Minimum odometer', required=True)
    maximum_odometer = fields.Float('Maximum odometer', required=True)
