# -*- coding: utf-8 -*-
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_vendor_code = fields.Char(
        string='Mã nhà cung cấp',
        related='partner_id.vendor_code',
        readonly=True,
    )
