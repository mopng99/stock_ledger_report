# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    search_location_route_ids = fields.Char(compute='_compute_search_ids',
                                            search='search_location_routes')

    @api.depends('search_location_route_ids')
    def _compute_search_ids(self):
        pass

    def search_location_routes(self, operator, operand):
        """returns the allowed stock location routes ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            domain = self.search([('warehouse_ids', 'in',\
                logged_in_user.default_stock_warehouse_ids.ids)]).ids
            return [('id', 'in', domain)]
        return []

    @api.depends('company_id')
    def _compute_warehouses(self):
        res = super()._compute_warehouses()
        for loc in self:
            logged_in_user = self.env.user
            if logged_in_user.restrict_warehouse_operations:
                domain = [('id', 'in', logged_in_user.default_stock_warehouse_ids.ids),
                          ('company_id', '=', loc.company_id.id)]
                loc.warehouse_domain_ids = self.env['stock.warehouse'].search(domain)
        return res
