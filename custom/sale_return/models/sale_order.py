###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_return = fields.Boolean(
        string='Is Return',
    )
    original_sale_order_id = fields.Many2one(
        'sale.order',
        string='Original Sale Order',
        readonly=True,
        copy=False,
        ondelete='restrict',
        help='The original sale order that this return order is based on',
    )
    return_order_ids = fields.One2many(
        'sale.order',
        'original_sale_order_id',
        string='Return Orders',
        readonly=True,
    )
    return_count = fields.Integer(
        string='Return Count',
        compute='_compute_return_count',
    )
    state_return = fields.Selection([
        ('draft', 'Draft Return'),
        ('sent', 'Sent Return'),
        ('sale', 'Sale Return'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')],
        string='Sale Return Status',
        compute='_compute_state_return',
    )

    @api.depends('picking_ids.date_done')
    def _compute_effective_date(self):
        super(SaleOrder,self.filtered(lambda x: not x.is_return))._compute_effective_date()
        for order in self.filtered(lambda x: x.is_return):
            pickings = order.picking_ids.filtered(lambda x: x.state == 'done')
            dates_list = [date for date in pickings.mapped('date_done') if date]
            order.effective_date = min(dates_list, default=False)

    @api.depends('return_order_ids')
    def _compute_return_count(self):
        for order in self:
            order.return_count = len(order.return_order_ids.filtered(lambda o: o.is_return))

    @api.depends('state')
    def _compute_state_return(self):
        for res in self:
            res.state_return = res.state

    def action_view_return_orders(self):
        """View return orders for this sale order"""
        self.ensure_one()
        return {
            'name': _('Return Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('original_sale_order_id', '=', self.id), ('is_return', '=', True)],
            'context': {'create': False, 'default_is_return': False},
        }

    def action_return_sale_order(self):
        """Create a return order from this sale order and load full information"""
        self.ensure_one()
        
        if self.is_return:
            raise UserError(_('This action is only available for regular sale orders.'))
        
        if self.state not in ('sale'):
            raise UserError(_('You can only create return orders from confirmed sale orders.'))
        
        # Create new return order
        return_order_vals = {
            'is_return': True,
            'original_sale_order_id': self.id,
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'pricelist_id': self.pricelist_id.id,
            'currency_id': self.currency_id.id,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id,
            'warehouse_id': self.warehouse_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'company_id': self.company_id.id,
            'client_order_ref': self.client_order_ref,
            'state': 'draft',
        }
        
        return_order = self.env['sale.order'].create(return_order_vals)
        
        # Copy order lines from original order
        order_line_vals = []
        for line in self.order_line.filtered(lambda l: not l.is_downpayment and l.display_type == False):
            line_vals = {
                'order_id': return_order.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'sequence': line.sequence,
            }
            # Copy location_id if exists (for return orders)
            if hasattr(line, 'location_id') and line.location_id:
                line_vals['location_id'] = line.location_id.id
            
            order_line_vals.append((0, 0, line_vals))
        
        if order_line_vals:
            return_order.write({'order_line': order_line_vals})
        
        # Open the return order form
        return {
            'name': _('Return Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': return_order.id,
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals):
        for v in vals:
            if v.get('is_return') and 'name' not in v:
                v['name'] = self.env['ir.sequence'].next_by_code('sale.return')
        return super(SaleOrder,self).create(vals)

    def action_invoice_create(self, grouped=False, final=False):
        def recompute_origin(invoice):
            sale_names = list(set(
                s.order_id.name
                for i in invoice.invoice_line_ids
                for s in i.sale_line_ids))
            invoice.origin = ', '.join(sale_names)

        invoice_ids = super().action_invoice_create(grouped, final)
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            if invoice.amount_total != 0:
                continue
            new_invoice = invoice.copy({
                'type': 'out_refund',
                'invoice_line_ids': False})
            for line in invoice.invoice_line_ids:
                if line.quantity > 0:
                    continue
                line.write({
                    'invoice_id': new_invoice.id,
                    'quantity': line.quantity * -1})
            for invoice in [new_invoice, invoice]:
                recompute_origin(invoice)
                invoice.compute_taxes()
            invoice_ids.append(new_invoice.id)
        return invoice_ids

    def _get_tax_amount_by_group(self):
        self.ensure_one()
        if not self.is_return:
            return {}
        res = {}
        for line in self.order_line:
            price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
            qty = (line.product_uom_qty * -1) + line.qty_change
            taxes = line.tax_id.compute_all(
                price_reduce, quantity=qty,
                product=line.product_id,
                partner=self.partner_shipping_id)['taxes']
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                for t in taxes:
                    tax_ids = tax.children_tax_ids.ids
                    if t['id'] == tax.id or t['id'] in tax_ids:
                        res[group]['amount'] += t['amount']
                        res[group]['base'] += t['base']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [
            (l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
        return res
    
    
    @api.depends('vat_type','picking_ids', 'picking_ids.state','client_order_ref', 'invoice_ids', 'vehicle_trip_ids', 'is_coordinator',
        'picking_ids.is_return', 'picking_ids.date_done', 'picking_ids.picking_type_id','picking_ids.picking_type_id.delivery_status', 'state','invoice_ids.state')
    def _get_state_order(self):
        res = super(SaleOrder,self)._get_state_order()
        for rec in self:
            state_order = rec.state_order
            if rec.is_return:
                if state_order != 'done':
                    invoice_draft_ids = rec.invoice_ids
                    invoiced_ids = rec.invoice_ids.filtered(lambda r: r.state not in ['draft', 'cancel'])
                    picking_done = rec.picking_ids.filtered(lambda r: r.state == 'done')
                    if not len(picking_done):
                        state_order = 'waiting_receipt'
                    elif len(picking_done) and not len(invoice_draft_ids): # chờ tạo hóa đơn
                        state_order = 'waiting_invoice' 
                    elif len(picking_done) and len(invoice_draft_ids) and not len(invoiced_ids): # chờ xác nhận công nợ
                        state_order = 'waiting_invoice_open' 
                    elif len(picking_done) and len(invoiced_ids):
                        state_order = 'done' 
                if rec.state_return in ('draft', 'sent'):
                    state_order = 'draft'
                if rec.state_return == 'cancel':
                    state_order = 'cancel'
                rec.state_order = state_order
        return res