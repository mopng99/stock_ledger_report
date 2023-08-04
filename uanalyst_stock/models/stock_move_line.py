# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    total_line_cost = fields.Monetary(string="Total Line Cost",
                                      compute='_compute_product_line_cost', store=True)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.company.currency_id)

    @api.depends('product_id', 'qty_done')
    def _compute_product_line_cost(self):
        """_summary_
            total Line Cost = done quantity * compute product cost per uom
        """
        for record in self.filtered(lambda r: r.product_id and r.product_uom_id):
            per_uom_cost = record.product_id.uom_id._compute_price(record.product_id.standard_price,
                                                                   record.product_uom_id)
            record.total_line_cost = per_uom_cost * record.qty_done
