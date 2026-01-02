###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_return = fields.Boolean(
        string='Is return',
    )
    is_change = fields.Boolean(
        string='Is return change',
    )

    # def _action_confirm(self, merge=True, merge_into=False):
    #     for move in self:
    #         if not move.sale_line_id:
    #             continue
    #         sale_line = move.sale_line_id
    #         to_change = sale_line.qty_changed - sale_line.qty_change
    #         if not to_change:
    #             continue
    #         return_type = move.picking_type_id.return_picking_type_id
    #         if not return_type:
    #             continue
    #         new_move = self.copy({
    #             'is_return': False,
    #             'is_change': True,
    #             'product_uom_qty': move.sale_line_id.qty_change,
    #             'origin_returned_move_id': move.id,
    #             'picking_type_id': return_type.id,
    #             'location_id': return_type.default_location_src_id.id,
    #             'location_dest_id': self.location_id.id,
    #             'procure_method': 'make_to_stock',
    #             })
    #         self |= new_move
    #     return super()._action_confirm(merge, merge_into)

    # def _push_apply(self):
    #     """Override to prevent push rules from creating additional moves for return orders"""
    #     # Filter out return moves to prevent push rules
    #     return_moves = self.filtered(lambda m: m.is_return)
    #     non_return_moves = self - return_moves
        
    #     # Only apply push rules to non-return moves
    #     if return_moves:
    #         # For return moves, skip push rules to avoid creating outgoing pickings
    #         if non_return_moves:
    #             return super(StockMove, non_return_moves)._push_apply()
    #         return self.env['stock.move']
    #     return super()._push_apply()
