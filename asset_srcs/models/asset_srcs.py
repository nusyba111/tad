from odoo import api, fields, models,_

class SrcsAsset(models.Model):
    _inherit = "account.asset"

    location_id = fields.Many2one('account.analytic.account', string='Location',domain="[('type','=','location')]")
    owner = fields.Many2one('res.users', string='User', default= lambda self: self.env.user)
    donor_id = fields.Many2one('res.partner', string='Donor')
    project_id = fields.Many2one('account.analytic.account', string='Project',domain="[('type','=','project')]")
    office = fields.Char('Office')
    description = fields.Char('Description')
    mark = fields.Char('Mark')
    serial_num = fields.Char('Serial Number')
    code = fields.Char('Code')
    photo = fields.Binary('Photo')

class SrcsAssetOpertaion(models.Model):
    _name = "asset.opertaion"

    name = fields.Char('Operation Name', required=True)
    donor_id = fields.Many2one('res.partner', string='Donor', required=True)
    project_id = fields.Many2one('account.analytic.account', string='Project',domain="[('type','=','project')]", required=True)
    location_id = fields.Many2one('account.analytic.account', string='Location',domain="[('type','=','location')]", required=True)
    type = fields.Selection([
        ('donation', 'Donation'),('transfer','Transfer')
    ], string='Type')
    acquistion_date = fields.Date('Acquisition Date')
    asset_id = fields.Many2one('account.asset', string='Asset', domain="[('state','!=','model')]")
    asset_type_id = fields.Many2one('account.asset', string='Asset Type', domain="[('state','=','model')]")
    net_value = fields.Float('Net Value')
    debit = fields.Many2one('account.account', string='Debit Account')
    credit = fields.Many2one('account.account', string='Credit Account')
    state = fields.Selection([
        ('darft','Draft'),
        ('project', 'Project/Fleet'),
        ('asset_manager','Asset Manager'),
        ('finance_director','Finance Director'),
        ('secratry_general','Secretary General  '),
    ], default="darft", string='State')

    def confirm(self):
        self.state = "project"

    def submit_manager(self):
        self.state = "asset_manager"

    def approve_director(self):
        move = {
            'name': self.name,
            'date': self.acquistion_date,
            'partner_id': self.donor_id.id,
            'move_type': 'entry',
            'state': 'draft',
            'line_ids': [(0, 0, {
                'name': self.name,
                'partner_id': self.donor_id.id,
                'account_id': self.debit.id,
                'analytic_account_id': self.project_id.id,
                'location_id': self.location_id.id,
                'debit': self.net_value}),
                (0, 0, {
                'name': self.name,
                'partner_id': self.donor_id.id,
                'account_id': self.credit.id,
                'analytic_account_id': self.project_id.id,
                'location_id': self.location_id.id,
                'credit': self.net_value})]
            }
        move_id = self.env['account.move'].create(move)
        # move_id.post()
        self.state = "finance_director"

    def done_secratry(self):
        self.state = "secratry_general"

    def reset_draft(self):
        self.state = "darft"