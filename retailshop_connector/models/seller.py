from asyncio.log import logger
from dataclasses import field
import random
import string    

from odoo import fields,api, models,_
import requests
from odoo.exceptions import UserError, ValidationError
# import xmltodict
import datetime
import pprint
import logging
_logger = logging.getLogger(__name__)

class Seller(models.Model):
    _name = 'retail.shop.seller'
    _description = 'Retail Shops Managment'


    name = fields.Char("name")
    seller_id = fields.Char("Seller Id")
    seller_token = fields.Char("Seller Access Token",store=True)
    product_count = fields.Integer("")
    state = fields.Selection([
        ('draft','Draft'),
        ('done','Confirmed'),
        ('cancel','Cancelled'),
    ])
    api_login = fields.Char("Login ID")
    api_password = fields.Char("Password")
    test_token = fields.Char("",default="")
    warehouse_id = fields.Many2one("stock.warehouse","Warehouse ID",required=True)
    least_qty = fields.Integer("Least Quantity to make zero")
    # shop_id = fields.Many2one("stock.warehouse","Shop")
    

    def generate_token(self):
        if self.api_login:
            key = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 50))
            self.write({'seller_token': key})

    @api.onchange('seller_token')
    def onchange_token(self):
        if not self.seller_token:
            self.write({'seller_token': 0})

    def get_sale_order_lines(self, order_lines,sale_order):
        sale_order_lines = []
        if isinstance(order_lines['OrderLine'], list):
            for line in order_lines['OrderLine']:
                product_id =  self._create_product(line)
                if product_id and product_id > 0:
                    added_line = (0, 0, {
                            'product_id': product_id,
                            'commission_fee': line.get('commission_fee') if line.get('commission_fee') else False,
                            'description': line.get('Name') if line.get('Name') else False,
                            'offer_sku': line.get('offer_sku') if line.get('offer_sku') else False,
                            'offer_state_code': line.get('offer_state_code') if line.get('offer_state_code') else False,
                            'order_line_index': line.get('order_line_index') if line.get('order_line_index') else False,
                            'order_line_state_reason_code': line.get('order_line_state_reason_code') if line.get('order_line_state_reason_code') else False,
                            'order_line_state_reason_label': line.get('order_line_state_reason_label') if line.get('order_line_state_reason_label') else False,
                            'order_line_index': line.get('order_line_index') if line.get('order_line_index') else False,
                            'price_additional_info': line.get('price_additional_info') if line.get('price_additional_info') else False,
                            'shipping_price': line.get('shipping_price') if line.get('shipping_price') else False,
                            'shipping_price_additional_unit': line.get('shipping_price_additional_unit') if line.get('shipping_price_additional_unit') else False,
                            'shipping_price_unit': line.get('shipping_price_unit') if line.get('shipping_price_unit') else False,
                            'total_commission': line.get('total_commission') if line.get('total_commission') else False,
                        })

                    sale_order_lines.append(added_line)
            print(sale_order_lines)
            print(len(sale_order_lines))
        else:
            prod_id = self.env['product.product'].search([('name', '=', order_lines['OrderLine']['SellerProductId'])]).id
            line = order_lines['OrderLine']
            if prod_id > 0:
                added_line = (0, 0, {
                    'product_id': prod_id,
                            'commission_fee': line.get('commission_fee') if line.get('commission_fee') else False,
                            'description': line.get('Name') if line.get('Name') else False,
                            'offer_sku': line.get('offer_sku') if line.get('offer_sku') else False,
                            'offer_state_code': line.get('offer_state_code') if line.get('offer_state_code') else False,
                            'order_line_index': line.get('order_line_index') if line.get('order_line_index') else False,
                            'order_line_state_reason_code': line.get('order_line_state_reason_code') if line.get('order_line_state_reason_code') else False,
                            'order_line_state_reason_label': line.get('order_line_state_reason_label') if line.get('order_line_state_reason_label') else False,
                            'order_line_index': line.get('order_line_index') if line.get('order_line_index') else False,
                            'price_additional_info': line.get('price_additional_info') if line.get('price_additional_info') else False,
                            'shipping_price': line.get('shipping_price') if line.get('shipping_price') else False,
                            'shipping_price_additional_unit': line.get('shipping_price_additional_unit') if line.get('shipping_price_additional_unit') else False,
                            'shipping_price_unit': line.get('shipping_price_unit') if line.get('shipping_price_unit') else False,
                            'total_commission': line.get('total_commission') if line.get('total_commission') else False,
                        })
                sale_order_lines.append(added_line)
        return sale_order_lines

    def _create_product(self, line):
        product_env = self.env['product.product']

        prod = product_env.search([('name', '=', line.get('SellerProductId'))])
        return prod.id

    def _create_billing_customer(self, billing_address, customer_id):
        billing_customer = self.env['res.partner'].search([('type', '=', 'invoice'), ('parent_id', '=', customer_id)])
        if not billing_customer:
            country = state = full_name = False
            if billing_address['Country'] == "Espagne":
                country = self.env['res.country'].search([('name', '=', 'Spain')])
            else:
                country = self.env['res.country'].search([('code', '=', billing_address['Country'])])
            # if billing_address['state'] != "None":
            #     state = self.env['res.country.state'].search([('name', '=', billing_address['state']), ('country_id', '=', country.id)])
            if billing_address.get('FirstName'):
                full_name = billing_address.get('FirstName')
                if billing_address.get('LastName'):
                    full_name += " "+ billing_address.get('LastName')
            else:
                if billing_address.get('LastName'):
                    full_name = billing_address.get('LastName')
            billing_customer = self.env['res.partner'].create({
                'company_type': 'person',
                'type': 'invoice',
                'name': full_name,
                'parent_id': customer_id,
                'street': billing_address['Street'],
                # 'street2': billing_address['street_2'],
                # 'phone': billing_customer.get("Phone") if billing_customer.get("Phone") != "None" else False,
                'city': billing_address.get("City") if billing_address.get("City") != "None" else False,
                # 'state_id': state.id if state else False,
                'country_id': country.id if country else False,
                'country_code': country.code if country else False,
                'zip': billing_address.get("ZipCode") if billing_address.get("ZipCode") != "None" else False,
            })
        return billing_customer.id



    def _create_shipping_customer(self, shipping_address, customer_id):
        shipping_customer = self.env['res.partner'].search([('type', '=', 'delivery'), ('phone', '=', shipping_address.get("phone"))],limit=1)
        if not shipping_customer:
            country = state = full_name = False
            if shipping_address['country'] == "Espagne":
                country = self.env['res.country'].search([('name', '=', 'Spain')])
            else:
                country = self.env['res.country'].search([('name', '=', shipping_address['Country'])])
            # if shipping_address['state'] != "None":
            #     state = self.env['res.country.state'].search([('name', '=', shipping_address['state']), ('country_id', '=', country.id)])
            if shipping_address.get('FirstName'):
                full_name = shipping_address.get('FirstName')
                if shipping_address.get('LastName'):
                    full_name += " "+ shipping_address.get('LastName')
            else:
                if shipping_address.get('LastName'):
                    full_name = shipping_address.get('LastName')
            
            shipping_customer = self.env['res.partner'].create({
                'company_type': 'person',
                'type': 'delivery',
                'name': full_name,
                'parent_id': customer_id,
                'street': shipping_address['Street'],
                # 'street2': shipping_address['street_2'],
                # 'phone': shipping_address.get("phone"),
                'city': shipping_address['City'],
                # 'state_id': state.id if state else False,
                'country_id': country.id if country else False,
                'country_code': country.code if country else False,
                'zip': shipping_address['ZipCode'],
            })
        return shipping_customer.id

    def _create_customer(self, order):
        customer_data = order.get('Customer')
        if customer_data:
            customer_env = self.env['res.partner']
            customer = customer_env.search([('cdiscount_customer_id', '=', customer_data.get("CustomerId"))])
            if not customer:
                customer = customer_env.create({
                    'company_type': 'person',
                    'name': customer_data.get('FirstName') + ' ' + customer_data.get('LastName'),
                    'phone': customer_data.get("MobilePhone"),
                    'email': customer_data.get('Email'),
                    'cdiscount_customer_id': customer_data.get("CustomerId"),
                    # 'mirakl_locale': customer_data.get("locale"),
                })
            return customer.id
        return False

    
    # def action_view_cdiscount_sale_order(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _("%s's Retail Shop Orders", self.name),
    #         'view_mode': 'list,form',
    #         'res_model': 'retail.shop.orders',
    #         'context': {
    #             'search_default_group_status': 1,
    #             'warehouse_id': self.warhouse_id.id,
    #             'shop_id': self.id
    #         },
    #     }

    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sales Orders Generated from %s Retail Shop", self.name),
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'context': {
                'search_default_groub_by_date': 1,
            },
            'domain': [('retail_order_id', '!=', False)],
        }


    def action_view_retailshop_sale_order(self):
        # raise UserError(_("Sale Order Showed Successfully"))
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("%s's Orders", self.name),
            'view_mode': 'list,form',
            # 'view_ids': [(self.env.ref('odoo_mirakl_integration.view_mirakl_sales_order_tree').id, 'list'), (self.env.ref('odoo_mirakl_integration.view_sales_order_form').id, 'form')],
            'res_model': 'retail.shop.orders',
            'context': {
                'search_default_group_status': 1,
                'search_default_today': 1,
                'warehouse_id': self.warehouse_id.id,
                'shop_id': self.id
            },
            'domain': [('shop_id', '=', self.id)],
        }

    def action_view_sale_orders(self):
        # raise UserError(_("Sale Order Showed Successfully"))
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sales Orders Generated from Amazon"),
            'view_mode': 'list,form',
            # 'view_ids': [(self.env.ref('odoo_mirakl_integration.view_mirakl_sales_order_tree').id, 'list'), (self.env.ref('odoo_mirakl_integration.view_sales_order_form').id, 'form')],
            'res_model': 'sale.order',
            'context': {
                'search_default_groub_by_date': 1,
            },
            'domain': [('retail_order_id', '!=', False),('market_place_shop','=',self.name)],
        }
    def generate_fullfillment_center_data(self):
        sale_orders = self.env['sale.order'].search([ ('retail_order_id', '!=', False)])
        if not len(sale_orders):
            raise UserError(_("Please map sale orders First. There are none"))
        for order in sale_orders:
            marketplace = ""
            data = {}
            if len(order.retail_order_id) > 0 and not order.processed:
                order.processed = True

                # Marketplace Code Name
                marketplace = order.market_place_shop
                #add country extension of order
                if order.partner_id.country_id.code:
                    marketplace = marketplace + "_" + order.partner_shipping_id.country_id.code
                germen_warehouse = False
                if order.warehouse in ['EGRG','EGRH','EGTD']:
                    germen_warehouse = True
                # Basic Fileds
                data = {
                    "name": order.partner_id.name,
                    "mail_address": order.customer_notification_email,
                    "street": order.partner_id.street,
                    "street2": order.partner_id.street2,
                    "country": order.partner_id.country_id.name,
                    "postal_code": order.partner_id.zip,
                    "town": order.partner_id.city,
                    "phone": order.partner_id.phone,
                    # "picking_date": order.shipping_deadline.date(),
                    "order_id": order.amazon_order_id,
                    "comment": "",
                    "carrier": "",
                    "marketplace": marketplace,
                    "sale_order_id": order.id,
                    "stock_status": "check_available",
                    "order_processing_status": "unprocessed",
                    "process_date": datetime.datetime.now(),

                    # "market_place_shop": 'Amazon',
                }

                # Update Order Line Details and Carrier Update
                if len(order.order_line) > 0:
                    count = 1
                    for line in order.order_line:
                        data.update({
                            "item_id": line.product_id.default_code,
                            "quantity": int(line.product_uom_qty),
                            "weight": line.product_id.weight,
                            "product_id": line.product_id.id,
                            "inventory_stock_count": line.product_id.qty_available,
                        })

                        #Update ORder Name
                        if len(order.order_line) > 1:
                            data.update({
                                "order_id": order.retail_order_id + "-" + str(count),
                            })
                            count += 1
                        order_found = self.env['order.tracking.export'].search([('item_id','ilike', line.product_id.default_code),('order_id','ilike',order.retail_order_id)])
                        if not order_found:
                            ref = self.env['uk.order.tracking.export'].create_export_lines(data)
                            logger.info("Order Exported with ID ", ref.item_id )
                        else:
                            logger.info("Order already exported")

        return True

            
                
    
