
from odoo import models, fields, api, _


class OfficeLease(models.Model):
    _name = 'office.lease'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Create an Office Lease'
    _rec_name = 'sequence'
    _order = "date,state desc"

    sequence=fields.Char(readonly=True)
    date=fields.Date(string='Date',required=True,tracking=True)
    partner_id=fields.Many2one('res.partner',string='Second Party',required=True,tracking=True)
    start_date=fields.Datetime(string='Start Date',required=True,tracking=True)
    location=fields.Many2one('hr.work.location',string='Leased Location',required=True,tracking=True)
    total_amount=fields.Float(string='Total Amount')
    lease_details=fields.One2many('lease.detail','lease_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admin', 'Administration Approve'),
        ('cancel', 'Cancel'),
        ('done', 'Done')], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.model
    def create(self, vals):
        lease = super(OfficeLease, self).create(vals)
        for x in lease:
            x.sequence = self.env['ir.sequence'].next_by_code('lease.no')
        return lease

    def to_admin(self):
        self.write({'state': 'admin'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_done(self):
        self.write({'state': 'done'})

class LeaseDetails(models.Model):
    _name='lease.detail'

    lease_id=fields.Many2one('office.lease')
    item=fields.Char(string='Item')
    cost=fields.Float(string='Cost Per Month(Euro)')