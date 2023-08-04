# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_picking_type(self, company_id):
        logged_in_user = self.env.user
        if logged_in_user.restrict_warehouse_operations:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids),
                 ('warehouse_id.company_id', '=', company_id)])
            if not picking_type:
                picking_type = self.env['stock.picking.type'].search(\
                    [('code', '=', 'incoming'),
                     ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids),
                     ('warehouse_id', '=', False)])
            return picking_type[:1]
        res = super()._get_picking_type(company_id)
        return res

    def _domain_picking_type(self):
        """returns the operations types based on the purchase personal user
        and allowed wareshouse configuration"""
        if self.user_has_groups('uanalyst_warehouse_restrictions.group_purchase_purchaserepresentative'):
            logged_in_user = self.env.user
            if logged_in_user.restrict_warehouse_operations:
                return [('code', '=', 'incoming'),
                        ('warehouse_id.company_id', '=', self.company_id.id or self.env.company.id),
                        ('warehouse_id', 'in', logged_in_user.default_stock_warehouse_ids.ids)]
        return [('code', '=', 'incoming'), '|', ('warehouse_id', '=', False),
                ('warehouse_id.company_id', '=', self.company_id.id or self.env.company.id)]

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',
                                      domain=lambda self:self._domain_picking_type())

    search_purchase_order_ids = fields.Char(compute='_compute_picking_types_ids_search',
                                            search='purchase_order_ids_search')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        #picking_type_id field by default  set to the empty.
        super(PurchaseOrder, self)._onchange_company_id()
        if self.user_has_groups('stock.group_stock_multi_locations'):
            self.picking_type_id = False

    @api.depends('search_purchase_order_ids')
    def _compute_purchase_order_ids_search(self):
        pass

    def purchase_order_ids_search(self, operator, operand):
        """purchase personal user"""
        logged_in_user = self.env.user
        if self.user_has_groups('uanalyst_warehouse_restrictions.group_purchase_purchaserepresentative'):
            if self.env.ref('purchase.purchase_rfq'):
                return ['|', ('user_id', '=', logged_in_user.id), ('user_id', '=', False)]
            if self.env.ref('purchase.purchase_form_action'):
                return ['|', ('user_id', '=', logged_in_user.id), ('user_id', '=', False)]
        return []
