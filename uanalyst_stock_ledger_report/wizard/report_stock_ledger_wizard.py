# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time
from calendar import monthrange
#
from odoo import fields, models, _


class ReportStockLedgerWizard(models.TransientModel):
    _name = 'report.stock.ledger.wizard'
    _description = 'Stock Ledger Report Wizard'

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

    def action_confirm(self):
        """location wise stock transaction report will be generated"""
        print(self.location_id)
        self.location_id.sudo().compute_transactions_report()
        uom_column_hide = False
        po_uom_column_hide = False
        if self.uom_options == 'product_unit_of_measure':
            uom_column_hide = False
            po_uom_column_hide = True
        else:
            uom_column_hide = True
            po_uom_column_hide = False
        return {'name': _('Stock Ledger Report'),
                'view_mode': 'tree',
                'res_model': 'stock.ledger.report',
                'view_id': self.env.ref('uanalyst_stock_ledger_report.view_report_stock_ledger_tree').id,
                'type': 'ir.actions.act_window',
                'domain': ['&', ('location_id_report', 'in', [self.location_id.id]),
                           '&', ('date', '>=', datetime.combine(self.from_date, time.min)),
                           ('date', '<=', datetime.combine(self.to_date, time.max)), ],
                'context': {'search_default_product': True,
                            'search_default_product_active': True,
                            'uom_column_hide': uom_column_hide,
                            'po_uom_column_hide': po_uom_column_hide}, }
