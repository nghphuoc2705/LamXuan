from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Char(string="Brand")