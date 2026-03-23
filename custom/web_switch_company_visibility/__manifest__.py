# -*- coding: utf-8 -*-
{
    "name": "Web Switch Company Visibility",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "summary": "Show company switcher only for allowed users",
    "author": "Custom Development",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "security/security.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_switch_company_visibility/static/src/js/switch_company_menu_patch.js",
            "web_switch_company_visibility/static/src/xml/switch_company_menu.xml",
        ],
    },
    "installable": True,
    "application": False,
}
