# -*- coding: utf-8 -*-
{
    'name' : 'Partner Custom View',
    'version' : '18.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'Customize the partner view in the POS',
    'author': 'CoreFlow',
    'company': 'CoreFlow',
    'website': '',
    'description': """  """,
    'depends': ['base', 'contacts', 'account', 'sale', 'purchase','biz_vn_address'],
    'data': [
        'views/res_partner_view.xml',
        'views/partner_menus.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

