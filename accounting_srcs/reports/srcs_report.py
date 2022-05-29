from odoo import api, fields, models, _

class SRCSAccountFinancialReport(models.Model):
    _inherit = 'account.financial.html.report'

    # @property
    # def filter_comparison(self):
    #     if self.comparison:
    #         return {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    #     return super().filter_comparison
    