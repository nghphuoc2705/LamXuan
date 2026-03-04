# -*- coding: utf-8 -*-
from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def _prepare_product_base_line_for_taxes_computation(self, product_line):
    #     """Áp dụng line_discount_pct (chiết khấu %) khi tính thuế và price_subtotal."""
    #     result = super()._prepare_product_base_line_for_taxes_computation(product_line)
    #     pct = (getattr(product_line, 'line_discount_pct', 0) or 0.0) / 100.0
    #     if pct != 0.0 and self.is_invoice(include_receipts=True):
    #         result['price_unit'] = result['price_unit'] * (1.0 - pct)
    #     return result
