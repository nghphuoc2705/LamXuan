# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class Users(models.Model):
    _inherit = "res.users"

    def unlink(self):
        for res in self:
            if res.id == 2 or res.login in ['admin']:
                raise ValidationError(_('You cannot delete the administrative user of BizApps'))
        return super().unlink()


class Partner(models.Model):
    _inherit = "res.partner"

    def unlink(self):
        for res in self:
            if any([user.id == 2 or user.login in ['admin'] for user in res.user_ids]):
                raise ValidationError(_('You cannot delete the administrative user of BizApps'))
        return super().unlink()
