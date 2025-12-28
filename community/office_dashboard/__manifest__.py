# -*- coding: utf-8 -*-

{
    'name': 'Office Dashboard',
    'version': '1.0',
    'summary': 'Custom office dashboard for internal use',
    'category': 'Tools',
    'depends': ['web', 'website'],
    'data': [
        'views/dashboard_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'office_dashboard/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}