{
    'name': 'SRCS Branch',
    'version': '1.0',
    'author': 'IATL IntelliSoft',
    'description': """ """,
    'depends': ['base', 'web', 'accounting_srcs', 'product', 'account_reports','asset_srcs','srcs_financial_requests','report_xlsx'],
    'data': [
        # 'security/branch_security.xml',
        'security/ir.model.access.csv',
        'wizard/user_branch_wizard_view.xml',
        'wizard/srcs_projectwizard.xml',
        'wizard/report_action.xml',
        'views/res_branch.xml',
       

    ],
    
  
   
}
