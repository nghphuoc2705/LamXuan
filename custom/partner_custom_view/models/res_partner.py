from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code_partner = fields.Char(string="Mã khách hàng")
    branch_code = fields.Char(string="Chi nhánh tạo")
    vendor_code = fields.Char(string="Mã nhà cung cấp")
    cccd = fields.Char(string="CCCD")
    user_create_id = fields.Many2one('res.users', string="Người tạo")
    type_partner = fields.Selection(
        selection=[
            ('customer', 'Khách hàng'),
            ('supplier', 'Nhà cung cấp'),
        ],
        string='Type Partner',
        help='Lưu lựa chọn Khách hàng hoặc Nhà cung cấp khi dùng trường Company Type.',
    )
    address_temp = fields.Char(string="Địa chỉ Giao Hàng")
    #khu vực
    region_id = fields.Char(string="Khu vực")

    # Nhóm Sale: nợ thu, tổng bán, tổng bán trừ trả hàng
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_partner_currency_id',
        string='Currency',
    )
    receivable_current = fields.Monetary(
        string='Nợ cần thu hiện tại',
        compute='_compute_receivable_current',
        currency_field='currency_id',
        help='Tổng nợ từ các hóa đơn bán chưa thanh toán (out_invoice posted, amount_residual).',
    )
    total_sale = fields.Monetary(
        string='Tổng bán',
        compute='_compute_total_sale',
        currency_field='currency_id',
        help='Tổng các đơn bán đã xác nhận (Sales Order state = sale) cho partner này.',
    )
    total_sale_net = fields.Monetary(
        string='Tổng bán trừ trả hàng',
        currency_field='currency_id',
        help='Tổng bán sau khi trừ trả hàng (chưa tính toán).',
    )

    # Nhóm Purchase: nợ trả, tổng mua, tổng mua trừ trả hàng
    payable_current = fields.Monetary(
        string='Nợ cần trả hiện tại',
        compute='_compute_payable_current',
        currency_field='currency_id',
        help='Tổng nợ từ các hóa đơn mua chưa thanh toán (in_invoice posted, amount_residual).',
    )
    total_purchase = fields.Monetary(
        string='Tổng mua',
        compute='_compute_total_purchase',
        currency_field='currency_id',
        help='Tổng các đơn mua đã xác nhận (Purchase Order state = purchase) cho partner này.',
    )
    total_purchase_net = fields.Monetary(
        string='Tổng mua trừ trả hàng',
        currency_field='currency_id',
        help='Tổng mua sau khi trừ trả hàng (chưa tính toán).',
    )

    category_type_partner_id = fields.Many2one('res.partner.category', string="Nhóm khách hàng")

    @api.depends('company_id')
    def _compute_partner_currency_id(self):
        company = self.env.company
        for partner in self:
            partner.currency_id = partner.company_id.currency_id or company.currency_id

    @api.depends_context('company')
    def _compute_receivable_current(self):
        AccountMove = self.env['account.move'].with_context(active_test=False)
        for partner in self:
            commercial = partner.commercial_partner_id
            moves = AccountMove.search([
                ('commercial_partner_id', '=', commercial.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ('not_paid', 'partial')),
                ('company_id', '=', self.env.company.id),
            ])
            partner.receivable_current = -sum(moves.mapped('amount_residual_signed'))

    @api.depends_context('company')
    def _compute_total_sale(self):
        SaleOrder = self.env['sale.order']
        for partner in self:
            commercial = partner.commercial_partner_id
            orders = SaleOrder.search([
                ('partner_id.commercial_partner_id', '=', commercial.id),
                ('state', '=', 'sale'),
                ('company_id', '=', self.env.company.id),
            ])
            # amount_total theo đơn vị đơn hàng, quy đổi về tiền công ty
            total = 0.0
            for order in orders:
                total += order.currency_id._convert(
                    order.amount_total,
                    self.env.company.currency_id,
                    self.env.company,
                    order.date_order.date() if order.date_order else fields.Date.context_today(self),
                )
            partner.total_sale = total

    @api.depends_context('company')
    def _compute_payable_current(self):
        AccountMove = self.env['account.move'].with_context(active_test=False)
        for partner in self:
            commercial = partner.commercial_partner_id
            moves = AccountMove.search([
                ('commercial_partner_id', '=', commercial.id),
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ('not_paid', 'partial')),
                ('company_id', '=', self.env.company.id),
            ])
            # amount_residual_signed: dương = ta nợ NCC (nợ cần trả)
            partner.payable_current = sum(moves.mapped('amount_residual_signed'))

    @api.depends_context('company')
    def _compute_total_purchase(self):
        PurchaseOrder = self.env['purchase.order']
        for partner in self:
            commercial = partner.commercial_partner_id
            orders = PurchaseOrder.search([
                ('partner_id.commercial_partner_id', '=', commercial.id),
                ('state', '=', 'purchase'),
                ('company_id', '=', self.env.company.id),
            ])
            total = 0.0
            for order in orders:
                total += order.currency_id._convert(
                    order.amount_total,
                    self.env.company.currency_id,
                    self.env.company,
                    order.date_order.date() if order.date_order else fields.Date.context_today(self),
                )
            partner.total_purchase = total

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        for partner in res:
            partner.write({
                'user_create_id': self.env.user.id,
            })
        return res