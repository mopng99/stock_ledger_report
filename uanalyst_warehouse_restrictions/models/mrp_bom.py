# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _domain_picking_type(self):
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            return [('code', '=', 'mrp_operation'),
                    ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids)]
        return [('code', '=', 'mrp_operation'),
                ('company_id', '=', self.company_id.id or self.env.company.id)]

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      domain=lambda self: self._domain_picking_type())
