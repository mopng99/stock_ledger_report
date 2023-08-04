# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    @api.model
    def _get_allowed_warehouses_ids(self):
        """returns the allowed warehouse ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            return [('id', 'in', logged_in_user.default_stock_warehouse_ids.ids)]

    @api.model
    def _get_allowed_picking_type_ids(self):
        """returns the allowed operations ttypesype ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_operations_type:
            return [('id', 'in', logged_in_user.restrict_stock_picking_type_ids.ids)]

    @api.model
    def _get_allowed_default_source_location_ids(self):
        """returns the allowed source locations ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            return [('id', 'in', logged_in_user.restrict_stock_location_ids.ids)]

    @api.model
    def _get_allowed_destionation_location_ids(self):
        """returns the allowed destination locations ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            return [('id', 'in', logged_in_user.restrict_stock_location_ids.ids)]

    search_stock_picking_type_ids = fields.Char(compute='_compute_picking_types_ids_search',
                                                search='stock_picking_type_ids_search')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', \
                                   domain=lambda self: self._get_allowed_warehouses_ids())
    return_picking_type_id = fields.Many2one('stock.picking.type', 'Operations Type', \
                                             domain=lambda self: self._get_allowed_picking_type_ids())
    default_location_src_id = fields.Many2one('stock.location', 'Default Source Location', \
                                              domain=lambda self: self._get_allowed_default_source_location_ids())
    default_location_dest_id = fields.Many2one('stock.location', 'Default Destination Location', \
                                               domain=lambda self: self._get_allowed_destionation_location_ids())

    @api.depends('search_stock_picking_type_ids')
    def _compute_picking_types_ids_search(self):
        pass

    def stock_picking_type_ids_search(self, operator, operand):
        """returns the allowed operations ttypesype ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_operations_type:
            return [('id', 'in', logged_in_user.restrict_stock_picking_type_ids.ids)]
        return []



