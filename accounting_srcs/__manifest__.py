# -*- coding: utf-8 -*-
{
    'name': "SRCS Accounting ",

    'summary': """
        """,

    'description': """
    """,
    'version': '15.0',
    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'Accounting/Common',
    'depends': ['account','account_budget','account_accountant'],
    'data': [
        'security/srcs_security_groups.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/account_voucher_view.xml',
        'views/donors.xml',
        'views/journal.xml',
        'views/budget.xml',
    ],
}