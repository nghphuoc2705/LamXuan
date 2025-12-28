from odoo import models, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    payment_method = fields.Selection([('cash','Cash'),
                                       ('card','ATM Card - Pay Card')], string='Payment Mode')
