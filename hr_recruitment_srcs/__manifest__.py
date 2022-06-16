# -*- coding: utf-8 -*-
{
    'name': "HR Recruitment SRCS",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'license': "AGPL-3",
    'category': 'HR',
    'depends': ['hr_recruitment'],
    'data': [
        'security/security_views.xml',
        'security/ir.model.access.csv',
        'data/plan_sequense.xml',
        'views/hr_recruitment_plan_view.xml',
        'views/hr_recruitment_general_plan_view.xml',
        'report/recruitment _plan_template.xml',
        'report/report.xml',
    ],
}
