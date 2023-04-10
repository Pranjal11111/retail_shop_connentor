from odoo import models,api,fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    retail_customer_id = fields.Char("Retail Shop Customer Id")