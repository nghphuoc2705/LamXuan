# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class OfficeDashboard(http.Controller):

    @http.route('/office/dashboard', type='http', auth='user', website=True)
    def render_dashboard(self, **kwargs):
        return request.render('office_dashboard.dashboard_template', {})
