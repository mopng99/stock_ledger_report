# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, Command, tools, _


class Location(models.Model):
    _inherit = "stock.location"

    stock_ledger_report_ids = fields.One2many('stock.ledger.report',
                                              'location_id_report')

    def compute_transactions_report(self):
        tools.drop_view_if_exists(self.env.cr, 'stock_ledger_report_temp1')
        self.env.cr.execute('''CREATE OR REPLACE VIEW stock_ledger_report_temp1 AS (
            SELECT MIN(sm.id) AS id,
                    sp.scheduled_date as scheduled_date,
                    sm.date,
                    sm.product_id,
                    sale_uom.id as uom_id,
                    purchase_uom.id as uom_po_id,
                    sp.partner_id,
                    sm.reference,
                    sm.location_dest_id,
                    sm.location_id,
                    sm.picking_type_id,
                    sm.scrapped,
                    sm.to_refund,
                    source_location.usage as source_location_usgae,
                    dest_location.usage as dest_location_usage,
                    sm.total_line_cost,
                    product_categ.complete_name as product_category,
                    CASE
						WHEN (purchase_uom.uom_type='reference') THEN
							COALESCE(purchase_uom.factor,0.0)
						WHEN (purchase_uom.uom_type='bigger') THEN
							COALESCE(1.0/purchase_uom.factor,0.0)
						ELSE
							COALESCE(purchase_uom.factor,0.0)
						END AS po_uom_ratio,
                    CASE
                        WHEN (sm.location_dest_id=%s) THEN
                            COALESCE(sum(sm.product_qty),0.0)
                        ELSE
                            0.0 END AS inward_stock,
                    CASE
                        WHEN (sm.location_id=%s) THEN
                            COALESCE(sum(sm.product_qty),0.0)
                        ELSE
                            0.0 END AS outward_stock,
                    sm.state,
                    sm.company_id,
                    pp.active as product_active
            from stock_move sm
            LEFT JOIN product_product pp ON (sm.product_id=pp.id)
            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
            LEFT JOIN stock_location dest_location ON sm.location_dest_id = dest_location.id
            LEFT JOIN stock_location source_location ON sm.location_id = source_location.id
            LEFT JOIN product_category product_categ ON (product_categ.id=pt.categ_id)
            LEFT JOIN uom_uom purchase_uom ON purchase_uom.id=pt.uom_po_id
            LEFT JOIN uom_uom sale_uom ON sale_uom.id=pt.uom_id
            LEFT JOIN stock_picking sp on sp.id=sm.picking_id
            WHERE sm.state='done' and (sm.location_id=%s or sm.location_dest_id=%s)
            GROUP BY
                sm.state,
                sp.scheduled_date,
                sm.date,
                sm.company_id,
                sm.product_id,
                purchase_uom.uom_type,
                purchase_uom.factor,
                sale_uom.id,
                purchase_uom.id,
                sm.product_qty,
                source_location.usage,
                dest_location.usage,
                sp.partner_id,
                sm.reference,
                sm.location_dest_id,
                sm.location_id,
                sm.picking_type_id,
                sm.scrapped,
                sm.to_refund,
                pp.active,
                sm.total_line_cost,
                product_categ.complete_name
            ORDER BY sm.product_id)''', (self.id, self.id, self.id, self.id))
        tools.drop_view_if_exists(self.env.cr, 'stock_ledger_report_temp2')
        self.env.cr.execute('''CREATE OR REPLACE VIEW stock_ledger_report_temp2 AS (SELECT
                                MIN(temp1.id) AS id,
                                temp1.scheduled_date,
                                temp1.date,
                                temp1.product_id,
                                temp1.uom_id,
                                temp1.uom_po_id,
                                temp1.po_uom_ratio,
                                temp1.location_dest_id,
                                temp1.location_id,
                                temp1.partner_id,
                                temp1.reference,
                                temp1.picking_type_id,
                                temp1.total_line_cost,
                                temp1.product_active,
                                temp1.inward_stock,
                                temp1.outward_stock,
                                temp1.product_category,
                                CASE WHEN (temp1.scrapped = 'true') THEN
                                    COALESCE('scrap','')
                                WHEN (temp1.to_refund='true') THEN
                                    COALESCE('return','')
                                WHEN (temp1.source_location_usgae = 'customer') THEN
                                    COALESCE('return','')
                                WHEN (temp1.dest_location_usage = 'customer' OR temp1.dest_location_usage = 'supplier') THEN
                                    COALESCE('sale','')
                                WHEN (temp1.source_location_usgae = 'supplier') THEN
                                    COALESCE('purchase','')
                                ELSE 'internal' END AS type,
                            SUM(SUM(inward_stock) - SUM(outward_stock)) OVER (
                                PARTITION BY temp1.company_id, temp1.product_id 
                                ORDER BY temp1.date
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                            ) AS balance_qty,
                            COALESCE(temp1.inward_stock/temp1.po_uom_ratio) As uom_po_inward_stock,
                            COALESCE(temp1.outward_stock/temp1.po_uom_ratio) As uom_po_outward_stock,
                            temp1.state,
                            temp1.company_id
            FROM stock_ledger_report_temp1 temp1
            GROUP BY temp1.scheduled_date,
                    temp1.date,
                    temp1.product_id,
                    temp1.uom_id,
                    temp1.uom_po_id,
                    temp1.po_uom_ratio,
                    temp1.partner_id,
                    temp1.reference,
                    temp1.inward_stock,
                    temp1.outward_stock,
                    temp1.state,
                    temp1.company_id,
                    temp1.location_dest_id,
                    temp1.location_id,
                    temp1.picking_type_id,
                    temp1.total_line_cost,
                    temp1.product_active,
                    temp1.scrapped,
                    temp1.to_refund,
                    temp1.dest_location_usage,
                    temp1.source_location_usgae,
                    temp1.product_category
            ORDER BY temp1.date)''')
        temp3_query = """SELECT temp2.scheduled_date,
                                temp2.date,
                                temp2.product_id,
                                temp2.uom_id,
                                temp2.uom_po_id,
                                temp2.location_dest_id,
                                temp2.location_id,
                                temp2.partner_id,
                                temp2.reference,
                                temp2.picking_type_id,
                                temp2.product_active,
                                temp2.inward_stock,
                                temp2.outward_stock,
                                CASE
                                    WHEN (temp2.inward_stock=0) THEN COALESCE(temp2.total_line_cost,0.0)
                                    ELSE 0.0 
                                    END AS out_total_line_cost,
                                CASE
                                    WHEN (temp2.outward_stock=0) THEN COALESCE(temp2.total_line_cost,0.0)
                                    ELSE 0.0 
                                    END AS in_total_line_cost,
                                temp2.product_category,
                           		temp2.balance_qty,
								temp2.uom_po_inward_stock,
                                temp2.uom_po_outward_stock,
							 	COALESCE(temp2.balance_qty/temp2.po_uom_ratio) As uom_po_balance_qty,
								temp2.state,
                                temp2.type,
								temp2.company_id
            FROM stock_ledger_report_temp2 temp2
            GROUP BY temp2.scheduled_date,
                    temp2.date,
                    temp2.product_id,
                    temp2.uom_id,
                    temp2.uom_po_id,
					temp2.po_uom_ratio,
                    temp2.partner_id,
                    temp2.reference,
                    temp2.inward_stock,
                    temp2.outward_stock,
					temp2.balance_qty,
					temp2.uom_po_inward_stock,
					temp2.uom_po_outward_stock,
                    temp2.state,
                    temp2.company_id,
                    temp2.location_dest_id,
                    temp2.location_id,
                    temp2.picking_type_id,
                    temp2.total_line_cost,
                    temp2.product_active,
                    temp2.type,
                    temp2.product_category
            ORDER BY temp2.date"""
        self.env.cr.execute(temp3_query)
        result_temp3_query = self.env.cr.dictfetchall()
        self.env.cr.execute("delete from stock_ledger_report where location_id_report=%s",
                            [self.id])
        self.update({'stock_ledger_report_ids': \
                         [Command.create(record) for record in result_temp3_query]})
