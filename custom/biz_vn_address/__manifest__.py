# -*- coding: utf-8 -*-
{
    'name': 'Bizapps VN Address',
    'version' : '18.0.1.0',
    'category': 'General',
    'author': 'support@bizapps.vn',
    'website': "https://bizapps.vn/ung-dung",
    "license": "OPL-1",
    'description': """ 
        Address vietnam \n
        - Search Partner by phone or mobile number: help you to find a partner by phone or mobile number, work on partner without preconfiguration, Just install the module and enjoy it.
        - Change address information format according to Vietnamese structure
        - Adding an update feature for logistics partners such as ViettelPost, Grab,...
    """,
    'depends': ['base', 'contacts', 'l10n_vn'],
    'data': [
        'security/ir.model.access.csv',
        
        'data/res.country.state.csv',
        'data/res.country.district.csv',
        'data/res.country.wards.csv',

        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/update_address_view.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
