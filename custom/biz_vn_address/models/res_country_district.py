# -*- coding: utf-8 -*-

from ast import literal_eval
from operator import itemgetter
import time
import requests
import threading
import json
from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _
GHN_TOKEN = '5cf85160-befa-11ec-8bf9-6e703843c1f8'
GHN_ENPOINT = 'https://online-gateway.ghn.vn/shiip/public-api'

        
class ResCountryDistrict(models.Model):
    _name = 'res.country.district'
    _description = 'District'
    
    code = fields.Char('District ID')
    name = fields.Char('District Name', index=True)
    state_id = fields.Many2one('res.country.state', 'Province', index=True)
    active = fields.Boolean(default=True)
    name_extension = fields.Char(string="Name Extension", index=True)
    ghn_id = fields.Char('Origin ID', index=True)
    
    _sql_constraints = [
        ('code_uniq', 'CHECK(1=1)', 'District ID must be unique!'),
    ]
    
    @api.constrains('code', 'state_id')
    def check_existing(self):
        check_ids = []
        for district in self:
            check_ids = self.sudo().search([('code', '=', district.code),('state_id', '=', district.state_id.id),('id', '!=', district.id)], limit=1)
            if check_ids:
                raise ValidationError(_('District Code must be unique!'))

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        
    #     return super(ResCountryDistrict, self)._search(domain=domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)

    def check_existing_ward_update(self, name, ghn_id,NameExtension):
        self = self.with_context(active_test=False)
        check_ids = self.env['res.country.wards'].search(['|', '|', 
            ('name','ilike',name),('name','in',NameExtension), 
            ('ghn_id','=',ghn_id), 
            ('district_id', '=', self.id)])

        if len(check_ids) > 1:
            check_id = check_ids.filtered(lambda x: x.name == name)
            if len(check_id) != 1:
                raise
        else:
            check_id = check_ids

        if len(check_id) != 1:
            raise

        return check_id

    #11730 / 482
    def _procure_ghn_all_ward_update(self):
        payload = """{"district_id": %s}"""%(self.ghn_id)
        url = GHN_ENPOINT + '/master-data/ward?district_id'
        response = requests.request("GET", url, data=payload, headers={'Content-Type': "application/json", 'token': GHN_TOKEN})
        value = json.loads(response.text)
        if value.get('code') == 200 and value.get('data'):
            for item in value.get('data'):
                ghn_id = item.get('WardCode')
                name = item.get('WardName').strip().replace("  ", " ")
                NameExtension = item.get('NameExtension',[]) or []
                #check ward
                ward_id = self.check_existing_ward_update(name, ghn_id, NameExtension)

                NameExtension = NameExtension and ','.join(NameExtension) or ""
                if not ward_id:
                    ward_id = self.env['res.country.wards'].create({
                        'ghn_id': ghn_id, 
                        'name': name, 
                        'code': 'ghn%s'%ghn_id,
                        'district_id': self.id, 
                        'state_id' : self.state_id.id,
                        'name_extension': NameExtension,
                        'active': True,
                    })
                else:
                    ward_id.write({
                        'ghn_id': ghn_id,
                        'name_extension': NameExtension,
                        'active': True, 
                    })
        return True