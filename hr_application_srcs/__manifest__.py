# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name': "Application SRCS",

    'author': "IATL Intellisoft International",
    'website': "http://www.iatl-intellisoft.com",
    'category': 'Human Resource',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/view_application_inherit.xml',
        'report/application_report.xml',
        'report/application _srcs_template.xml'
    ],

}
