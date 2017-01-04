# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
 
from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging


class stock_move(osv.osv):

    _inherit = 'stock.move'

    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        vals = super(stock_move,self)._prepare_procurement_from_move(cr, uid, move, context=context)
        name = move.name
        vals.update({'name': name})
        
        return vals
        # origin = (move.group_id and (move.group_id.name + ":") or "") + (move.rule_id and move.rule_id.name or move.origin or move.picking_id.name or "/")
        # group_id = move.group_id and move.group_id.id or False
        # if move.rule_id:
            # if move.rule_id.group_propagation_option == 'fixed' and move.rule_id.group_id:
                # group_id = move.rule_id.group_id.id
            # elif move.rule_id.group_propagation_option == 'none':
                # group_id = False
        # return {
            # 'name': move.rule_id and move.rule_id.name or "/",
            # 'origin': origin,
            # 'company_id': move.company_id and move.company_id.id or False,
            # 'date_planned': move.date,
            # 'product_id': move.product_id.id,
            # 'product_qty': move.product_uom_qty,
            # 'product_uom': move.product_uom.id,
            # 'product_uos_qty': (move.product_uos and move.product_uos_qty) or move.product_uom_qty,
            # 'product_uos': (move.product_uos and move.product_uos.id) or move.product_uom.id,
            # 'location_id': move.location_id.id,
            # 'move_dest_id': move.id,
            # 'group_id': group_id,
            # 'route_ids': [(4, x.id) for x in move.route_ids],
            # 'warehouse_id': move.warehouse_id.id or (move.picking_type_id and move.picking_type_id.warehouse_id.id or False),
            # 'priority': move.priority,
        # }