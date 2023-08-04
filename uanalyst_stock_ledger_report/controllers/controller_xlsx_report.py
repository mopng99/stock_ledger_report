import re
from ast import literal_eval

from odoo import http
from odoo.http import content_disposition, request


class XLSXReportController(http.Controller):

    @http.route('/web/content/download/stock_ledger_report', type='http', csrf=False)
    def get_report_xlsx(self, **kw):
        from_date = kw.get('from_date')
        to_date = kw.get('to_date')
        location_id_report = literal_eval(kw.get('location_id'))
        uom_options = kw.get('uom_options')
        group_by_options = kw.get('group_by_options')
        filter_id = re.findall('\d+', (kw.get('filter_id')))

        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                     (
                         'Content-Disposition',
                         content_disposition('Stock Ledger Report' + '.xlsx'))
                     ]
        )
        request.env['report.excel.stock.ledger.wizard'].get_xlsx_report(
            response,
            from_date,
            to_date,
            location_id_report,
            uom_options,
            group_by_options,
            filter_id,
        )
        return response

