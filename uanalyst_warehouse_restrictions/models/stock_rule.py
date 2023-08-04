# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    search_stock_rule_ids = fields.Char(compute='_compute_stock_rule_ids',
                                        search='stock_rule_ids_search')
    @api.model
    def _get_allowed_source_stock_location_ids(self):
        """returns the allowed source stock locations ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            domain = self.env['stock.location'].search([('id', 'in',\
                    logged_in_user.restrict_stock_location_ids.ids)]).ids
            return [('id', 'in', domain)]

    @api.model
    def _get_allowed_destionation_stock_location_ids(self):
        """returns the allowed destination stock locations ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            domain = self.env['stock.location'].search([('id', 'in',\
                    logged_in_user.restrict_stock_location_ids.ids)]).ids
            return [('id', 'in', domain)]

    @api.model
    def _get_allowed_warehouses_ids(self):
        """returns the allowed warehouse ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.env['stock.warehouse'].search([('id', 'in',\
                    logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('id', 'in', domain)]

    @api.model
    def _get_allowed_operation_type_ids(self):
        """returns the allowed warehouse ids related operation types"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.env['stock.picking.type'].search([('warehouse_id', 'in',\
                    logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('id', 'in', domain)]

    @api.model
    def _get_allowe_route_ids(self):
        """returns the allowed warehouse ids related routes ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.env['stock.location.route'].search([('warehouse_ids', 'in',\
                        logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('id', 'in', domain)]

    route_id = fields.Many2one('stock.location.route', 'Route',
                               domain=lambda self:self._get_allowe_route_ids())
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse',
                                   domain=lambda self: self._get_allowed_warehouses_ids())
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      domain=lambda self: self._get_allowed_operation_type_ids(),)

    location_src_id = fields.Many2one('stock.location', 'Source Location',\
                            domain=lambda self: self._get_allowed_source_stock_location_ids())
    location_id = fields.Many2one('stock.location', 'Destination Location',\
                            domain=lambda self: self._get_allowed_destionation_stock_location_ids())
    propagate_warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse to Propagate',
                                             domain=lambda self: self._get_allowed_warehouses_ids())

    @api.depends('search_stock_rule_ids')
    def _compute_stock_rule_ids(self):
        pass

    def stock_rule_ids_search(self, operator, operand):
        """return allow stock rules ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.search([('warehouse_id', 'in',\
                logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('id', 'in', domain)]
        return []
