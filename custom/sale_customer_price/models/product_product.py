# -*- coding: utf-8 -*-

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_customer_price(self, partner_id, quantity=1.0, date=None, uom_id=None):
        """Get customer-specific price for this product."""
        if not partner_id:
            return False
        
        customer_info = self.env['product.customerinfo']._get_customer_price(
            partner_id=partner_id,
            product_id=self.id,
            quantity=quantity,
            date=date,
            uom_id=uom_id
        )
        
        if customer_info:
            # Return the price (UOM conversion will be handled in sale_order_line if needed)
            return customer_info.price
        
        return False

