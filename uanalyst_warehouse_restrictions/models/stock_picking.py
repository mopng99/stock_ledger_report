# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_allowed_operation_type_ids(self):
        """returns the allowed warehouse ids related operation types"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.env['stock.picking.type'].search([('warehouse_id', 'in',\
                    logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('id', 'in', domain)]

    @api.model
    def _get_allowed_location_ids(self):
        """"returns the allowed location ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            return [('id', 'in', logged_in_user.restrict_stock_location_ids.ids)]

    location_id = fields.Many2one('stock.location', "Source Location",
                                  domain=lambda self: self._get_allowed_location_ids(),)
    location_dest_id = fields.Many2one('stock.location', "Destination Location",
                                       domain=lambda self: self._get_allowed_location_ids(),)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      domain=lambda self: self._get_allowed_operation_type_ids(),)
    search_stock_pickings = fields.Char(compute='_compute_warehouse_search_ids',
                                        search='stock_picking_type_ids_search')

    @api.depends('search_stock_pickings')
    def _compute_warehouse_search_ids(self):
        pass

    def stock_picking_type_ids_search(self, operator, operand):
        """return allow operation types ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.env['stock.picking.type'].search([('warehouse_id', 'in',\
                    logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('picking_type_id', 'in', domain)]
        return []
