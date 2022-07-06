# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name': "Administration SRCS",

    'author': "IATL Intellisoft International",
    'website': "http://www.iatl-intellisoft.com",
    'category': 'Human Resource',

    # any module necessary for this one to work correctly
    'depends': ['base','srcs_branch','purchase_requisition','hr','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/exit_permission_view.xml',
        'views/maintainance_request_view.xml',
        'views/office_lease_view.xml',
        'report/exit_permission.xml',
        'report/maintenance_requests.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}


