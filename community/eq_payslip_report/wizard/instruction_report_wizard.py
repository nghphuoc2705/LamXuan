from odoo import models, fields, api

from odoo.exceptions import UserError


#ToDo: Make Salary Instruction Report generated from Wizard

class InstructionReportWizard(models.TransientModel):
    _name = 'instruction.report.wizard'
    _description = 'Instruction Report Wizard'

    employee_ids = fields.Many2many('hr.employee','Employees')
    description = fields.Text(string="Description", required=True)
    remarks = fields.Text(string="Remarks", required=True)

    def generate_report(self):
        datas = {
            'active_ids': self.env.context.get('active_ids', []),
            'form':self.read(['employee_id', 'start_date','group'])[0],
                }

        res = self.env.ref('eq_payslip_report.action_report_instruction').report_action(self, data=datas)
        return res
