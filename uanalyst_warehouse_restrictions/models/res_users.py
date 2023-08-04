# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_warehouse_operations = fields.Boolean(default=False,
                                                   string='Allow Warehouse Operations')
    default_stock_warehouse_ids = fields.Many2many('stock.warehouse',
                                                   'stock_warehouse_users_rel', 'user_id',
                                                   'warehouse_id',
                                                   context={'active_test': False},
                                                   string='Allow Warehouse Operations')
    restrict_stock_locations = fields.Boolean(default=False,
                                              string='Allow Stock Locations')
    restrict_stock_location_ids = fields.Many2many('stock.location',
                                                   'restrict_stock_location_res_users_rel',
                                                   'user_id', 'location_id',
                                                   'Allow Stock Locations',
                                                   context={'active_test': False})
    restrict_stock_operations_type = fields.Boolean(default=False, string='Allow Stock operations Type')
    restrict_stock_picking_type_ids = fields.Many2many('stock.picking.type',
                                                       'restrict_stock_return_picking_type_res_users_rel',
                                                       'user_id', 'return_picking_type_id',
                                                       'Allow Stock operations Type',
                                                       context={'active_test': False})

    @api.constrains('restrict_stock_location_ids', 'restrict_stock_locations')
    def stock_locations_restriction(self):
        restrict_group = \
            self.env.ref('uanalyst_warehouse_restrictions.stock_location_restrictions_group')
        if self.restrict_stock_locations:
            restrict_group.write({'users':  [(4, self.id)]})
        else:
            restrict_group.write({'users':  [(3, self.id)]})
