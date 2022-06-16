# -*- coding: utf-8 -*-
{
    'name': "HR Employee SRCS",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'license': "AGPL-3",
    'category': 'HR',
    'depends': ['hr','hr_contract','accounting_srcs','hr_payroll'],
    'data': [
        # 'security/security_views.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'views/hr_contract_views.xml',
    ],
}
