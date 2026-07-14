import os
import json
from datetime import datetime

filename = "escalations.json"


def escalate_to_human(reason):
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump({}, file)

    with open(filename, "r") as file:
        data = json.load(file)
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    data[timestamp_str] = {"reason": reason}
    with open(filename, "w") as file:
        json.dump(data, file)
    return "A human agent will contact you shortly"


escalate_to_human_schema = {
    "type": "function",
    "function": {
        "name": "escalate_to_human",
        "description": "Use this function to escalate to human.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "A brief explanation of why the customer is being escalated to a human agent, based on the conversation.",
                },
            },
            "required": ["reason"],
        },
    },
}
