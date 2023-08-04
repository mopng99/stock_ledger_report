# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    # as per client request default picking_type_id manual MO creation time set empty
    # # @api.model
    # # def _get_default_picking_type(self):
    # #     logged_in_user = self.env.user
    # #     if logged_in_user.restrict_warehouse_operations:
    # #         picking_type_obj = self.env['stock.picking.type'].search([
    # #             ('code', '=', 'mrp_operation'),
    # #             ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids),
    # #         ], limit=1)
    # #         return picking_type_obj.id or False
    # #     return super()._get_default_picking_type()

    def _domain_picking_type(self):
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            return [('code', '=', 'mrp_operation'),
                    ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids)]
        return [('code', '=', 'mrp_operation'),
                ('company_id', '=', self.company_id.id or self.env.company.id)]

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', default=False,
                                      domain=lambda self: self._domain_picking_type())

    @api.onchange('company_id')
    def _onchange_company_id(self):
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            if self.move_raw_ids:
                self.move_raw_ids.update({'company_id': self.company_id})
            if self.picking_type_id and self.picking_type_id.company_id != self.company_id:
                self.picking_type_id = self.env['stock.picking.type'].search([
                    ('code', '=', 'mrp_operation'),
                    ('warehouse_id.company_id', '=', self.company_id.id),
                    ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids)
                ], limit=1).id or False
        return super()._onchange_company_id()
