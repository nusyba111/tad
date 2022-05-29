# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models, _
from odoo import http, tools
from odoo.service import db
import base64
import odoo
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from werkzeug import url_encode
import werkzeug
from odoo.exceptions import UserError


class UserBranchWizard(models.Model):
    _inherit = "res.users"

    branch_id = fields.Many2one('res.branch', string='Branch',
                                domain=lambda self: [('id', 'in', self.env.user.allowed_branchs.ids)])

    def change_branch(self, redirect=None):
        user = self.env.user
        if self.branch_id in user.allowed_branchs:
            user.current_branch = self.branch_id.id
        else:
            raise UserError('This branch is not allowed for your user, contact the administrator !')

        return {'type': 'ir.actions.client', 'tag': 'reload', }
