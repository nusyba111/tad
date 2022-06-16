# -*- coding: utf-8 -*-
# from odoo import http


# class HrEndOfServiceSrcs(http.Controller):
#     @http.route('/hr_end_of_service_srcs/hr_end_of_service_srcs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_end_of_service_srcs/hr_end_of_service_srcs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_end_of_service_srcs.listing', {
#             'root': '/hr_end_of_service_srcs/hr_end_of_service_srcs',
#             'objects': http.request.env['hr_end_of_service_srcs.hr_end_of_service_srcs'].search([]),
#         })

#     @http.route('/hr_end_of_service_srcs/hr_end_of_service_srcs/objects/<model("hr_end_of_service_srcs.hr_end_of_service_srcs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_end_of_service_srcs.object', {
#             'object': obj
#         })
