from odoo import fields, models, api, _

class SrcsStock(models.Model):
    _inherit = "stock.picking"

    mean_transport = fields.Selection([
        ('air', 'Air'),('road','Road'),('sea','Sea'),('other','Other'),
    ], string='Mean of Transport')
    arrival_date = fields.Date('Date of Arrival')
    bill_leading = fields.Char('Bill of Leading')
    vessel = fields.Char('Vessel')
    flight_number = fields.Char('Flight Number')
    truck_number = fields.Char('Truck Number')
    
class SrcsProduct(models.Model):
    _inherit = "product.template"    

    tracking_no = fields.Char('Tracking NO')
    donor_id = fields.Many2one('res.partner', string='Donor/Owner')
    item_description = fields.Char('Arabic Description')