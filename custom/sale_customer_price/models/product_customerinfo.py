# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CustomerInfo(models.Model):
    _name = "product.customerinfo"
    _description = "Customer Pricelist"
    _order = 'sequence, min_qty DESC, price, id'
    _rec_name = 'partner_id'

    def _default_product_id(self):
        product_id = self.env.get('default_product_id')
        if not product_id:
            model, active_id = [self.env.context.get(k) for k in ['model', 'active_id']]
            if model == 'product.product' and active_id:
                product_id = self.env[model].browse(active_id).exists()
        return product_id

    partner_id = fields.Many2one(
        'res.partner', 'Customer',
        ondelete='cascade', required=True,
        check_company=True,
        domain="[('customer_rank', '>', 0)]")
    product_name = fields.Char(
        'Customer Product Name',
        help="This customer's product name will be used when printing a quotation. Keep empty to use the internal one.")
    product_code = fields.Char(
        'Customer Product Code',
        help="This customer's product code will be used when printing a quotation. Keep empty to use the internal one.")
    sequence = fields.Integer(
        'Sequence', default=1, help="Assigns the priority to the list of product customer.")
    product_uom = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        related='product_tmpl_id.uom_id')
    min_qty = fields.Float(
        'Quantity', default=0.0, required=True, digits="Product Unit of Measure",
        help="The quantity to sell to this customer to benefit from the price, expressed in the product's default unit of measure.")
    price = fields.Float(
        'Price', default=0.0, digits='Product Price',
        required=True, help="The price to sell a product to this customer")
    price_discounted = fields.Float('Discounted Price', compute='_compute_price_discounted')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company.id, index=1)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    date_start = fields.Date('Start Date', help="Start date for this customer price")
    date_end = fields.Date('End Date', help="End date for this customer price")
    product_id = fields.Many2one(
        'product.product', 'Product Variant', check_company=True,
        domain="[('product_tmpl_id', '=', product_tmpl_id)] if product_tmpl_id else []",
        default=_default_product_id,
        help="If not set, the customer price will apply to all variants of this product.")
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', check_company=True,
        index=True, ondelete='cascade')
    product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
    discount = fields.Float(
        string="Discount (%)",
        digits='Discount',
        readonly=False)

    @api.depends('discount', 'price')
    def _compute_price_discounted(self):
        for rec in self:
            rec.price_discounted = rec.price * (1 - rec.discount / 100)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """Clear product variant if it no longer matches the product template."""
        if self.product_id and self.product_id not in self.product_tmpl_id.product_variant_ids:
            self.product_id = False

    def _sanitize_vals(self, vals):
        """Sanitize vals to sync product variant & template on read/write."""
        # add product's product_tmpl_id if none present in vals
        if vals.get('product_id') and not vals.get('product_tmpl_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._sanitize_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._sanitize_vals(vals)
        return super().write(vals)

    def _get_filtered_customer(self, company_id, product_id, date=None, params=False):
        """Filter customer info based on company, product, and date validity."""
        self.ensure_one()
        filtered = self.filtered(lambda s: (
            (not s.company_id or s.company_id.id == company_id.id) and
            (s.partner_id.active) and
            (not s.product_id or s.product_id == product_id)
        ))
        if date:
            filtered = filtered.filtered(lambda s: (
                (not s.date_start or s.date_start <= date) and
                (not s.date_end or s.date_end >= date)
            ))
        return filtered

    @api.model
    def _get_customer_price(self, partner_id, product_id, quantity=1.0, date=None, uom_id=None):
        """Get the customer price for a given partner and product."""
        if not partner_id or not product_id:
            return False
        
        company = self.env.company
        product = self.env['product.product'].browse(product_id) if isinstance(product_id, int) else product_id
        
        # Search for matching customer info
        customer_info = self.search([
            ('partner_id', '=', partner_id),
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            '|', ('product_id', '=', False), ('product_id', '=', product.id),
            '|', ('company_id', '=', False), ('company_id', '=', company.id),
        ], order='sequence, min_qty DESC')
        
        if not customer_info:
            return False
        
        # Filter by date if provided
        if date:
            customer_info = customer_info.filtered(lambda s: (
                (not s.date_start or s.date_start <= date) and
                (not s.date_end or s.date_end >= date)
            ))
        
        # Convert quantity to customer_info.product_uom (which is product.uom_id) for comparison
        # customer_info.product_uom is related to product_tmpl_id.uom_id
        if uom_id:
            uom = self.env['uom.uom'].browse(uom_id)
            # Convert quantity to product's UOM (which matches customer_info.product_uom)
            quantity_in_product_uom = uom._compute_quantity(quantity, product.uom_id)
        else:
            quantity_in_product_uom = quantity
        
        # Find the best matching customer info based on quantity
        for info in customer_info:
            # min_qty is in product_uom (which is product.uom_id)
            if quantity_in_product_uom >= info.min_qty:
                return info
        
        return False

