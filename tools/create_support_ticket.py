import json
import os

filename = "tickets.json"


def create_support_ticket(issue_summary, priority):
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump({}, file)

    with open(filename, "r") as file:
        data = json.load(file)
        current_no = len(data)
        add_current_no = current_no + 1
        ticket_no = f"{add_current_no:03}"
        ticket = f"TICKET-{ticket_no}"
    data[ticket] = {
        "issue_summary": issue_summary,
        "priority": priority,
        "status": "open",
    }
    with open(filename, "w") as file:
        json.dump(data, file)
        return ticket


create_support_ticket_schema = {
    "type": "function",
    "function": {
        "name": "create_support_ticket",
        "description": "Use this function to create a support ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_summary": {
                    "type": "string",
                    "description": "this should be a brief summary of the customer's problem, based on what they described in the conversation.",
                },
                "priority": {
                    "type": "string",
                    "description": "The urgency of the issue. Must be one of: low, medium, high.",
                },
            },
            "required": ["issue_summary", "priority"],
        },
    },
}
