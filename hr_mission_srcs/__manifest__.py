# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

{
    'name': 'HR Mission SRCS',
    'summary': """ """,
    'description': """ Long description of module's purpose """,
    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'Human Resource',
    'depends': ['portal','account',"base_address_city",'hr_payroll'],

    # always loaded
    'data': [
        'security/mission_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/mission_enrich.xml',
        'wizard/mission_wizard.xml',
        'views/mission_request.xml',
        'views/res_config_settings.xml',
        'views/mission_type.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
    'auto_install': False,
}
