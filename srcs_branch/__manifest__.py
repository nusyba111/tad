{
    'name': 'SRCS Branch',
    'version': '1.0',
    'author': 'IATL IntelliSoft',
    'description': """ """,
    'depends': ['base', 'web', 'accounting_srcs', 'product', 'account_reports','asset_srcs','srcs_financial_requests'],
    'data': [
        'security/ir.model.access.csv',
        'security/branch_security.xml',
        'wizard/user_branch_wizard_view.xml',
        'views/repair_maintainance.xml',
       

    ],
    
  
   
}
