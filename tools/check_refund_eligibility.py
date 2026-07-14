import json
from datetime import datetime


def check_refund_eligibility(order_id):
    with open("orders.json", "r") as file:
        data = json.load(file)
        if order_id in data:
            order = data[order_id]
            order_status = order["status"]
            if order_status != "Delivered":
                return "Order has yet to be delivered, You can cancel the order."
            else:
                delivery_date_string = order["delivery_date"]
                delivery_date = datetime.strptime(delivery_date_string, "%Y-%m-%d")

                today = datetime.now()

                days_passed = (today - delivery_date).days
                if days_passed < 30:
                    return f"{days_passed} has been passed"
                else:
                    return "You can not try for refund, it's been more than 30 days"
        else:
            return f"Couldn't find the data for {order_id}"


check_refund_eligibility_schema = {
    "type": "function",
    "function": {
        "name": "check_refund_eligibility",
        "description": "Use this function to check the eligibility for refund.",
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
