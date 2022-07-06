# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

{
    'name': "Fleet SRCS",

    'author': "IATL Intellisoft International",
    'website': "http://www.iatl-intellisoft.com",
    'category': 'Human Resource',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_fleet', 'fleet','stock','purchase_requisition','srcs_branch','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_view_form_inherit.xml',
        'views/view_attach_inherit.xml',
        'report/repair_fleet_template.xml',
        'report/flue_issue.xml',
        'report/reports.xml',
        'report/fueling_report.xml',
        'report/insurance_report.xml',
        'report/vehicle_rent.xml',
        'report/contract.xml',
        'views/repair_maintainance.xml',
        'views/fueling_view.xml',
        'views/insurance_view.xml',
        'views/vehicle_request_view.xml',
        'views/vehicle_rent_view.xml',
        'wizard/preventive_maintainance_view.xml',
        'wizard/insurance_date_view.xml',
        'wizard/fuel_report_view.xml',
        'wizard/maintainance_report_view.xml',
        'wizard/new_vehicle.xml',
        'wizard/fuel_tracking_view.xml',
        'wizard/insurance_price_change_view.xml',
        'wizard/excel_maintainance_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}


