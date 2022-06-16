# -*- coding: utf-8 -*-
{
    'name': "Employee Update Process",

    'summary': """
        """,

    'description': """
          This module update salary department jop position
        
    """,
    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'HR Contract PGM ',
    'depends': ['hr_contract'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/hr_update_process.xml',
        'views/hr_employee.xml'
    ],
}
