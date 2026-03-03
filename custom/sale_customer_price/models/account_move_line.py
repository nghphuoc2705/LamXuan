# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    line_discount_pct = fields.Float(
        string='Chiết khấu %',
        digits='Discount',
        default=0.0,
        help='Chiết khấu bổ sung: price_subtotal trừ thêm (chiết khấu % × price_unit × qty)',
    )

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'line_discount_pct')
    def _compute_totals(self):
        return super()._compute_totals()
