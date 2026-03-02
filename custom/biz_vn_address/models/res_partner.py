# -*- coding: utf-8 -*-

from ast import literal_eval
from operator import itemgetter
import time

from odoo import api, fields, models, _
from odoo.osv.expression import get_unaccent_wrapper
# ADDRESS_FIELDS_VN = ('street', 'street2', 'wards_name', 'district_name', 'city', 'zip', 'country_id')

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    city = fields.Char(string="City")
    def _default_country(self):
        country = self.env.ref('base.vn')
        return country and country.id or False
    
    def _get_full_address_vi(self):
        for partner in self:
            address = ''
            if partner.street:
                address += partner.street
            if partner.wards_id:
                address += len(address) > 0 and ', ' + partner.wards_id.name or partner.wards_id.name
            if partner.district_id:
                address += len(address) > 0 and ', ' + partner.district_id.name or partner.district_id.name
            if partner.state_id:
                address += len(address) > 0 and ', ' + partner.state_id.name or partner.state_id.name
            if partner.country_id:
                address += len(address) > 0 and ', ' + partner.country_id.name or partner.country_id.name
            partner.full_address_vi = address
            
    full_address_vi = fields.Char('Address', compute=_get_full_address_vi)
    country_id = fields.Many2one('res.country', tracking=True, string='Country', ondelete='restrict', default=_default_country)
    district_id = fields.Many2one('res.country.district', 'District')
    wards_id = fields.Many2one('res.country.wards', 'Wards')
    contact_type = fields.Selection([('customer', 'Customer'),('supplier', 'Supplier')])
    
    @api.model
    def _get_address_format(self):
        # return self.country_id.address_format or self._get_default_address_format()
        return "%(street)s\n%(country_name)s\n%(state_name)s %(state_code)s\n%(district_name)s\n%(wards_name)s"

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
            'district_name': self.district_id.name or '',
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

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            if self.parent_id.customer_rank > 0:
                self.contact_type = 'customer'
            else: self.contact_type = False
        else: self.contact_type = False
        return super(ResPartner, self).onchange_parent_id()
    
    def get_sql_address(self, query):
        from_string, from_params = query.from_clause
        where_string, where_params = query.where_clause
        return from_string, where_string, from_params + where_params
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = self.get_sql_address(where_query)
            from_str = from_clause if from_clause else 'res_partner'
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = self.env.registry.unaccent

            query = """SELECT res_partner.id
                             FROM {from_str}
                          {where} ({email} {operator} {percent}
                               OR {complete_name} {operator} {percent}
                               OR {phone} {operator} {percent}
                               OR {mobile} {operator} {percent}
                               OR {reference} {operator} {percent})
                               -- don't panic, trust postgres bitmap
                         ORDER BY {complete_name} {operator} {percent} desc,
                                  {complete_name}
                        """.format(from_str=from_str,
                                   where=where_str,
                                   operator=operator,
                                   email=unaccent('res_partner.email'),
                                   phone=unaccent('res_partner.phone'),
                                   mobile=unaccent('res_partner.mobile'),
                                   complete_name=unaccent('res_partner.complete_name'),
                                   reference=unaccent('res_partner.ref'),
                                   percent=unaccent('%s'))

            where_clause_params += [search_name] * 6
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = list(map(lambda x: x[0], self.env.cr.fetchall()))
            if partner_ids:
                return [(partner.id, partner.display_name) for partner in self.browse(partner_ids)]
                # return self.browse(partner_ids)._compute_display_name()
            else:
                return []
        return super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)
        
        