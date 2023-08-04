# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class StockLedgerReport(models.Model):
    _name = 'stock.ledger.report'
    # _auto = True
    _rec_name = 'date'
    _order = 'date asc'
    _description = 'Stock ledger report'

    location_id_report = fields.Many2one('stock.location', 'Test Location', readonly=True)
    scheduled_date = fields.Datetime('Scheduled Date', help='Scheduled time for the first part of'
                                                            'the shipment to be processed. Setting manually a value here'
                                                            'would set it as expected date for all the stock moves.')
    date = fields.Datetime(string='Date Processing',
                           help='Scheduled date until move is done,'
                                'then date of actual move processing')
    reference = fields.Char(string="Reference", readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Contact")
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template',
                                      related='product_id.product_tmpl_id', readonly=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    uom_po_id = fields.Many2one('uom.uom', 'Purchase UoM', readonly=True)
    location_id = fields.Many2one('stock.location', 'From', readonly=True)
    location_dest_id = fields.Many2one('stock.location', 'To', readonly=True)
    # UOM i.e stock_move.uom_id wise compute fields
    inward_stock = fields.Float(string='In. Qty', readonly=True)
    outward_stock = fields.Float(string='Out. Qty', readonly=True)
    balance_qty = fields.Float(string='Balance Qty.', readonly=True, group_operator=False)
    # Purchase UOM i.e product_id.po_uom_id wise compute fields
    uom_po_inward_stock = fields.Float(string='In. Qty', readonly=True)
    uom_po_outward_stock = fields.Float(string='Out. Qty', readonly=True)
    uom_po_balance_qty = fields.Float(string='Balance Qty.', readonly=True, group_operator=False)
    # transfer cost i.e stock_move.total_line_cost
    total_line_cost = fields.Monetary(string='Total Line Cost')
    in_total_line_cost = fields.Monetary(string='In. Total Line Cost')
    out_total_line_cost = fields.Monetary(string='Out. Total Line Cost')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', readonly=True)
    type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('return', 'Return'),
        ('internal', 'Internal'),
        ('scrap', 'Scrap'),
    ], readonly=True)
    company_id = fields.Many2one('res.company', 'Company')
    # hidden fields from view but used in search view/ Other dependency
    product_category = fields.Char(string='Product Category', readonly=True)
    product_active = fields.Boolean(help="Product Archived/ Un-Archived.", readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status')

