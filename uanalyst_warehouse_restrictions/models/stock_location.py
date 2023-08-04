# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Location(models.Model):
    _inherit = "stock.location"

    @api.model
    def _get_allowed_parent_stock_location_ids(self):
        """returns the allowed locations ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            return [('id', 'in', logged_in_user.restrict_stock_location_ids.ids)]
        return [('id', 'in', self.search([]).ids)]

    search_stock_location_ids = fields.Char(compute='_compute_stock_location_ids',
                                            search='search_location_ids_search')
    @api.depends('search_stock_location_ids')
    def _compute_stock_location_ids(self):
        pass

    def search_location_ids_search(self, operator, operand):
        """return allowed stock locations ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            return [('id', 'in', logged_in_user.restrict_stock_location_ids.ids)]
        return []

    location_id = fields.Many2one('stock.location', 'Parent Location',\
                                  domain=lambda self: self._get_allowed_parent_stock_location_ids())
