###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_return = fields.Boolean(
        related='order_id.is_return',
        string='Is Return',
    )
    
    qty_changed = fields.Float(compute='_compute_qty_to_invoice',digits='Product Unit of Measure',string='Changed', store=True)
    
    qty_change = fields.Float(
        digits='Product Unit of Measure',
        string='Change',  store=True
        )
    qty_changed_to_invoice = fields.Float(
        digits='Product Unit of Measure',
        compute='_compute_qty_to_invoice',
        string='Change to invoice',
        store=True
    )
    qty_changed_invoiced = fields.Float(
        digits='Product Unit of Measure',
        compute='_get_invoice_qty',
        string='Change invoiced'
    )
    qty_returned = fields.Float(
        digits='Product Unit of Measure',
        compute='_get_qty_returned',
        string='Returned', store=True, readonly=True
    )
    qty_returned_to_invoice = fields.Float(
        digits='Product Unit of Measure',
        compute='_get_invoice_qty',
        string='Returned to invoice'
    )
    
    qty_returned_invoiced = fields.Float(
        digits='Product Unit of Measure',
        compute='_get_qty_returned_invoiced',
        string='Invoiced', store=True, readonly=True
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        domain='[("usage", "=", "internal")]',
        string='Location', copy=False
    )
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        sale_return = self.filtered(lambda x: x.is_return)
        sale_return._compute_amount_return()
        return super(SaleOrderLine, self - sale_return)._compute_amount()

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'is_return')
    def _compute_amount_return(self):
        for line in self:
            # Use the same method as standard sale order line but with negative quantity
            total_discount = line.discount or 0.0
            qty = (line.product_uom_qty * -1) + line.qty_change
            
            # Prepare base line for taxes computation with modified quantity
            base_line = line.env['account.tax']._prepare_base_line_for_taxes_computation(
                line,
                tax_ids=line.tax_id,
                quantity=qty,
                partner_id=line.order_id.partner_id,
                currency_id=line.order_id.currency_id or line.order_id.company_id.currency_id,
                rate=line.order_id.currency_rate,
            )
            
            # Add tax details
            line.env['account.tax']._add_tax_details_in_base_line(base_line, line.company_id)
            
            # Get the computed amounts
            line.price_subtotal = base_line['tax_details']['raw_total_excluded_currency']
            line.price_total = base_line['tax_details']['raw_total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.picking_ids', 'is_return', 'qty_change')
    def _get_qty_returned(self):
        for line in self:
            if not line.is_return:
                return
            bom = self.env['mrp.bom']._bom_find(line.product_id, company_id=line.company_id.id)
            product_bom = bom.get(line.product_id)
            bom_id = False
            if product_bom:
                bom_id = product_bom
            if bom_id and bom_id.type == 'phantom':
                moves = line.move_ids.filtered(lambda m: m.picking_id and m.picking_id.state != 'cancel')
                bom_delivered = moves and all([move.state == 'done' for move in moves])
                if bom_delivered:
                    line.qty_returned = line.product_uom_qty
                else:
                    line.qty_returned = 0.0
            else:
                if line.product_id.type == 'service':
                    line.qty_returned = line.product_uom._compute_quantity(line.product_uom_qty, line.product_uom)
                else:
                    line.qty_returned = line.product_uom._compute_quantity(
                        sum([m.quantity for m in line.move_ids if m.is_return and m.state == 'done']), line.product_uom)


    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _get_qty_returned_invoiced(self):
        for line in self:
            if not line.is_return:
                return
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.move_id.state != 'cancel':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.qty_returned_invoiced = qty_invoiced

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.picking_ids', 'is_return', 'qty_change')
    def _compute_qty_to_invoice(self):
        super(SaleOrderLine,self)._compute_qty_to_invoice()
        for line in self:
            if line.is_return:
                bom = self.env['mrp.bom']._bom_find(line.product_id, company_id=line.company_id.id)
                product_bom = bom.get(line.product_id)
                bom_id = False
                if product_bom:
                    bom_id = product_bom
                if bom_id and bom_id.type == 'phantom':
                    moves = line.move_ids.filtered(lambda m: m.picking_id and m.picking_id.state != 'cancel')
                    bom_delivered = moves and all([move.state == 'done' for move in moves])
                    if bom_delivered:
                        qty_returned = line.product_uom_qty
                    else:
                        qty_returned = 0.0
                else:
                    qty_returned = sum([m.quantity for m in line.move_ids if m.is_return and m.state == 'done'])

                if line.product_id.invoice_policy == 'order':
                    qty_returned = line.product_uom._compute_quantity(line.product_uom_qty, line.product_uom)
                    qty_changed = line.product_uom._compute_quantity(line.product_uom_qty, line.product_uom)
                else:
                    qty_returned = qty_returned
                    qty_changed = qty_returned
                line.qty_changed = qty_changed
                line.update({
                    'qty_returned_to_invoice': max(qty_returned - line.qty_returned_invoiced, 0),
                    'qty_changed_to_invoice': max(qty_changed - line.qty_changed_invoiced, 0),
                    'qty_to_invoice': max(qty_returned - line.qty_returned_invoiced, 0),
                    'qty_changed' : qty_changed})


    @api.depends(
        'state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice',
        'qty_invoiced', 'qty_changed_invoiced', 'qty_returned_invoiced',
        'qty_change', 'qty_changed_to_invoice')
    def _compute_invoice_status(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')

        def compare(a, b):
            return float_compare(a, b, precision_digits=precision)

        def is_to_invoice(line):
            return not float_is_zero(
                line.qty_to_invoice + line.qty_changed_to_invoice,
                precision_digits=precision)

        def is_upselling(line):
            return (
                line.state == 'sale' and
                line.product_id.invoice_policy == 'order' and
                compare(line.qty_delivered, line.product_uom_qty) == 1)

        def is_invoiced(line):
            return (
                compare(line.qty_changed_invoiced, line.qty_change) >= 0 and
                compare(line.qty_returned_invoiced, line.product_uom_qty) >= 0)

        super()._compute_invoice_status()
        for line in self:
            if not line.order_id.is_return:
                continue
            if is_to_invoice(line):
                line.invoice_status = 'to invoice'
            elif is_upselling(line):
                line.invoice_status = 'upselling'
            elif is_invoiced(line):
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        def has_return(invoice_line):
            return any(
                [l for l in invoice_line.sale_line_ids if l.is_return])
        for res in self:
            res.qty_invoiced = 0.0
            res.qty_changed_invoiced = 0.0
            invoice_lines = [
                l for l in res.invoice_lines if l.move_id.state != 'cancel']
            for invoice_line in invoice_lines:
                qty = invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, res.product_uom)
                if invoice_line.move_id.move_type == 'out_invoice':
                    if has_return(invoice_line):
                        if qty < 0:
                            #pass
                            res.qty_changed_invoiced -= qty
                        else:
                            res.qty_changed_invoiced += qty
                    else:
                        res.qty_invoiced += qty
                elif invoice_line.move_id.move_type == 'out_refund':
                    if has_return(invoice_line):
                        if qty > 0:
                            #pass
                            res.qty_changed_invoiced += qty
                        else:
                            res.qty_changed_invoiced -= qty
                    else:
                        res.qty_invoiced -= qty

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        if self.is_return:
            res['quantity'] = self.qty_to_invoice * -1
        return res

    def _onchange_product_id_check_availability(self):
        if self.is_return:
            return {}
        return super()._onchange_product_id_check_availability()

    @api.onchange('order_id', 'product_id')
    def _onchange_location_id(self):
        for res in self:
            res.location_id = (
                res.order_id and
                res.order_id.warehouse_id.lot_stock_id.id or None)

    @api.onchange('qty_change')
    def _onchange_qty_change(self):
        for res in self:
            if res.qty_change < 0:
                res.qty_change = 0
            elif res.qty_change > res.product_uom_qty:
                res.qty_change = res.product_uom_qty
                raise UserError(
                    _('You can not change more units of returned, at most you '
                      'can return %s') % res.product_uom_qty)
