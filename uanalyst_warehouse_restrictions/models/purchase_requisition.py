# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def _get_picking_in(self):
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            pick_in = self.env['stock.picking.type'].search(\
                [('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids),
                 ('code', '=', 'incoming'),], limit=1)
            return pick_in
        res = super()._get_picking_in()
        return res

    @api.model
    def _get_allowed_operation_type_ids(self):
        """returns the allowed warehouse ids related operation types"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            return [('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids),
                    ('warehouse_id.company_id', '=', self.env.company.id)]
        return ['|', ('warehouse_id', '=', False),
                ('warehouse_id.company_id', '=', self.env.company.id)]

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      required=True, default=_get_picking_in,
                                      domain=lambda self: self._get_allowed_operation_type_ids())

    search_purchase_requisition_ids = fields.Char(compute='_compute_purchase_requisition_ids_search',
                                            search='purchase_requisition_ids_search')

    @api.depends('search_purchase_requisition_ids')
    def _compute_purchase_requisition_ids_search(self):
        pass

    def purchase_requisition_ids_search(self, operator, operand):
        """Purchase personal user"""
        if self.user_has_groups('uanalyst_warehouse_restrictions.group_purchase_purchaserepresentative'):
            return ['|', ('user_id', '=', self.env.user.id), ('user_id', '=', False)]
        return []
