{
    'name': "SRCS Financial Request ",

    'summary': """
        """,

    'description': """
    """,
    'version': '15.0',
    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    'category': 'Accounting/Common',
    'depends': ['accounting_srcs'],
    'data': [
        'security/ir.model.access.csv',
        'views/cash_request.xml',
        'reports/cash_report.xml',
    ],
}