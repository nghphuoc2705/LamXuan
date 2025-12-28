from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    permit_no = fields.Char('QID No', groups="hr.group_hr_user", tracking=True)
    health_card_no = fields.Char('HMC No', groups="hr.group_hr_user", tracking=True)
    health_card_expiration_date = fields.Date('HMC Expiration Date', groups="hr.group_hr_user", tracking=True)
    work_permit_expiration_date = fields.Date('QID Expiration Date', groups="hr.group_hr_user", tracking=True)
    passport_expiration_date = fields.Date('Passport Expiration Date', groups="hr.group_hr_user", tracking=True)
    join_date = fields.Date('Join Date', groups="hr.group_hr_user", tracking=True)  # related='contract_id.start_date',
    current_sponsor = fields.Char('Current Sponsor', groups="hr.group_hr_user", tracking=True)
    # current_employer = fields.Char(string='Current Employer', groups="hr.group_hr_user", tracking=True)
    current_employer = fields.Selection([('0', 'Family',),
                                         ('1', 'Company'),('3', 'Other')
                                         #('Arsan','3'),('Saad','4'),
                                         #('','3'),('2', 'AlNarjis'),
                                         ],
                                        string='Sponsorship Type', groups="hr.group_hr_user", tracking=True)
