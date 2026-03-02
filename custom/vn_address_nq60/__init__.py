from . import models
from odoo import SUPERUSER_ID, api

def do_merge_state(env):
    # env['res.country.state'].do_merge_state_nq60()
    env['res.country.wards'].do_merge_wards_nq60()