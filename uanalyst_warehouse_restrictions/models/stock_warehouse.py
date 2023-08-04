# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    search_warehouse_ids = fields.Char(compute='_compute_warehouse_ids',
                                       search='warehouse_ids_search')

    @api.depends('search_warehouse_ids')
    def _compute_warehouse_ids(self):
        pass

    def warehouse_ids_search(self, operator, operand):
        """return allow warehouse ids"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            return [('id', 'in', logged_in_user.default_stock_warehouse_ids.ids)]
        return []
