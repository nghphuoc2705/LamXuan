# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # Basic
    'name': "BizApps - Hidden Admin",
    'version': '18.0.1.0',
    'description': """
        Hide admin from user and partner lists.
    """,
    'author': "support@bizapps.vn",
    'website': "https://bizapps.vn/",
    'license': "LGPL-3", 
    'category': "Access",
    'data': [
        'security/security.xml'
    ],

    # Advanced
    'auto_install': True,
    'application': False, 
    'author': "support@bizapps.vn",
    'website': "https://bizapps.vn/",
    'license': "LGPL-3", 
    'category': "Access",
    'depends': ['base'],
    'data': [
        'security/security.xml'
    ],

    # Advanced
    'auto_install': True,
    'application': False, 
    'installable': True,
}
