# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name': "Fleet SRCS Contract",

    'author': "IATL Intellisoft International",
    'website': "http://www.iatl-intellisoft.com",
    'category': 'Human Resource',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'hr_fleet', 'fleet_srcs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/view_inherit_fleet_contract.xml',

    ],

}
