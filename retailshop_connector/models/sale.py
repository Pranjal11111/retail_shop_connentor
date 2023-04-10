from odoo import fields,api,models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    retail_order_id = fields.Char("reference")
    retail_ship_name = fields.Char("retail ship to name")
    retail_first_name = fields.Char("retail First Name")
    retail_last_name = fields.Char("retail Last Name")
    retail_address_one = fields.Char("address one")
    retail_address_two = fields.Char("address two")
    retail_address_three = fields.Char("address three")
    retail_postcode = fields.Char("postcode")
    retail_town = fields.Char("town")
    retail_quantity = fields.Char("retail Item Quantity")
    retail_line_net_price = fields.Char("line net price")
    retail_phone = fields.Char('retail Phone Number')
    retail_line_id = fields.Char('retail Line ID')
    order_id = fields.Many2one('sale.order',"Sale Order")
    retail_sku = fields.Char('retail SKU')
    retail_delivery_country = fields.Char("country")
    retail_warehouse = fields.Char('Retail Warehouse Code')
    retail_date_placed = fields.Char("date placed")
    retail_shipping_net_price = fields.Char("shipping net price")
    retail_shipping_code = fields.Char("shipping code")
    retail_duty_paid = fields.Char("duty paid")
    retail_email = fields.Char("retail email")
    retail_insured_value = fields.Char("insured value")
    retail_delivery_inst = fields.Char("delivery instructions")
    retail_picking_inst = fields.Char("picking instructions")
    retail_despatch_inst = fields.Char("despatch instructions")
    retail_inv_before_dispatch = fields.Char("invoice before dispatch")
    retail_hold = fields.Char("hold")
    retail_booking_req = fields.Char("booking required")
    retail_company = fields.Char("company")
    retail_title = fields.Char("title")
    retail_vat = fields.Char("vat")
    retail_xero_account = fields.Char("xero account number")
    retail_gift_meesage = fields.Char("retail Gift Message")
    retail_shop_id = fields.Many2one("retail.shop.seller","Retail Shop ID")

    
    def export_warehouse_orders(self):

        shipping_sale_orders = []
        for order in self:
            if order.mirakl_order_state and order.mirakl_order_state == "shipping" and order.retail_order_id:
                shipping_sale_orders.append(order)
        if len(shipping_sale_orders) > 0:
            # _logger.info("_________%r Order Processed to Warehouse Processing Management~~~~~~~~",len(shipping_sale_orders))
            shop_obj = self.env['retail.shop.seller']
            shop_obj.generate_fullfillment_center_data()
        return super(SaleOrder, self).export_warehouse_orders()
    
    # _sql_constraints = [
    #     ('date_order_conditional_required', "CHECK(1=1)", "A confirmed sales order requires a confirmation date."),
    # ]

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_id = fields.Char("Line Id")
