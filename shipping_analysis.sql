SELECT AVG(order_delivered_customer_date::timestamp - order_purchase_timestamp::timestamp) AS average_shipping_time
FROM olist_orders_dataset
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;