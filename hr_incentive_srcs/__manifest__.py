# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name': 'HR Incentive SRCS',
    'summary': """ """,

    'description': """
        Long description of module's purpose
    """,

    'author': "IATL Intellisoft International",
    'website': "http://www.iatl-intellisoft.com",
    'category': 'Human Resource',

    'depends': ['account','hr_payroll','hr_employee_srcs'],

    'data': [
        'security/ir.model.access.csv',
        'security/incentive_security.xml',
        'views/hr_incentive_view.xml',
        'views/res_config_settings_views.xml',
        'views/hr_payroll_view.xml',
        # 'report/incentive_report.xml',
        # 'report/incentive_templates.xml',
        'data/sequence.xml',
        'data/hr_incentive_data.xml',
        'data/template.xml',
    ],

    'installable': True,
    'auto_install': False
}
