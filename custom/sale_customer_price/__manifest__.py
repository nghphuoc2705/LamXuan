# -*- coding: utf-8 -*-
{
    'name': 'Sale Customer Price',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Customer-specific product prices for sales',
    'description': """
        This module allows you to set customer-specific prices for products, 
        similar to vendor prices in the purchase module.
        When selecting a product in a sales order, it will automatically use 
        the customer-specific price if available.
    """,
    'author': 'Custom Development',
    'depends': ['sale', 'product', 'account'],
    'data': [
        'security/product_security.xml',
        'security/ir.model.access.csv',
        'views/product_customerinfo_views.xml',
        'views/product_views.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

