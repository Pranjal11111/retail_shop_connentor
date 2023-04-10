{
    "name" : "Retail Shop Connector",
    "depends": ['sale','account','odoo_mirakl_integration','amazon_connector'],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/seller_views.xml",
        "views/retail_shop_orders_views.xml",
        "wizard/notification_wizard.xml",

    ],
    "application": True,
    "installable": True,
    'license': 'LGPL-3',
    

}
