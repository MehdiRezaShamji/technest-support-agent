import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from tools.check_order_status import check_order_status, check_order_status_schema
from tools.check_refund_eligibility import (
    check_refund_eligibility,
    check_refund_eligibility_schema,
)
from tools.create_support_ticket import (
    create_support_ticket,
    create_support_ticket_schema,
)
from tools.escalate_to_human import escalate_to_human, escalate_to_human_schema

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
filename = "conversation.json"

system_prompt = """
You are a helpful customer support agent working at a company called TechNest. 
Your role is to help customers with their requests and queries.

Tone: Be concise and friendly, speaking as a real customer support agent would. 
Stay calm and polite even if the customer shows signs of distress or anger.

Never invent information regarding orders, refunds, tickets, or any customer 
or company data. Always check using the available tools: check_order_status, 
check_refund_eligibility.

If order information cannot be found, ask the customer for more details 
before trying again. If it still cannot be found after that, escalate to 
a human.

Escalate to a human if any of the following occur:
- A tool fails or repeatedly cannot find the requested information
- The customer shows frustration or anger
- The customer explicitly asks to speak with a human
"""


class Agent:

    def __init__(self):
        self.conversation = self.load_memory()
        if not (
            self.conversation
            and self.conversation[0]
            == {
                "role": "system",
                "content": system_prompt,
            }
        ):
            self.conversation.append({"role": "system", "content": system_prompt})

        self.tools = {}
        self.tool_schema = []
        self.last_error = None

        self.register_tool(
            "check_order_status", check_order_status, check_order_status_schema
        )
        self.register_tool(
            "check_refund_eligibility",
            check_refund_eligibility,
            check_refund_eligibility_schema,
        )

        self.register_tool(
            "create_support_ticket", create_support_ticket, create_support_ticket_schema
        )

        self.register_tool(
            "escalate_to_human", escalate_to_human, escalate_to_human_schema
        )

    def load_memory(self):
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                    return data
                except json.JSONDecodeError:
                    data = []
                    return data
        else:
            data = []
            return data

    def add_message(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def call_llm(self):
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + api_key},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": self.conversation,
                "tools": self.tool_schema,
            },
        )
        if response.status_code != 200:
            self.last_error = response.text
            return None
        else:
            parse = response.json()
            message = parse["choices"][0]["message"]
            self.conversation.append(message)
            return message

    def register_tool(self, name, function, schema):
        self.tools[name] = function
        self.tool_schema.append(schema)

    def run_tool(self, message):
        for item in message["tool_calls"]:
            name = item["function"]["name"]
            args = item["function"]["arguments"]
            parsed = json.loads(args)
            func = self.tools[name]
            result = func(**parsed)
            id = item["id"]
            self.conversation.append(
                {"role": "tool", "tool_call_id": id, "content": result}
            )

    def save_memory(self):
        with open(filename, "w") as file:
            json.dump(self.conversation, file, indent=2)

    def loop(self):
        print("Type 'quit' to exit")
        print("Hello, How may i help you.")
        while True:
            query = input("You: ")
            if query == "quit".lower():
                print("Goodbye!")
                break
            else:
                self.add_message("user", query)
                while True:
                    max_tries = 2
                    for i in range(max_tries):
                        call_llm_result = self.call_llm()
                        if call_llm_result is not None:
                            break
                    else:
                        if not os.path.exists("errors.log"):
                            with open("errors.log", "w") as file:
                                json.dump({}, file)
                        with open("errors.log", "r") as file:
                            data = json.load(file)
                            now = datetime.now()
                            timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
                            data[timestamp_str] = {"reason": self.last_error}
                        with open("errors.log", "w") as file:
                            json.dump(data, file)
                            print("Sorry, I'm having trouble processing that right now")
                            break

                    if call_llm_result.get("tool_calls"):
                        self.run_tool(call_llm_result)
                    else:
                        print(call_llm_result["content"])
                        self.save_memory()
                        break


my_agent = Agent()
my_agent.loop()
