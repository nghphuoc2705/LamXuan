from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResCountry(models.Model):
    _inherit = 'res.country'

    def init(self):
        noupdate_ids = self.search([('name', '=', 'Vietnam')])
        for data in noupdate_ids:
            data.address_format = '%(street)s\n%(wards_name)s\n%(state_name)s\n%(country_name)s'

    @api.constrains('address_format')
    def _check_address_format(self):
        for record in self:
            if record.address_format:
                address_fields = self.env['res.partner']._formatting_address_fields() + ['state_code', 'state_name','wards_name', 'country_code', 'country_name', 'company_name']
                try:
                    record.address_format % {i: 1 for i in address_fields}
                except (ValueError, KeyError):
                    raise UserError(_('The layout contains an invalid format key'))

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    map_with_state_ids = fields.Many2many('res.country.state',
        'res_country_state_map_rel',
        'res_country_state_id',
        'map_with_state_id', string='Map With State', copy=False, compute_sudo=True)

    active = fields.Boolean('Active', default=True)

    def do_merge_state_nq60(self):
        records = self.env['res.country.state'].with_context(active_test=False).search([])
        for state in records.filtered(lambda x: x.map_with_state_ids):
            state.action_merge_state_nq60()

    def action_merge_state_nq60(self):
        if not self.map_with_state_ids:
            return

        partner_ids = self.env['res.partner'].with_context(active_test=False).search([('state_id', 'in', self.map_with_state_ids.ids)])
        for partner in partner_ids:
            partner.write({'state_id': self.id})

        self.map_with_state_ids.write({'active': False})
class ResCountryWards(models.Model):
    _inherit = 'res.country.wards'

    active = fields.Boolean('Active', default=True)
    map_with_wards_ids = fields.Many2many('res.country.wards',
        'res_country_wards_map_rel',
        'res_country_wards_id',
        'map_with_wards_id', string='Map With Wards', copy=False, compute_sudo=True)

    is_new = fields.Boolean('Is New Wards', default=False, copy=False)
    map_with_state_ids = fields.Many2many('res.country.state', related='state_id.map_with_state_ids', string='Map With State')

    def do_merge_wards_nq60(self):
        import_id = self.env.ref('vn_address_nq60.import_vn_address')
        import_id.action_import()
        import_id.action_load()

    def action_merge_wards(self):
        if not self.map_with_wards_ids or not self.is_new:
            return

        partner_ids = self.env['res.partner'].with_context(active_test=False).search([('wards_id', 'in', self.map_with_wards_ids.ids)])
        for partner in partner_ids:
            partner.write({'wards_id': self.id})

        self.map_with_wards_ids.write({'active': False})

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100) -> list[tuple[int, str]]:
        domain = args or []
        domain += [('is_new', '=', True)]
        return super().name_search(name, domain, operator, limit)

class ResCountryDistrict(models.Model):
    _inherit = 'res.country.district'

    active = fields.Boolean('Active', default=False)