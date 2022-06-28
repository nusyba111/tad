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
    driver_id = fields.Many2one('res.partner', compute='compute_default', store=False)# compute to come auto
    engine_no=fields.Integer('Engine No')
    # insurance_start=fields.Date('Insurance Start Date',Tracking=True)
    # insurance_end = fields.Date('Insurance End Date', Tracking=True)
    on_rent=fields.Boolean(string='On Rent',readonly=True)
    insurance_start = fields.Datetime('Insurance Start Date', Tracking=True)
    insurance_end = fields.Datetime('Insurance End Date', Tracking=True)
    # new fields
    vrp_user=fields.Many2one('res.partner',string='VRP USER?')
    federation_vehicle_code = fields.Char(string='Federation Vehicle Code')
    model_model_id = fields.Many2one('fleet.vehicle', string='Car Model')
    engine_type = fields.Char(string='Engine Type/Model')
    registration_start = fields.Date('Registration Start')
    registration_end = fields.Date('Registration End')
    local_insurance_policy_number = fields.Char('Local Insurance Policy Number')
    cost_third_party_local = fields.Float(string='Cost Third Party Local(Country Currency Sudan Pound SDG)')
    registration_plate_type = fields.Selection([('diplomatic','Diplomatic'),
                                                ('civilian','Civilian')],string='Registration Plate Type')
    fuel_count=fields.Integer(string='Fuel', compute='_compute_fuel_ids',tracking=True)
    repair_count=fields.Integer(string='Fuel', compute='_compute_repair_ids',tracking=True)

    def _compute_fuel_ids(self):
        for rec in self:
            fuel = self.env['fuel.type'].search([('service_id.vehicle', '=', self.id)])
            rec.fuel_count = len(fuel)

    def _compute_repair_ids(self):
            for rec in self:
                repair = self.env['repair'].search([('fleet', '=', self.id)])
                rec.repair_count = len(repair)

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


