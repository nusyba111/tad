{
    'name': "SRCS Purchase",

    'summary': """
        """,

    'description': """
    """,
    'version': '15.0',
    'author': "IATL International",
    'website': "http://www.iatl-sd.com",
    # 'category': 'Accounting/Common',
    'depends': ['purchase', 'purchase_requisition', 'hr', 'accounting_srcs', 'base', 'stock'],
    'data': [
            'security/ir.model.access.csv',
            'security/srcs_security.xml',
            'data/seq.xml',
            'views/srcs_purchase.xml',
            'views/srcs_requestion.xml',
            # 'views/srcs_stock.xml',
            'views/finacial_limit.xml',
            # 'views/product.xml',
            'reports/order.xml',
            'reports/quotation.xml',
            'reports/header.xml',
            'reports/red.xml',
            'wizard/procurment_track_sheet_view.xml',
            'wizard/procurement_view.xml',
            'wizard/custom_track_report_view.xml',
    ],
}