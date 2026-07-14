import json


def check_order_status(order_id):
    with open("orders.json", "r") as file:
        data = json.load(file)
        if order_id in data:
            order = data[order_id]
            order_details = f"Name:{order['customer']}, Product:{order['product']}, status:{order['status']}, tracking_id:{order['tracking_id']}, estimated_delivery: {order['estimated_delivery']}, delivery_date:{order['delivery_date']}"
            return order_details
        else:
            return f"Couldn't find the data for {order_id}"


check_order_status_schema = {
    "type": "function",
    "function": {
        "name": "check_order_status",
        "description": "Use this function to check the order status.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Here's the order id",
                }
            },
            "required": ["order_id"],
        },
    },
}
