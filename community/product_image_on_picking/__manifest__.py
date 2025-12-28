# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': "Product Image On Picking",
	'version': "18.0.0.0",
	'category': "Warehouse",
    'license':'OPL-1',
	'summary': "Display product image on picking print product image on delivery order report print image on receipt product image print product image on picking product image in delivery order line print Product image on picking order",
	'description': """
						Display product image on picking(receipt/delivery) and print product image on delivery slip report. 
					""",
	'author': "BROWSEINFO",
	"website" : "https://www.browseinfo.com/demo-request?app=product_image_on_picking&version=18&edition=Community",
    'depends': ['base', 'sale_management', 'purchase','stock'],
	'data': [
			'report/delivery_slip_report.xml',
			'views/view_stock_picking.xml',
			],
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': False,
	"live_test_url":'https://www.browseinfo.com/demo-request?app=product_image_on_picking&version=18&edition=Community',
	"images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
