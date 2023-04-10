from asyncio.log import logger
from email.policy import default
from odoo.tools import float_compare
from select import select
# import imp
from odoo import fields, models,api
import logging
_logger = logging.getLogger(__name__)

class RetailOrder(models.Model):
    _name = 'retail.shop.orders'
    _description = 'Retail Shop Orders Managment'


    name = fields.Char("Item Title")
    retail_order_id = fields.Char("reference")
    ship_name = fields.Char("ship to name")
    first_name = fields.Char("First Name")
    last_name = fields.Char("Last Name")
    address_one = fields.Char("address one")
    address_two = fields.Char("address two")
    address_three = fields.Char("address three")
    postcode = fields.Char("postcode")
    town = fields.Char("town")
    quantity = fields.Char("Item Quantity")
    line_net_price = fields.Char("line net price")
    phone = fields.Char('Phone Number')
    line_id = fields.Char('Line ID')
    order_id = fields.Many2one('sale.order',"Sale Order")
    sku = fields.Char('SKU')
    delivery_country = fields.Char("country")
    warehouse = fields.Char('Warehouse Code')
    date_placed = fields.Char("date placed")
    shipping_net_price = fields.Char("shipping net price")
    shipping_code = fields.Char("shipping code")
    duty_paid = fields.Char("duty paid")
    email = fields.Char("email")
    insured_value = fields.Char("insured value")
    delivery_inst = fields.Char("delivery instructions")
    picking_inst = fields.Char("picking instructions")
    despatch_inst = fields.Char("despatch instructions")
    inv_before_dispatch = fields.Char("invoice before dispatch")
    hold = fields.Char("hold")
    booking_req = fields.Char("booking required")
    order_status = fields.Char("Order Status")
    company = fields.Char("company")
    title = fields.Char("title")
    vat = fields.Char("vat")
    xero_account = fields.Char("xero account number")
    gift_meesage = fields.Char("Gift Message")
    warehouse_id = fields.Many2one("stock.warehouse","Warehouse ID")
    shop_id = fields.Many2one("retail.shop.seller","Shop")

    @api.model_create_multi
    def create(self,vals):
        result = super(RetailOrder,self).create(vals)
        for res in result:
            res.warehouse_id = self.env.context.get('warehouse_id')
            res.shop_id = self.env.context.get('shop_id')
            res.line_id = res.id
            res.name = res.retail_order_id
        return result

    def map_sale_orders(self):
        total_count = 0
        new_added_so = new_added_line = 0
        sale_orders = self.env['sale.order'].search([]).ids
        for order in self:
            res = self.create_sale_order(order)
            if res:
                total_count +=1
                if res[0].id not in sale_orders:
                    new_added_so += 1
                order.order_id = res[0].id
                if len(res) > 2:
                    new_added_line += 1
                self.check_for_delivery_validation(res[0])

        return self.env['amazon.wizard'].sudo().show_wizard_message(new_added_so, new_added_line, total_count - (new_added_line + new_added_so))

    def check_for_delivery_validation(self, sale_order):
        if sale_order.mirakl_order_state in ["shipped" ,"closed", "received"]:
            if len(sale_order.picking_ids) > 0:

                for delivery in sale_order.picking_ids:
                    if delivery.products_availability == "Available":
                        delivery.action_assign()
                        for move in delivery.move_lines.filtered(lambda m: m.state not in ["done", "cancel"]):
                            rounding = move.product_id.uom_id.rounding
                            if (
                                float_compare(
                                    move.quantity_done,
                                    move.product_qty,
                                    precision_rounding=rounding,
                                )
                                == -1
                            ):
                                for move_line in move.move_line_ids:
                                    move_line.qty_done = move_line.product_uom_qty
                        delivery.with_context(skip_immediate=True, skip_sms=True).button_validate()

    def create_sale_order(self,order):
        new_added_so = new_added_line = existing_line_update = 0
        sale_order = self.env['sale.order'].search([('retail_order_id', '=', order.retail_order_id)], limit=1) or False
        product = self.env['product.product'].search([('name','=',order.sku)])
        if not sale_order and product:
            customer_id = self._create_customer(order)
            billing_id = self._create_billing_customer(order, customer_id)
            shipping_id = self._create_shipping_customer(order, customer_id)
            mirakl_state = None
            if order.order_status:
                if order.order_status == 'despatched':
                    mirakl_state = 'shipped'
                if order.order_status == 'awaiting_collection':
                    mirakl_state = 'to_collect'
                if order.order_status == 'Cancelled':
                    mirakl_state = 'canceled'
                if order.order_status == 'Pending Ship Confirmation':
                    mirakl_state = 'waiting_acceptance'
                if order.order_status == 'Returned':
                    mirakl_state = 'received'
                else:
                    mirakl_state = 'closed'
            if customer_id:
                sale_order = self.env['sale.order'].sudo().create({
                        'partner_id': customer_id,
                        'partner_invoice_id': billing_id,
                        'partner_shipping_id': shipping_id ,
                        'retail_order_id': order.retail_order_id,
                        'mirakl_order_state': 'shipped',
                        'retail_first_name': order.first_name,
                        'state': 'sale',
                        'retail_last_name': order.last_name,
                        'type_id': self.env['sale.order.type'].search([('id','=', 1)]).id,
                        'market_place_shop': self.shop_id.name,
                        'retail_address_one': order.address_one,
                        'retail_address_two': order.address_two,
                        'warehouse_id': order.warehouse_id.id,
                        'order_status': order.order_status,
                        'retail_address_three': order.address_three,
                        'retail_postcode': order.postcode,
                        'retail_town': order.town,
                        'retail_quantity': order.quantity,
                        'retail_line_net_price': order.line_net_price,
                        'retail_phone': order.phone,
                        'retail_line_id': order.line_id,
                        # 'retail_phone': order.phone,
                        'retail_sku': order.sku,
                        'date_order': order.date_placed,
                        'retail_delivery_country': order.delivery_country,
                        'retail_warehouse': order.warehouse,
                        'retail_date_placed': order.date_placed,
                        'retail_shipping_net_price': order.shipping_net_price,
                        'retail_shipping_code': order.shipping_code,
                        # 'retail_gift_meesage': order.gift_meesage,
                        'retail_duty_paid': order.duty_paid,
                        'retail_email': order.email,
                        'retail_insured_value': order.insured_value,
                        'retail_picking_inst': order.picking_inst,
                        'retail_despatch_inst': order.despatch_inst,
                        'retail_inv_before_dispatch': order.inv_before_dispatch,
                        'retail_hold': order.hold,
                        'retail_booking_req': order.booking_req,
                        'retail_company': order.company,
                        'retail_title': order.title,
                        'retail_vat': order.vat,
                        'retail_xero_account': order.xero_account,
                        'retail_gift_meesage': order.gift_meesage,
                    })
                new_added_so += 1
                order_line = self.get_sale_order_lines(sale_order,order)
                print('==============retail==============order_line  %r',order_line)
                logger.info("Order Created with ID "+ sale_order.name + " and Line added with ID "+ str(order_line.id))
                return (sale_order)
              
        
        elif sale_order and order.line_id not in  sale_order.order_line.ids:
            product = self.env['product.product'].search([('name','=',order.sku)])
            ex_product_ids = [line.product_id.id for line in sale_order.order_line]
            if product and product.id not in ex_product_ids:
                line = self.env['sale.order.line'].create({
                    'product_id': self.env['product.product'].search([('name','=',order.sku)]).id,
                                'description': product.name,
                                'name': product.name,
                                'order_id': sale_order.id,
                                'product_uom_qty': order.quantity,
                                'price_unit': order.line_net_price,

                })
                logger.info("***LIne added to exiting order " + sale_order.name + " with ID ****"+ str(line.id))
                new_added_line += 1
                return sale_order, new_added_line
            else:
                for line in sale_order.order_line:
                    if line.product_id == product:
                        line.update({'product_uom_qty': order.quantity,'price_unit': order.line_net_price})
                existing_line_update += 1
                sale_order.write({'date_order': order.date_placed})
                logger.info("****** Sale Order Already Exist WIth ID " + str(sale_order.id))

                return (sale_order)
        else:
            logger.info("****** Sale Order Already Exist WIth ID " + str(sale_order.id))
            customer_id = self._create_customer(order)
            sale_order.write({'date_order': order.date_placed})
            billing_id = self._create_billing_customer(order, customer_id)
            shipping_id = self._create_shipping_customer(order, customer_id)
            return (sale_order)

    def get_sale_order_lines(self,order,order1):
        product = self.env['product.product'].search([('name','=',order1.sku)])
        if product:
            line = self.env['sale.order.line'].create({
                                'product_id': product.id,
                                'name': product.name,
                                'order_id': order.id,
                                'product_uom' : product.uom_id.id,
                                'product_uom_qty': order1.quantity,
                                'price_unit': order1.line_net_price,
                                # 'price_subtotal': order1.total_price,
            })
            return line

    def _create_customer(self, order):
        customer_env = self.env['res.partner']
        customer = customer_env.search([('phone', '=', order.phone)],limit=1) or False
        if not customer:
            customer = customer_env.create({
                    'company_type': 'person',
                    'name': order.first_name + ' '+ order.last_name,
                    'phone': order.phone,
                    'street': order.address_one,
                    'zip': order.postcode,
                    'city': order.town,
                    'country_id': self.env['res.country'].search([('name','=', order.delivery_country)],limit=1).id,
            })
        else:
            customer.country_id = self.env['res.country'].search([('name','=',order.delivery_country)]).id
            customer.zip = order.postcode
            customer.city = order.town
            customer.phone = order.phone
        return customer.id

    def _create_billing_customer(self,order, customer_id):
        billing_customer = self.env['res.partner'].search([('type', '=', 'invoice'), ('parent_id', '=', customer_id)]) or False
        if not billing_customer:
            country = state = full_name = False
            billing_customer = self.env['res.partner'].create({
                'company_type': 'person',
                'type': 'invoice',
                'name': order.first_name + ' '+ order.last_name,
                'parent_id': customer_id,
                # 'street': order.delivery_address,
                # 'street2': billing_address['street_2'],
                # 'phone': billing_customer.get("Phone") if billing_customer.get("Phone") != "None" else False,
                'city': order.town,
                # 'state_id': state.id if state else False,
                'country_id': self.env['res.country'].search([('name', '=', order.delivery_country)]).id or False,
                'country_code': country.code if country else False,
                'zip': order.postcode,
            })
        return billing_customer.id



    def _create_shipping_customer(self, order, customer_id):
        billing_customer = self.env['res.partner'].search([('type', '=', 'invoice'), ('parent_id', '=', customer_id)]) or False
        if not billing_customer:
            country = state = full_name = False
            if order.first_name:
                full_name = order.first_name
                if order.last_name:
                    full_name += " "+ order.last_name
            else:
                if order.last_name:
                    full_name = order.first_name
            billing_customer = self.env['res.partner'].create({
                'company_type': 'person',
                'type': 'delivery',
                'name': full_name,
                'parent_id': customer_id,
                'street': order.address_one,
                # 'street2': billing_address['street_2'],
                # 'phone': billing_customer.get("Phone") if billing_customer.get("Phone") != "None" else False,
                'city': order.town,
                # 'state_id': state.id if state else False,
                'country_id': self.env['res.country'].search([('name', '=', order.delivery_country)]).id,
                'country_code': country.code if country else False,
                'zip': order.postcode,
            })
        return billing_customer.id




