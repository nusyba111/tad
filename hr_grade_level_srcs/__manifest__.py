# -*- coding: utf-8 -*-
{
    'name' : 'HR Grade & Level SRCS',
    'summary': """ """,

    'description': """
        Long description of module's purpose
    """,

    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'Human Resource',

    'depends':['hr','srcs_branch'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',
        'data/data.xml',
        'views/hr_grade.xml', 
        'views/hr_contract.xml',
        # 'views/hr_application.xml',
        'views/hr_employee.xml',
        'views/hr_wage_process.xml',
        'views/hr_wage_process_batch.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
