# -*- coding: utf-8 -*-
{
    'name': "admin Custom",

    'summary': """
        A custom model for administration""",

    'description': """
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'fleet', 'hr', 'account', 'hr_contract_kambal', 'fleet_kambaal', 'report_xlsx',
                'board', 'kambal_stock_custom'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/seq_seq.xml',
        'reports/loan_car_action_report.xml',
        'reports/car_move_action_report.xml',
        'reports/total_car_move.xml',
        'reports/compare_sanitation_action_report.xml',
        'reports/inventory_scrap_report.xml',
        'reports/garbage_report_action.xml',
        'reports/compare_garbage_report.xml',
        'reports/total_tanker_report.xml',
        'reports/all_car_tab_reports.xml',
        'reports/all_loan_tab_reports.xml',
        'reports/all_worker_tab_reports.xml',
        'reports/test.xml',
        'wizard/ledger_report_view.xml',
        'wizard/car_excel_wizard.xml',
        'wizard/inventory_scrap_wiz.xml',
        'wizard/loan_car_wiz_view.xml',
        'wizard/car_move_wiz.xml',
        'wizard/total_car_move_wiz.xml',
        'wizard/total_tanker_wiz.xml',
        'wizard/garbage_report_wiz.xml',
        'wizard/compare_garbage_wiz.xml',
        'wizard/compare_sanitation_report.xml',
        'views/all_actions_menus.xml',
        'views/technical_test_view.xml',
        'views/config.xml',
        'views/apartment_req.xml',
        'views/product_health.xml',
        'views/car_contract.xml',
        'views/car_fuel.xml',
        'views/loan_car_request.xml',
        'views/loan_car_stop.xml',
        'views/loan_car_clearance.xml',
        'views/loan_car_monthly_fees.xml',
        'views/worker_meal.xml',
        'views/worker_meal_subsidy.xml',
        'views/worker_meal_subsidy_cancel.xml',
        'views/worker_meal_cost_calculation.xml',
        'views/w_employee_meal_cost.xml',
        'views/x_meal_cost_calculation.xml',
        'views/cleaning_follow_up.xml',
        'views/sanitation_follow_up.xml',
        'views/sanitation_calculations.xml',
        'views/garbage_calculation.xml',
        'views/garbage_follow_up.xml',
        'views/sim_card.xml',
        'views/adding_worker_to_transport_line.xml',
        'views/cars_warning.xml',
        'views/loan_car_request.xml',
        'views/transportation_cars_attendance.xml',
        'views/transportation_line_request.xml',
        # 'views/dashboard.xml',
    ],
    "demo": [],
    "qweb": [],
    "auto_install": False,
    "application": True,
    "installable": True,
}
