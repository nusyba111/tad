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

from odoo.tools import float_compare, get_lang, format_date

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS

class ResBranch(models.Model):
    _name = 'res.branch'

    name = fields.Char(string="Name", required=True)
    account_id = fields.Many2one("account.analytic.account", string="Analytic Acount")
    company_id = fields.Many2one('res.company', string="Region Name",
                                 default=lambda self: self.env.user.company_id)

    quotation_header_img_left = fields.Binary(string="Quotation Header Image Left")
    quotation_header_img_center = fields.Binary(string="Quotation Header Image Center")
    quotation_header_img_right = fields.Binary(string="Quotation Header Image Right")
    quotation_header_img_bottom = fields.Binary(string="Quotation Header Image bottom")
    quotation_footer_img = fields.Binary(string="Quotation Footer Image")
    watermark = fields.Binary(string="Watermark Image")
    # location_id = fields.Many2one(comodel_name="stock.location", string="Stock Location", required=False, )

    @api.model_create_multi
    def create(self, vals):
        res = super(ResBranch, self).create(vals)
        project = self.env['account.analytic.account'].create(
            {
                'name': res.name,
                'type': 'location',
                'branch_id':res.id,
            }
        )
        print('_____________res',res.id,res.name)
        return res

class ResUsers(models.Model):
    _inherit = 'res.users'

    current_branch = fields.Many2one("res.branch", string="Current Branch")
    allowed_branchs = fields.Many2many("res.branch", string="Allowed Branch")

    @api.constrains('current_branch', 'allowed_branchs')
    def _current_branch_on_allowed_branchs(self):
        if (self.current_branch.id not in self.allowed_branchs.ids):
            raise UserError(('Current branch must be in allowed branches!!'))


class accountMoveInherit(models.Model):
    _inherit = 'account.move'

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                readonly=True,
                                default=lambda self: self.env.user.current_branch)


class accountMoveLine(models.Model):
    _inherit = 'account.move.line'

    branch_id_line = fields.Many2one(related='move_id.branch_id', string="Branch")

    # @api.onchange('product_id')
    # def get_analytic_account(self):
    #     for rec in self:
    #         rec.analytic_account_id = rec.move_id.branch_id.account_id.id


class accountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                default=lambda self: self.env.user.current_branch,
                                )
    transfer_to = fields.Many2one('res.branch', string='Destination Branch')

# class ProductTemplate(models.Model):
#     _inherit = 'product.template'


#     arabic_name = fields.Char(string="Arabic Name", required=False, )
#     branch_ids = fields.Many2many(comodel_name="res.branch", string="Branch")
#     is_sapre = fields.Boolean('Spare')


# class productCategoryInherit(models.Model):
#     _inherit = 'product.category'

#     branch_ids = fields.Many2many(comodel_name="res.branch", string="Branch")
#     arabic_name = fields.Char(string="Arabic Name", required=False, )


class accountJournalInherit(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                default=lambda self: self.env.user.current_branch.id)

    # allowed_users = fields.Many2many("res.users", string="Allowed users")


# class productProductInherit(models.Model):
#     _inherit = 'product.product'

#     @api.model
#     def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
#         args = args or []
#         domain = []
#         if (name or '').strip():
#             domain = ['|','|',
#                       ('name', operator, name),
#                       ('arabic_name', operator, name),
#                       ('default_code', operator, name)
#                       ]
#             if operator in NEGATIVE_TERM_OPERATORS:
#                 domain = domain[1:]
#         return self._search(AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

#     branch_id = fields.Many2one(comodel_name="res.branch",
#                                 string="Branch",
#                                 default=lambda self: self.env.user.current_branch.id)
#     # product_tmpl_id
#     arabic_name = fields.Char(related='product_tmpl_id.arabic_name',string="Arabic Name", required=False, )

class ConveriosnCurrency(models.Model):
    _inherit = 'currency.conversion'

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                readonly=True,
                                default=lambda self: self.env.user.current_branch)

# class ConveriosnCurrency(models.Model):
#     _inherit = 'crossovered.budget'

#     def _get_default_project(self):
#         # for rec in self:
#             branch_project = self.env['account.analytic.account'].search([('branch_id','=',self.env.user.current_branch.id),('type','=','project')])
#             self.project_id = branch_project
#             print('_______________project',branch_project)

#     project_id = fields.Many2one('account.analytic.account',string='Project', required=True, domain="[('type','=','project')]", default=_get_default_project)

    

class ConveriosnCurrency(models.Model):
    _inherit = 'account.analytic.account'

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                readonly=True,
                                default=lambda self: self.env.user.current_branch)

class SrcAssetBranch(models.Model):
    _inherit = "account.asset"

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                readonly=True,
                                default=lambda self: self.env.user.current_branch)

class SrcAssetOperationBranch(models.Model):
    _inherit = "asset.opertaion"

    transfer_to = fields.Many2one('res.branch', string='Transfer To')
    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                readonly=True,
                                default=lambda self: self.env.user.current_branch)

class SrcsCashRequestBranch(models.Model):
    _inherit = "cash.request"

    branch_id = fields.Many2one(comodel_name="res.branch",
                                string="Branch",
                                readonly=True,
                                default=lambda self: self.env.user.current_branch)