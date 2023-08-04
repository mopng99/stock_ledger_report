# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Uanalyst Stock',
    'version': '15.0.1.0.0',
    'summary': 'Compute Product Transfer Cost',
    'description': """stock.
        TASK ID - 3012483""",
    'category': 'Customization',
    'author': "Odoo PS",
    'website': "http://www.odoo.com",
    'depends': ['sale_management', 'purchase_requisition_stock'],
    'data': [
        'security/security_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
