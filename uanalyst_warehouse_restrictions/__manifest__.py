# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Uanalyst Warehouse Access Rights',
    'version': '15.0.1.0.0',
    'summary': 'Uanalyst Warehouse Restrictions',
    'description': """ This Module Restricts the User from Accessing Warehouse and its Locations,
    Operation Types,Stock Rules,Routes,Product Qunatity On Hand Button.
        TASK ID - 3076215""",
    'category': 'Customization',
    'author': "Odoo PS",
    'website': "http://www.odoo.com",
    'depends': ['base', 'sale_management', 'sale_stock',
                'purchase', 'purchase_requisition_stock', 'stock', 'mrp'],
    'data': [
        'security/warehouse_security_views.xml',
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
        'views/stock_warehouse.xml',
        'views/stock_location_views.xml',
        'views/product_views.xml',
        'views/stock_move_views.xml',
        'views/purchase_views.xml',
        ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
