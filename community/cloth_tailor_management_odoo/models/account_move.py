# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_cloth_request_ids = fields.Many2many(
        'cloth.request.details',
        string="Cloth Requests"
    )
    deposit = fields.Float(
        compute='_compute_amount_cloth_tailor'
    )
    total = fields.Float(
        compute='_compute_amount_cloth_tailor'
    )
    reminder = fields.Float(
        compute='_compute_amount_cloth_tailor'
    )

    @api.depends('custom_cloth_request_ids')
    def _compute_amount_cloth_tailor(self):
        for rec in self:
            if rec.custom_cloth_request_ids:
                rec.deposit = sum(rec.custom_cloth_request_ids.mapped('deposit'))
                rec.total = sum(rec.custom_cloth_request_ids.mapped('total'))
                rec.reminder = sum(rec.custom_cloth_request_ids.mapped('reminder'))
            else:
                rec.deposit = 0.0
                rec.total = 0.0
                rec.reminder = 0.0
