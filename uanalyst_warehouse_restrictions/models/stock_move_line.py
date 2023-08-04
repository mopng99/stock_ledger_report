# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    on_hand_qty = fields.Float(string="On Hand Qty", compute='_compute_product_on_hand_qty',
                               store=False, help="Product On Hand Qty. based on Source Location.")

    @api.depends('product_id')
    def _compute_product_on_hand_qty(self):
        """_summary_
        compute the product On Hand Qty based on source location.
        """
        for record in self:
            source_location_id = record.location_id.id or record.picking_id.location_id.id
            quant_query = \
                self.env['stock.quant'].search([('product_id', '=', record.product_id.id),
                                                ('location_id', '=', source_location_id),
                                                ('on_hand', '=', True)])
            record.on_hand_qty = sum([r.quantity for r in quant_query])
