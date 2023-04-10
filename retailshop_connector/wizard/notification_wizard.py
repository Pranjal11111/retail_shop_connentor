 # -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import Warning

class Marketplace_Wizard(models.TransientModel):
    _name = "amazon.wizard"
    _description = "Amazon Wizard"

    # wizard_message = fields.Text(string="", readonly=True)
    new_added_so = fields.Integer("New Added Sale Order",default=0)
    new_added_line = fields.Integer("New Added Line",default=0)
    existing_updated_line = fields.Integer("Updated Orders",default=0)

    def show_wizard_message(self, new_added_so, new_added_line, existing_updated_line):
        message_id = self.create({'new_added_so': new_added_so,'new_added_line':new_added_line, 'existing_updated_line': existing_updated_line }).id
        # return {
        #     'name': 'Record Counts', 
        #     'res_model': 'amazon.wizard', 
        #     'res_id': message_id, 
        #     'type': 'ir.actions.act_window', 
        #     'view_mode': 'form',
        #     'view_id': 'amazon_wizard_form',
        #     'view_type': 'form',
        #     'domain': '[]',
        #     'target': 'new',
        #     'nodestroy': True
        # }
        return {
        'name': "Order Counts",
        'res_model': 'amazon.wizard',
        'view_mode': 'form',
        # 'view_id': self.env.ref("amazon_connector.amazon_wizard_form"),
        'view_type': 'form',
        'res_id': message_id,
        'type': 'ir.actions.act_window',
            # 'nodestroy': True,
        'target': 'new',
        # 'domain': '[if you need]',
        # 'context': {'if you need'}
    }