from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_name = fields.Char(string="Brand Name")