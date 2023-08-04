# -*- coding: utf-8 -*-
import ast
import json

from odoo.osv.expression import AND
from odoo import api, models, fields, _
from datetime import datetime, time
from calendar import monthrange
import xlsxwriter
import io


class ReportExcelStockLedgerWizard(models.TransientModel):
    _name = 'report.excel.stock.ledger.wizard'
    _description = 'Report Excel Stock Ledger Wizard'

    def _allow_user_base_locations(self):
        """returns the user allowed locations"""
        logged_in_user = self.env.user
        if logged_in_user.restrict_stock_locations:
            return [('id', 'in', logged_in_user.restrict_stock_location_ids.ids),
                    ('usage', '!=', 'view')]
        return [('usage', '!=', 'view')]

    def _last_day_of_month(date_value):
        return date_value.replace(day=monthrange(date_value.year, date_value.month)[1])

    location_id = fields.Many2one('stock.location', required=False, string='Stock Ledger Location',
                                  domain=lambda self: self._allow_user_base_locations())
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    uom_options = fields.Selection([('product_unit_of_measure', 'Unit of Measure'),
                                    ('purchase_uom', 'Purchase UoM')],
                                   string='UOM Options', default='product_unit_of_measure')
    from_date = fields.Date('From Date', required=True,
                            default=fields.Datetime.today().replace(day=1))
    to_date = fields.Date('To Date', required=True,
                          default=_last_day_of_month(fields.Datetime.today().date()))
    group_by_options = fields.Selection([('per_line', 'By Line'),
                                         ('group_by_category', 'By Product Category'),
                                         ('group_by_product', 'By Product'),
                                         ('group_by_product_category', 'By Product Category + Product'),
                                         ('group_by_contact_product', 'By Contact + Product'),
                                         ('group_by_contact', 'By Contact'),
                                         ('group_by_scheduled_date_product', 'By Scheduled Date + Product'),
                                         ('group_by_effective_date_product', 'By Effective date + Product')],
                                        string='Group By Options', default='per_line')
    filter_id = fields.Many2one('ir.filters', string='Favorite Filter',
                                domain=[('model_id', '=', 'stock.ledger.report')])

    def action_print_excel_report(self):
        self.location_id.sudo().compute_transactions_report()
        return {
            'type': "ir.actions.act_url",
            'target': "new",
            'tag': 'reload',
            'url': "/web/content/download/stock_ledger_report?from_date={from_date}&to_date={to_date}&location_id={location_id_report}&uom_options={uom_options}&group_by_options={group_by_options}&filter_id={filter_id}".format(
                from_date=self.from_date, to_date=self.to_date,
                location_id_report=self.location_id.ids,
                group_by_options=self.group_by_options,
                uom_options=self.uom_options,
                filter_id=self.filter_id,
            )
        }

    def get_xlsx_report(self, response, from_date, to_date, location_id_report, uom_options, group_by_options, filter_id):
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
        domain = ['&', ('location_id_report', 'in', location_id_report),
                  '&', ('date', '>=', datetime.combine(from_date, time.min)),
                  ('date', '<=', datetime.combine(to_date, time.max))]
        stock_ledger_id = self.env['stock.ledger.report'].search(domain)
        if filter_id:
            filter_id = self.env['ir.filters'].browse(int(filter_id[0]))
            domain_2 = ast.literal_eval(filter_id.domain)
            domain = AND([domain, domain_2])
            stock_ledger_id = self.env['stock.ledger.report'].search(domain)

        data_dict = {}

        for rec in stock_ledger_id:
            if rec.product_category in data_dict:
                if rec.product_id.name in data_dict[rec.product_category]:
                    data_dict[rec.product_category][rec.product_id.name].append(rec)
                else:
                    data_dict[rec.product_category][rec.product_id.name] = [rec]
            else:
                data_dict[rec.product_category] = {}
                data_dict[rec.product_category][rec.product_id.name] = [rec]

        # for key1, value1 in data_dict.items():
        #     print(f"{key1}: {{")
        #     for key2, value2 in value1.items():
        #         print(f"    {key2}: {value2}")
        #     print("}")

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'strings_to_formulas': False, })
        sheet = workbook.add_worksheet('Stock Ledger')
        sheet.set_column('A:O', 40)
        sheet.set_default_row(25)
        date_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'align': 'center', 'font_size': 11, 'num_format': 'yyyy-mm-dd'})
        text_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'font_size': 11})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': '#071f75', 'font_size': 16, 'font_color': 'white',
             'bold': True, 'align': 'center', 'border': 2, 'left': 1,
             'bottom': 1,
             'right': 1, 'top': 1})
        pro_cat_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': 'red', 'font_size': 16,
             'bold': True, 'align': 'center', 'border': 2, 'left': 1,
             'bottom': 1,
             'right': 1, 'top': 1})
        pro_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': 'yellow', 'font_size': 13,
             'bold': True, 'align': 'center', 'border': 2, 'left': 1,
             'bottom': 1,
             'right': 1, 'top': 1})

        row = 0
        col = 0
        if group_by_options == 'group_by_product_category':
            sheet.write(row, col, 'Product Category', header_style)
            sheet.write(row, col + 1, 'Product', header_style)
            sheet.write(row, col + 2, 'Scheduled Date', header_style)
            sheet.write(row, col + 3, 'Date Processing', header_style)
            sheet.write(row, col + 4, 'Reference', header_style)
            sheet.write(row, col + 5, 'Contact', header_style)
            sheet.write(row, col + 6, 'Product', header_style)
            if uom_options == 'product_unit_of_measure':
                sheet.write(row, col + 7, 'Unite of Measure', header_style)
            else:
                sheet.write(row, col + 7, 'Purchase UoM', header_style)
            sheet.write(row, col + 8, 'From', header_style)
            sheet.write(row, col + 9, 'To', header_style)
            sheet.write(row, col + 10, 'In. Qty', header_style)
            sheet.write(row, col + 11, 'Out. Qty', header_style)
            sheet.write(row, col + 12, 'Balance. Qty', header_style)
            sheet.write(row, col + 13, 'In. Total Cost', header_style)
            sheet.write(row, col + 14, 'Out. Total Cost', header_style)

            count_cat = 0
            count_pro = 0
            in_total_cost_cat = 0
            in_qty_cat = 0
            out_total_cost_cat = 0
            out_qty_cat = 0
            in_total_cost_pro = 0
            in_qty_pro = 0
            out_total_cost_pro = 0
            out_qty_pro = 0
            for product_category in data_dict:
                col = 0
                row += 1

                sheet.write(row, col, product_category, pro_cat_style)

                for product_id in data_dict[product_category]:
                    col = 1
                    row += 1
                    count_pro = row
                    sheet.write(row, col, product_id, pro_style)

                    for stock in data_dict[product_category][product_id]:
                        col = 2
                        row += 1

                        sheet.write(row, col, stock.scheduled_date, date_style)
                        col += 1
                        sheet.write(row, col, stock.date, date_style)
                        col += 1
                        sheet.write(row, col, stock.reference, text_style)
                        col += 1
                        sheet.write(row, col, stock.partner_id.name, text_style)
                        col += 1
                        sheet.write(row, col, stock.product_id.name, text_style)
                        col += 1
                        if uom_options == 'product_unit_of_measure':
                            sheet.write(row, col, stock.uom_id.name, text_style)
                            col += 1
                        else:
                            sheet.write(row, col, stock.uom_po_id.name, text_style)
                            col += 1
                        sheet.write(row, col, stock.location_id.name, text_style)
                        col += 1
                        sheet.write(row, col, stock.location_dest_id.name, text_style)
                        col += 1
                        if uom_options == 'product_unit_of_measure':
                            sheet.write(row, col, round(stock.inward_stock, 2), text_style)
                            col += 1
                            sheet.write(row, col, round(stock.outward_stock, 2), text_style)
                            col += 1
                            sheet.write(row, col, round(stock.balance_qty, 2), text_style)
                            col += 1
                        else:
                            sheet.write(row, col, round(stock.uom_po_inward_stock, 2), text_style)
                            col += 1
                            sheet.write(row, col, round(stock.uom_po_outward_stock, 2), text_style)
                            col += 1
                            sheet.write(row, col, round(stock.uom_po_balance_qty, 2), text_style)
                            col += 1

                        sheet.write(row, col, round(stock.in_total_line_cost, 2), text_style)
                        col += 1
                        sheet.write(row, col, round(stock.out_total_line_cost, 2), text_style)
                        col += 1
                        out_total_cost_pro += stock.out_total_line_cost
                        in_total_cost_pro += stock.in_total_line_cost

                        if uom_options == 'product_unit_of_measure':
                            out_qty_pro += stock.outward_stock
                            in_qty_pro += stock.inward_stock
                        else:
                            out_qty_pro += stock.uom_po_outward_stock
                            in_qty_pro += stock.uom_po_inward_stock

                    col = 1
                    sheet.write(count_pro, col + 9, round(in_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 10, round(out_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 12, in_total_cost_pro, pro_style)
                    sheet.write(count_pro, col + 13, out_total_cost_pro, pro_style)

                    in_qty_cat += in_qty_pro
                    out_qty_cat += out_qty_pro
                    in_total_cost_cat += in_total_cost_pro
                    out_total_cost_cat += out_total_cost_pro

                    in_qty_pro = 0
                    out_qty_pro = 0
                    in_total_cost_pro = 0
                    out_total_cost_pro = 0

                col = 1
                if count_cat == 0:
                    count_cat = 1

                sheet.write(count_cat, col + 9, round(in_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 10, round(out_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 12, in_total_cost_cat, pro_cat_style)
                sheet.write(count_cat, col + 13, out_total_cost_cat, pro_cat_style)
                in_qty_cat = 0
                out_qty_cat = 0
                in_total_cost_cat = 0
                out_total_cost_cat = 0
                count_cat = row + 1

        if group_by_options == 'group_by_category':
            sheet.write(row, col, 'Product Category', header_style)
            sheet.write(row, col + 1, 'In. Qty', header_style)
            sheet.write(row, col + 2, 'Out. Qty', header_style)
            sheet.write(row, col + 3, 'In. Total Cost', header_style)
            sheet.write(row, col + 4, 'Out. Total Cost', header_style)

            in_total_cost_cat = 0
            in_qty_cat = 0
            out_total_cost_cat = 0
            out_qty_cat = 0
            for product_category in data_dict:
                col = 0
                row += 1

                sheet.write(row, col, product_category, pro_cat_style)

                for product_id in data_dict[product_category]:
                    for stock in data_dict[product_category][product_id]:
                        out_total_cost_cat += stock.out_total_line_cost
                        in_total_cost_cat += stock.in_total_line_cost

                        if uom_options == 'product_unit_of_measure':
                            out_qty_cat += stock.outward_stock
                            in_qty_cat += stock.inward_stock
                        else:
                            out_qty_cat += stock.uom_po_outward_stock
                            in_qty_cat += stock.uom_po_inward_stock

                sheet.write(row, col + 1, round(in_qty_cat, 2), pro_cat_style)
                sheet.write(row, col + 2, round(out_qty_cat, 2), pro_cat_style)
                sheet.write(row, col + 3, in_total_cost_cat, pro_cat_style)
                sheet.write(row, col + 4, out_total_cost_cat, pro_cat_style)
                in_qty_cat = 0
                out_qty_cat = 0
                in_total_cost_cat = 0
                out_total_cost_cat = 0

        if group_by_options == 'group_by_product':
            sheet.write(row, col, 'Product', header_style)
            if uom_options == 'product_unit_of_measure':
                sheet.write(row, col + 1, 'Unite of Measure', header_style)
            else:
                sheet.write(row, col + 1, 'Purchase UoM', header_style)
            sheet.write(row, col + 2, 'In. Qty', header_style)
            sheet.write(row, col + 3, 'Out. Qty', header_style)
            sheet.write(row, col + 4, 'In. Total Cost', header_style)
            sheet.write(row, col + 5, 'Out. Total Cost', header_style)

            in_qty_pro = 0
            out_qty_pro = 0
            in_total_cost_pro = 0
            out_total_cost_pro = 0
            for product_category in data_dict:
                for product_id in data_dict[product_category]:
                    col = 0
                    row += 1
                    sheet.write(row, col, product_id, pro_style)
                    for stock in data_dict[product_category][product_id]:
                        out_total_cost_pro += stock.out_total_line_cost
                        in_total_cost_pro += stock.in_total_line_cost

                        if uom_options == 'product_unit_of_measure':
                            out_qty_pro += stock.outward_stock
                            in_qty_pro += stock.inward_stock
                        else:
                            out_qty_pro += stock.uom_po_outward_stock
                            in_qty_pro += stock.uom_po_inward_stock

                    if uom_options == 'product_unit_of_measure':
                        sheet.write(row, col + 1, stock.uom_id.name, text_style)
                    else:
                        sheet.write(row, col + 1, stock.uom_po_id.name, text_style)
                    sheet.write(row, col + 2, round(in_qty_pro, 2), pro_style)
                    sheet.write(row, col + 3, round(out_qty_pro, 2), pro_style)
                    sheet.write(row, col + 4, in_total_cost_pro, pro_style)
                    sheet.write(row, col + 5, out_total_cost_pro, pro_style)

                    in_qty_pro = 0
                    out_qty_pro = 0
                    in_total_cost_pro = 0
                    out_total_cost_pro = 0

        if group_by_options == 'per_line':
            sheet.write(row, col, 'Scheduled Date', header_style)
            sheet.write(row, col + 1, 'Date Processing', header_style)
            sheet.write(row, col + 2, 'Reference', header_style)
            sheet.write(row, col + 3, 'Contact', header_style)
            sheet.write(row, col + 4, 'Product', header_style)
            if uom_options == 'product_unit_of_measure':
                sheet.write(row, col + 5, 'Unite of Measure', header_style)
            else:
                sheet.write(row, col + 5, 'Purchase UoM', header_style)
            sheet.write(row, col + 6, 'From', header_style)
            sheet.write(row, col + 7, 'To', header_style)
            sheet.write(row, col + 8, 'In. Qty', header_style)
            sheet.write(row, col + 9, 'Out. Qty', header_style)
            sheet.write(row, col + 10, 'Balance. Qty', header_style)
            sheet.write(row, col + 11, 'In. Total Cost', header_style)
            sheet.write(row, col + 12, 'Out. Total Cost', header_style)

            for stock in stock_ledger_id:
                col = 0
                row += 1

                sheet.write(row, col, stock.scheduled_date, date_style)
                col += 1
                sheet.write(row, col, stock.date, date_style)
                col += 1
                sheet.write(row, col, stock.reference, text_style)
                col += 1
                sheet.write(row, col, stock.partner_id.name, text_style)
                col += 1
                sheet.write(row, col, stock.product_id.name, text_style)
                col += 1
                if uom_options == 'product_unit_of_measure':
                    sheet.write(row, col, stock.uom_id.name, text_style)
                    col += 1
                else:
                    sheet.write(row, col, stock.uom_po_id.name, text_style)
                    col += 1
                sheet.write(row, col, stock.location_id.name, text_style)
                col += 1
                sheet.write(row, col, stock.location_dest_id.name, text_style)
                col += 1
                if uom_options == 'product_unit_of_measure':
                    sheet.write(row, col, round(stock.inward_stock, 2), text_style)
                    col += 1
                    sheet.write(row, col, round(stock.outward_stock, 2), text_style)
                    col += 1
                    sheet.write(row, col, round(stock.balance_qty, 2), text_style)
                    col += 1
                else:
                    sheet.write(row, col, round(stock.uom_po_inward_stock, 2), text_style)
                    col += 1
                    sheet.write(row, col, round(stock.uom_po_outward_stock, 2), text_style)
                    col += 1
                    sheet.write(row, col, round(stock.uom_po_balance_qty, 2), text_style)
                    col += 1

                sheet.write(row, col, round(stock.in_total_line_cost, 2), text_style)
                col += 1
                sheet.write(row, col, round(stock.out_total_line_cost, 2), text_style)
                col += 1

        if group_by_options == 'group_by_scheduled_date_product':
            data_dict = {}
            for rec in stock_ledger_id:
                if rec.scheduled_date.date() in data_dict:
                    if rec.product_id.name in data_dict[rec.scheduled_date.date()]:
                        data_dict[rec.scheduled_date.date()][rec.product_id.name].append(rec)
                    else:
                        data_dict[rec.scheduled_date.date()][rec.product_id.name] = [rec]
                else:
                    data_dict[rec.scheduled_date.date()] = {}
                    data_dict[rec.scheduled_date.date()][rec.product_id.name] = [rec]

            sheet.write(row, col, 'Scheduled Date', header_style)
            sheet.write(row, col + 1, 'Product', header_style)
            if uom_options == 'product_unit_of_measure':
                sheet.write(row, col + 2, 'Unite of Measure', header_style)
            else:
                sheet.write(row, col + 2, 'Purchase UoM', header_style)
            sheet.write(row, col + 3, 'In. Qty', header_style)
            sheet.write(row, col + 4, 'Out. Qty', header_style)
            sheet.write(row, col + 5, 'In. Total Cost', header_style)
            sheet.write(row, col + 6, 'Out. Total Cost', header_style)

            count_cat = 0
            count_pro = 0
            in_total_cost_cat = 0
            in_qty_cat = 0
            out_total_cost_cat = 0
            out_qty_cat = 0
            in_total_cost_pro = 0
            in_qty_pro = 0
            out_total_cost_pro = 0
            out_qty_pro = 0
            for scheduled_date in data_dict:
                col = 0
                row += 1

                sheet.write(row, col, str(scheduled_date.year) + '-' + str(scheduled_date.month) + '-' + str(scheduled_date.day), pro_cat_style)

                for product_id in data_dict[scheduled_date]:
                    col = 1
                    row += 1
                    count_pro = row
                    sheet.write(row, col, product_id, pro_style)

                    for stock in data_dict[scheduled_date][product_id]:
                        out_total_cost_pro += stock.out_total_line_cost
                        in_total_cost_pro += stock.in_total_line_cost

                        if uom_options == 'product_unit_of_measure':
                            out_qty_pro += stock.outward_stock
                            in_qty_pro += stock.inward_stock
                        else:
                            out_qty_pro += stock.uom_po_outward_stock
                            in_qty_pro += stock.uom_po_inward_stock

                    col = 1
                    if uom_options == 'product_unit_of_measure':
                        sheet.write(row, col + 1, stock.uom_id.name, pro_style)
                    else:
                        sheet.write(row, col + 1, stock.uom_po_id.name, pro_style)
                    sheet.write(count_pro, col + 2, round(in_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 3, round(out_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 4, in_total_cost_pro, pro_style)
                    sheet.write(count_pro, col + 5, out_total_cost_pro, pro_style)

                    in_qty_cat += in_qty_pro
                    out_qty_cat += out_qty_pro
                    in_total_cost_cat += in_total_cost_pro
                    out_total_cost_cat += out_total_cost_pro

                    in_qty_pro = 0
                    out_qty_pro = 0
                    in_total_cost_pro = 0
                    out_total_cost_pro = 0

                col = 1
                if count_cat == 0:
                    count_cat = 1

                sheet.write(count_cat, col + 2, round(in_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 3, round(out_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 4, in_total_cost_cat, pro_cat_style)
                sheet.write(count_cat, col + 5, out_total_cost_cat, pro_cat_style)
                in_qty_cat = 0
                out_qty_cat = 0
                in_total_cost_cat = 0
                out_total_cost_cat = 0
                count_cat = row + 1

        if group_by_options == 'group_by_contact':
            data_dict = {}
            for rec in stock_ledger_id:
                if rec.partner_id in data_dict:
                    data_dict[rec.partner_id].append(rec)
                else:
                    data_dict[rec.partner_id] = [rec]

            sheet.write(row, col, 'Contact', header_style)
            sheet.write(row, col + 1, 'In. Qty', header_style)
            sheet.write(row, col + 2, 'Out. Qty', header_style)
            sheet.write(row, col + 3, 'In. Total Cost', header_style)
            sheet.write(row, col + 4, 'Out. Total Cost', header_style)

            in_total_cost_sum = 0
            in_qty_sum = 0
            out_total_cost_sum = 0
            out_qty_sum = 0
            for partner_id in data_dict:
                col = 0
                row += 1

                sheet.write(row, col, partner_id.name, pro_cat_style)

                for stock in data_dict[partner_id]:
                    out_total_cost_sum += stock.out_total_line_cost
                    in_total_cost_sum += stock.in_total_line_cost

                    if uom_options == 'product_unit_of_measure':
                        out_qty_sum += stock.outward_stock
                        in_qty_sum += stock.inward_stock
                    else:
                        out_qty_sum += stock.uom_po_outward_stock
                        in_qty_sum += stock.uom_po_inward_stock

                sheet.write(row, col + 1, round(in_qty_sum, 2), pro_cat_style)
                sheet.write(row, col + 2, round(out_qty_sum, 2), pro_cat_style)
                sheet.write(row, col + 3, in_total_cost_sum, pro_cat_style)
                sheet.write(row, col + 4, out_total_cost_sum, pro_cat_style)
                in_total_cost_sum = 0
                in_qty_sum = 0
                out_total_cost_sum = 0
                out_qty_sum = 0

        if group_by_options == 'group_by_effective_date_product':
            data_dict = {}
            for rec in stock_ledger_id:
                if rec.date.date() in data_dict:
                    if rec.product_id.name in data_dict[rec.date.date()]:
                        data_dict[rec.date.date()][rec.product_id.name].append(rec)
                    else:
                        data_dict[rec.date.date()][rec.product_id.name] = [rec]
                else:
                    data_dict[rec.date.date()] = {}
                    data_dict[rec.date.date()][rec.product_id.name] = [rec]

            sheet.write(row, col, 'Effective Date', header_style)
            sheet.write(row, col + 1, 'Product', header_style)
            if uom_options == 'product_unit_of_measure':
                sheet.write(row, col + 2, 'Unite of Measure', header_style)
            else:
                sheet.write(row, col + 2, 'Purchase UoM', header_style)
            sheet.write(row, col + 3, 'In. Qty', header_style)
            sheet.write(row, col + 4, 'Out. Qty', header_style)
            sheet.write(row, col + 5, 'In. Total Cost', header_style)
            sheet.write(row, col + 6, 'Out. Total Cost', header_style)

            count_cat = 0
            count_pro = 0
            in_total_cost_cat = 0
            in_qty_cat = 0
            out_total_cost_cat = 0
            out_qty_cat = 0
            in_total_cost_pro = 0
            in_qty_pro = 0
            out_total_cost_pro = 0
            out_qty_pro = 0
            for date in data_dict:
                col = 0
                row += 1

                sheet.write(row, col, str(date.year) + '-' + str(date.month) + '-' + str(date.day), pro_cat_style)

                for product_id in data_dict[date]:
                    col = 1
                    row += 1
                    count_pro = row
                    sheet.write(row, col, product_id, pro_style)

                    for stock in data_dict[date][product_id]:
                        out_total_cost_pro += stock.out_total_line_cost
                        in_total_cost_pro += stock.in_total_line_cost

                        if uom_options == 'product_unit_of_measure':
                            out_qty_pro += stock.outward_stock
                            in_qty_pro += stock.inward_stock
                        else:
                            out_qty_pro += stock.uom_po_outward_stock
                            in_qty_pro += stock.uom_po_inward_stock

                    col = 1
                    if uom_options == 'product_unit_of_measure':
                        sheet.write(row, col + 1, stock.uom_id.name, pro_style)
                    else:
                        sheet.write(row, col + 1, stock.uom_po_id.name, pro_style)
                    sheet.write(count_pro, col + 2, round(in_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 3, round(out_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 4, in_total_cost_pro, pro_style)
                    sheet.write(count_pro, col + 5, out_total_cost_pro, pro_style)

                    in_qty_cat += in_qty_pro
                    out_qty_cat += out_qty_pro
                    in_total_cost_cat += in_total_cost_pro
                    out_total_cost_cat += out_total_cost_pro

                    in_qty_pro = 0
                    out_qty_pro = 0
                    in_total_cost_pro = 0
                    out_total_cost_pro = 0

                col = 1
                if count_cat == 0:
                    count_cat = 1

                sheet.write(count_cat, col + 2, round(in_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 3, round(out_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 4, in_total_cost_cat, pro_cat_style)
                sheet.write(count_cat, col + 5, out_total_cost_cat, pro_cat_style)
                in_qty_cat = 0
                out_qty_cat = 0
                in_total_cost_cat = 0
                out_total_cost_cat = 0
                count_cat = row + 1

        if group_by_options == 'group_by_contact_product':
            data_dict = {}
            for rec in stock_ledger_id:
                if rec.partner_id in data_dict:
                    if rec.product_id.name in data_dict[rec.partner_id]:
                        data_dict[rec.partner_id][rec.product_id.name].append(rec)
                    else:
                        data_dict[rec.partner_id][rec.product_id.name] = [rec]
                else:
                    data_dict[rec.partner_id] = {}
                    data_dict[rec.partner_id][rec.product_id.name] = [rec]
            sheet.write(row, col, 'Contact', header_style)
            sheet.write(row, col + 1, 'Product', header_style)
            if uom_options == 'product_unit_of_measure':
                sheet.write(row, col + 2, 'Unite of Measure', header_style)
            else:
                sheet.write(row, col + 2, 'Purchase UoM', header_style)
            sheet.write(row, col + 3, 'In. Qty', header_style)
            sheet.write(row, col + 4, 'Out. Qty', header_style)
            sheet.write(row, col + 5, 'In. Total Cost', header_style)
            sheet.write(row, col + 6, 'Out. Total Cost', header_style)

            count_cat = 0
            count_pro = 0
            in_total_cost_cat = 0
            in_qty_cat = 0
            out_total_cost_cat = 0
            out_qty_cat = 0
            in_total_cost_pro = 0
            in_qty_pro = 0
            out_total_cost_pro = 0
            out_qty_pro = 0
            for partner_id in data_dict:
                col = 0
                row += 1

                sheet.write(row, col, partner_id.name, pro_cat_style)

                for product_id in data_dict[partner_id]:
                    col = 1
                    row += 1
                    count_pro = row
                    sheet.write(row, col, product_id, pro_style)

                    for stock in data_dict[partner_id][product_id]:
                        out_total_cost_pro += stock.out_total_line_cost
                        in_total_cost_pro += stock.in_total_line_cost

                        if uom_options == 'product_unit_of_measure':
                            out_qty_pro += stock.outward_stock
                            in_qty_pro += stock.inward_stock
                        else:
                            out_qty_pro += stock.uom_po_outward_stock
                            in_qty_pro += stock.uom_po_inward_stock

                    col = 1
                    if uom_options == 'product_unit_of_measure':
                        sheet.write(row, col + 1, stock.uom_id.name, pro_style)
                    else:
                        sheet.write(row, col + 1, stock.uom_po_id.name, pro_style)
                    sheet.write(count_pro, col + 2, round(in_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 3, round(out_qty_pro, 2), pro_style)
                    sheet.write(count_pro, col + 4, in_total_cost_pro, pro_style)
                    sheet.write(count_pro, col + 5, out_total_cost_pro, pro_style)

                    in_qty_cat += in_qty_pro
                    out_qty_cat += out_qty_pro
                    in_total_cost_cat += in_total_cost_pro
                    out_total_cost_cat += out_total_cost_pro

                    in_qty_pro = 0
                    out_qty_pro = 0
                    in_total_cost_pro = 0
                    out_total_cost_pro = 0

                col = 1
                if count_cat == 0:
                    count_cat = 1

                sheet.write(count_cat, col + 2, round(in_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 3, round(out_qty_cat, 2), pro_cat_style)
                sheet.write(count_cat, col + 4, in_total_cost_cat, pro_cat_style)
                sheet.write(count_cat, col + 5, out_total_cost_cat, pro_cat_style)
                in_qty_cat = 0
                out_qty_cat = 0
                in_total_cost_cat = 0
                out_total_cost_cat = 0
                count_cat = row + 1

        workbook.close()
        output.seek(0)
        generated_file = response.stream.write(output.read())
        output.close()
        return generated_file
