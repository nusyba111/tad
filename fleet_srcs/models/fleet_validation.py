from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class FleetValidation(models.Model):
    _inherit = 'fleet.vehicle.assignation.log'

    attach = fields.Binary('Attachments', required=True)
