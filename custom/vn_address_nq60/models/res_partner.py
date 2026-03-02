from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_address_format(self):
        # return self.country_id.address_format or self._get_default_address_format()
        return "%(street)s\n%(country_name)s\n%(state_name)s %(state_code)s\n%(wards_name)s"

    # @api.model
    # def _formatting_address_fields(self):
    #     res = super(ResPartner, self)._formatting_address_fields()
    #     res += ['wards_id','']
    #     return res

    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format

        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'wards_name': self.wards_id.name or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        
        # custom address for other module
        address_format, args = self.custom_display_address(address_format, args)

        return address_format % args

    def custom_display_address(self, address_format, args):
        return address_format, args

    # @api.onchange('state_id')
    # def on_change_state_id(self):
    #     domain = {}
    #     if self.state_id:
    #         self.district_id = False
    #         self.wards_id = False
    #         domain['district_id'] = [('state_id', '=', self.state_id.id)]
    #         domain['wards_id'] = [('state_id', '=', self.state_id.id)]
    #     return {'domain': domain}
    
    # @api.onchange('district_id')
    # def on_change_district_id(self):
    #     return
    
    # @api.onchange('wards_id')
    # def on_change_wards_id(self):
    #     return
