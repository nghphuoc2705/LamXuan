# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Employee Payslip Report",
    'category': 'Payroll',
    'version': '1.0',
    'author': 'Equick ERP',
    'description': """
        This Module allows to print Payslip PDF & Excel Report.
        * Allows user to print Payslip PDF & Excel report.
        * User can see the salary computation group by the Salary rule Category & Salary Rules.
    """,
    'summary': """ This Module allows to print Payslip PDF & Excel Report. Payslip Template | employee report | employee payslip report | payslip report | pay slip report | payroll report""",
    'depends': ['base', 'hr_payroll', 'hr'],
    'price': 20,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_payslip_report.xml',
        'views/contract_views.xml',
        'views/employee_views.xml',
        'report/report_payslip_template.xml',
        'report/report.xml'
    ],
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: