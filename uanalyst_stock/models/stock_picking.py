# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_transfer_cost = fields.Monetary(string="Total Transfer Cost", copy=False)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.company.currency_id)

    def button_validate(self):
        res = super().button_validate()
        for record in self:
            #compute the total transfer cost based on the detailed stock operations
            if self.show_operations:
                total_transfer_cost = \
                    sum([move.total_line_cost for move in record.move_line_ids_without_package])
                record.total_transfer_cost = total_transfer_cost
            else:
                #compute the total transfer cost based on the stock operations
                total_transfer_cost = \
                    sum([move.total_line_cost for move in record.move_ids_without_package])
                record.total_transfer_cost = total_transfer_cost
        return res
