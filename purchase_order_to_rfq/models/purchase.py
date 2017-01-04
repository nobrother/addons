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

import pytz
from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare

import logging
import pprint

_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def action_view_purchase_requisition(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing Purchase requisition
        of given Purchase ids. 
        '''
        
        po_obj = self.pool.get('purchase.order').browse(cr, uid, ids[0], context=context)
        if po_obj.requisition_id:
            requisition_id = po_obj.requisition_id.id
        elif context and context.get('requisition_id'):
            requisition_id = context.get('requisition_id')
        else:
            return None;
            
        mod_obj = self.pool.get('ir.model.data') 
        act_obj = self.pool.get('ir.actions.act_window')        
        po_obj = self.pool.get('purchase.order').browse(cr, uid, ids[0], context=context)
        
        result = mod_obj.get_object_reference(cr, uid, 'purchase_requisition', 'action_purchase_requisition')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        
        res = mod_obj.get_object_reference(cr, uid, 'purchase_requisition', 'view_purchase_requisition_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = requisition_id or False
        
        return result
        
        
    def action_create_purchase_requisition(self, cr, uid, ids, context=None):
        '''
        Create Purchase requisition from Purchase Order
        - Copy the PO line into rfq line
        - Attach the PO to rfq
        '''
        
        po_obj = self.pool.get('purchase.order').browse(cr, uid, ids[0], context=context)
        
        # Cannot create purchase requisition if it exists
        if po_obj.requisition_id and po_obj.requisition_id.id:
            raise osv.except_osv(_('Invalid Action!'), _('Cannot create new Call for Bid for this purchase order because it is already created or attached to some Call for Bid already.'))
        
        line_ids = []
        for po_line in po_obj.order_line:
            line_ids += [(0, 0, {
                'product_id': po_line.product_id.id,
                'product_uom_id': po_line.product_uom.id,
                'product_qty': po_line.product_qty,
                'schedule_date': po_line.date_planned
            })]
        
        requisition_obj = self.pool.get('purchase.requisition')
        requisition_id = requisition_obj.create(cr, uid, {
            'origin': po_obj.name,
            'schedule_date': po_obj.minimum_planned_date,
            'warehouse_id': po_obj.picking_type_id.warehouse_id.id or False,
            'company_id': po_obj.company_id.id,
            'picking_type_id': po_obj.picking_type_id.id,
            'pricelist_id': po_obj.pricelist_id.id,
            'line_ids': line_ids,
            #'purchase_ids': [(4, po_obj.id)]
        }, context=context)
        
        _logger.info('\n============================\n' + pprint.pformat(requisition_id) + '\n============================\n')
        context.update({'requisition_id': requisition_id})
        
        # Confirm purchase requisition
        #requisition_obj.tender_in_progress(cr, uid, [requisition_id])
        
        # Display the purchase requisition
        return self.action_view_purchase_requisition(cr, uid, ids, context=context)
        