# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_discount_pct = fields.Float(
        string='Chiết khấu %',
        digits='Discount',
        default=0.0,
        help='Chiết khấu bổ sung: price_subtotal sẽ trừ thêm (chiết khấu % × price_unit × qty)',
    )

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """Giảm price_unit theo line_discount_pct để tax và price_subtotal tính đúng."""
        result = super()._prepare_base_line_for_taxes_computation(**kwargs)
        self.ensure_one()
        pct = (self.line_discount_pct or 0.0) / 100.0
        result['price_unit'] = result['price_unit'] * (1.0 - pct)
        return result

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'line_discount_pct')
    def _compute_amount(self):
        return super()._compute_amount()

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.display_type != 'line_section' and self.display_type != 'line_note':
            res['line_discount_pct'] = self.line_discount_pct
        return res

    def _get_pricelist_price(self):
        self.ensure_one()
        self.product_id.ensure_one()
        if not self.product_id or not self.order_id.partner_id:
            return super()._get_pricelist_price()
        
        order_date = self._get_order_date()
        date_val = order_date.date() if order_date else None
        
        customer_info = self.env['product.customerinfo']._get_customer_price(
            partner_id=self.order_id.partner_id.id,
            product_id=self.product_id.id,
            quantity=self.product_uom_qty or 1.0,
            date=date_val,
            uom_id=self.product_uom.id if self.product_uom else None
        )
        
        if customer_info:
            customer_price = customer_info.price
            
            if self.product_uom and customer_info.product_uom and self.product_uom != customer_info.product_uom:
                customer_price = customer_info.product_uom._compute_price(
                    customer_price, 
                    self.product_uom
                )
            
            if customer_info.currency_id != self.order_id.currency_id:
                if not date_val:
                    date_val = fields.Date.today()
                
                customer_price = customer_info.currency_id._convert(
                    customer_price,
                    self.order_id.currency_id,
                    self.order_id.company_id,
                    date_val
                )
            
            return customer_price
        
        return super()._get_pricelist_price()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        res = super().write(vals)
        if 'partner_id' in vals:
            for order in self:
                if order.order_line:
                    order.order_line.filtered(
                        lambda l: l.product_id and not l.display_type
                    )._compute_price_unit()
        return res