# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customer_ids = fields.One2many(
        'product.customerinfo', 'product_tmpl_id', 'Customers',
        depends_context=('company',))
    variant_customer_ids = fields.One2many(
        'product.customerinfo', 'product_tmpl_id')

