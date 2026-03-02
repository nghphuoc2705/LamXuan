from odoo import models, fields, api, _
import base64
import openpyxl
from io import BytesIO
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ImportWards(models.Model):
    _name = 'import.wards'
    _description = 'Import Wards'

    file_import = fields.Binary(string='File Import')
    file_name = fields.Char(string='File Name')    
    line_ids = fields.One2many('import.wards.line', 'import_wards_id', string='Lines')

    def read_xlsx_base64(self):
        try:
            xlsx_data = base64.b64decode(self.file_import)
            workbook = openpyxl.load_workbook(BytesIO(xlsx_data))
            sheet = workbook.active
            keys = [cell.value for cell in sheet[1]]
            data_by_rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_data = {key: value for key, value in zip(keys, row)}
                data_by_rows.append(row_data)
            return data_by_rows
        
        except Exception as e:
            raise UserError(_("Error reading XLSX file: %s") % str(e))

    def action_import(self):
        self.sudo().line_ids.unlink()
        datas = self.read_xlsx_base64()
        for data in datas:
            data['state_name'] = data.pop('state')
            data['import_wards_id'] = self.id
            self.env['import.wards.line'].create(data)

    def action_load(self):
        self = self.with_context(active_test=False)
        for line in self.line_ids.filtered(lambda l: not l.state_id):
            state_id = self.env['res.country.state'].search([('name', 'ilike', line.state_name)], limit=1)
            if not state_id:
                _logger.error("State %s not found", line.state_name) 
                continue

            line.write({'state_id': state_id.id})

        for line in self.line_ids.filtered(lambda l: not l.wards_id and l.state_id):
            ward_id = self.env['res.country.wards'].search([
                ('name', '=', line.name), 
                "|",
                ('state_id', '=', line.state_id.id),
                ('state_id','in',line.map_with_state_ids.ids)
            ], limit=1)
            
            if not ward_id:
                _logger.error("Ward %snot found", line.name) 
                continue

            line.write({'wards_id': ward_id.id})

        for line in self.line_ids.filtered(lambda l: not l.wards_id and l.state_id):
            line.create_wards()

        for line in self.line_ids.filtered(lambda l: l.wards_id and l.state_id):
            line.wards_id.write({
                'is_new': True,
                'state_id': line.state_id.id
            })

class ImportWardsLine(models.Model):
    _name = 'import.wards.line'
    _description = 'Import Wards Line'
    _order = 'stt'

    import_wards_id = fields.Many2one('import.wards', string='Import Wards', ondelete='cascade')
    stt = fields.Integer(string='STT')
    name = fields.Char(string='Name')
    state_name = fields.Char(string='State Name')

    state_id = fields.Many2one('res.country.state', string='State')
    wards_id = fields.Many2one('res.country.wards', string='Wards')    
    map_with_state_ids = fields.Many2many('res.country.state', related='state_id.map_with_state_ids', string='Map With State')

    def create_wards(self):
        self.ensure_one()
        if self.wards_id:
            return
        wards_id = self.env['res.country.wards'].create({
            'name': self.name,
            'state_id': self.state_id.id,
            'is_new': True
        })
        self.write({'wards_id': wards_id.id})