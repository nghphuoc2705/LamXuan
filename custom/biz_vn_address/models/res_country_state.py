# -*- coding: utf-8 -*-

from ast import literal_eval
from operator import itemgetter
import time
import requests
import threading
import json

from odoo import api, fields, models, _

GHN_TOKEN = '5cf85160-befa-11ec-8bf9-6e703843c1f8'
GHN_ENPOINT = 'https://online-gateway.ghn.vn/shiip/public-api'

class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    
    name = fields.Char(string='State Name', required=True, index=True,
               help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')
    accents = fields.Char('Accents')
    active = fields.Boolean(default=True)
    district_ids = fields.One2many('res.country.district', 'state_id', 'District')
    name_extension = fields.Char(string="Name Extension", index=True)
    ghn_id = fields.Char('Origin ID', index=True)

    def check_existing_update(self, name, ghn_id, NameExtension):
        self = self.with_context(active_test=False)
        country_id = self.env.ref('base.vn')
        check_id = self.search(['|', 
            ('ghn_id','=',ghn_id),
            ('name','in',NameExtension),
            ('country_id', '=', country_id.id)
        ])

        return check_id

    def odoo_get_wards(self):
        self = self.with_context(active_test=False)
        district_ids = self.env['res.country.district'].search([('ghn_id','!=', False)])
        for district_id in district_ids:
            district_id._procure_ghn_all_ward_update()
            self.env.cr.commit()

    def odoo_get_district(self):
        self = self.with_context(active_test=False)
        state_ids = self.search([('ghn_id','!=', False)])
        for state_id in state_ids:
            state_id._procure_ghn_all_district_update()

    def _procure_ghn_province_update(self):
        payload = ""
        url = GHN_ENPOINT + '/master-data/province'
        response = requests.request("GET", url, data=payload, headers={'Content-Type': "application/json", 'Token': GHN_TOKEN })
        value = json.loads(response.text)
        if value.get('code') == 200 and value.get('data'):
            state_ids = []
            state_ghn_available = []
            for item in value.get('data'):
                ProvinceID = item.get('ProvinceID')
                ProvinceName = item.get('ProvinceName').strip().replace("  ", " ")
                NameExtension = item.get('NameExtension',[]) or []
                Code = item.get('Code')
                country_id = self.env.ref('base.vn').id
                state_id = self.env['res.country.state'].check_existing_update(ProvinceName, ProvinceID, NameExtension)
                state_ghn_available.append(str(ProvinceID))
                NameExtension = NameExtension and ','.join(NameExtension) or ""
                if not state_id:
                    state_id = self.env['res.country.state'].create({
                        'name': ProvinceName, 
                        'ghn_id': int(ProvinceID), 
                        'country_id': country_id,
                        'code': 'ghn%s'%Code,
                        'name_extension': NameExtension,
                        'active': True,
                    })
                else:
                    if state_id.ghn_id !=  int(ProvinceID):
                        state_id.write({
                            'ghn_id': int(ProvinceID),
                            'active': True,
                            'name_extension': NameExtension,
                        })
                state_ids.append(state_id)

        print("Lay xong")
        return True

    def check_existing_district_update(self, name, ghn_id, NameExtension):
        self = self.with_context(active_test=False)
        check_id = self.env['res.country.district'].search(['|','|', 
            ('name','ilike',name), ('name','in',NameExtension), 
            ('ghn_id', '=', ghn_id), 
            ('state_id', '=', self.id)
        ])

        if len(check_id) > 1:
            check_id = check_id.filtered(lambda x: x.name == name)

        if len(check_id) != 1:
            raise

        return check_id

    def _procure_ghn_all_district_update(self):
        district_value = []
        payload = """{"province_id": %s}"""%(self.ghn_id)
        url = GHN_ENPOINT + '/master-data/district'
        response = requests.request("GET", url, data=payload, headers={'Content-Type': "application/json", 'token': GHN_TOKEN})
        value = json.loads(response.text)
        if value.get('code') == 200 and value.get('data'):
            for item in value.get('data'):
                code = item.get('Code')
                DistrictName = item.get('DistrictName').strip().replace("  ", " ")
                DistrictID = item.get('DistrictID')
                NameExtension = item.get('NameExtension',[]) or []
                #check district
                district_id = self.check_existing_district_update(DistrictName, DistrictID, NameExtension)
                NameExtension = NameExtension and ','.join(NameExtension) or ""
                if not district_id:
                    district_id = self.env['res.country.district'].create({
                        'name': DistrictName,
                        'state_id': self.id,
                        'code': 'ghn%s'%code,
                        'ghn_id': DistrictID,
                        'name_extension': NameExtension,
                        'active': True,
                    })
                else:
                    if district_id.ghn_id != int(DistrictID):
                        district_id.write({
                            'ghn_id': DistrictID,
                            'name_extension': NameExtension,
                            'active': True,
                        })
        return True
    