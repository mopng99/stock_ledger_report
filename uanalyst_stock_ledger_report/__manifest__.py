# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Uanalyst Inventory Ledger Report',
    'version': '15.0.1.1.0',
    'summary': 'Inventory Ledger Report',
    'description': """Helps you to analyze the track inventory movements stock.
        TASK ID - 3001009""",
    'category': 'Customization',
    'author': "Odoo PS",
    'website': "http://www.odoo.com",
    'depends': ['sale_management', 'purchase_requisition_stock',
                'uanalyst_warehouse_restrictions', 'uanalyst_stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/stock_ledger_report_views.xml',
        'wizard/report_excel_stock_ledger_wizard_view.xml',
        'wizard/report_stock_ledger_wizard_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
