# TechNest Support Agent

A tool-calling AI customer support agent built from scratch in Python for a fictional electronics store. This project demonstrates core AI agent concepts including tool calling, persistent memory, dynamic tool registration, retry/error handling, and modular software design—without relying on agent frameworks such as LangChain or LangGraph.

## Features

* Multi-turn customer support conversations
* Dynamic tool registration (Tool Registry Pattern)
* Order status lookup
* Refund eligibility checking
* Support ticket creation
* Human escalation
* Persistent conversation memory
* Automatic retry for failed LLM requests
* Error logging for failed API calls

## Architecture

```text
TechNest-Support-Agent/
│
├── main.py
├── tools/
│   ├── check_order_status.py
│   ├── check_refund_eligibility.py
│   ├── create_support_ticket.py
│   └── escalate_to_human.py
├── orders.json
├── requirements.txt
├── README.md
└── .gitignore
```

The agent dynamically registers tools at startup, allowing new capabilities to be added without modifying the core agent loop.

## Key Design Decisions

* **Tool Registry Pattern** — Tools are registered dynamically through `register_tool()` instead of hardcoded dispatch logic, making the agent easily extensible.
* **Persistent Memory** — Conversation history is stored in `conversation.json` and restored when the application starts.
* **Retry Logic** — Failed LLM requests are retried before reporting an error to the user.
* **Centralized Error Logging** — Failed API requests are logged to `errors.log` with timestamps after all retry attempts are exhausted.
* **Modular Tool Design** — Each tool is implemented in its own module with its corresponding JSON schema.

## Available Tools

* `check_order_status`
* `check_refund_eligibility`
* `create_support_ticket`
* `escalate_to_human`

## Known Limitations

* `check_refund_eligibility` may determine that an order can be cancelled, but a dedicated `cancel_order` tool has not yet been implemented.
* Order data is stored in a mock JSON database for demonstration purposes.
* No automated tests are included yet; functionality has been verified through manual testing.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Run the agent:

```bash
python main.py
```

Type `quit` to exit.

## Tech Stack

* Python
* Requests
* Groq API (`llama-3.3-70b-versatile`)
* OpenAI-compatible Function Calling
* JSON
* python-dotenv

## Future Improvements

* Implement order cancellation
* Replace the JSON database with SQLite or PostgreSQL
* Add automated unit tests
* Add authentication and customer profiles
* Build a web interface (FastAPI + React)
* Add semantic search over product documentation
* Introduce asynchronous tool execution for improved performance
