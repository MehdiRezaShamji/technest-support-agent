# TechNest Support Agent

A tool-calling AI customer support agent built from scratch in Python for a fictional electronics store.

The project demonstrates core AI agent concepts including **LLM tool calling, agentic loops, persistent session-based memory, dynamic tool registration, retry/error handling, REST API development with FastAPI, and modular software design** — without relying on agent frameworks such as LangChain or LangGraph.

## Live Demo

🌐 **Frontend:** https://technest-support-service.netlify.app/

## Features

* Multi-turn customer support conversations
* LLM-powered responses
* Tool/function calling
* Dynamic tool registration
* Order status lookup
* Refund eligibility checking
* Support ticket creation
* Human escalation
* Session-specific persistent conversation memory
* FastAPI REST API
* Session-based conversations
* Automatic retry for failed LLM requests
* Error logging for failed API calls
* Frontend ↔ backend integration
* CORS support for web frontend integration

## Architecture

```text
Customer
   │
   ▼
Frontend
   │
   ▼
FastAPI API
   │
   ▼
Agent
   │
   ▼
Groq LLM
   │
   ├── check_order_status
   ├── check_refund_eligibility
   ├── create_support_ticket
   └── escalate_to_human
```

## Project Structure

```text
TechNest-Support-Agent/
│
├── main.py
├── api.py
│
├── tools/
│   ├── check_order_status.py
│   ├── check_refund_eligibility.py
│   ├── create_support_ticket.py
│   └── escalate_to_human.py
│
├── orders.json
├── requirements.txt
├── README.md
└── .gitignore
```

## How It Works

The agent receives a customer's message and sends it to the LLM together with the available tool schemas.

If the LLM determines that external information or an action is required, it generates a tool call.

The agent then:

1. Detects the requested tool.
2. Parses the tool arguments.
3. Executes the corresponding Python function.
4. Sends the tool result back to the LLM.
5. Allows the LLM to generate the final response.

This creates an agentic loop:

```text
User Request
     ↓
    LLM
     ↓
Tool Required?
   ↙       ↘
 Yes        No
 ↓           ↓
Execute     Response
Tool
 ↓
Tool Result
 ↓
LLM
 ↓
Response
```

## Available Tools

### `check_order_status`

Checks the status and information associated with an order.

### `check_refund_eligibility`

Determines whether an order is eligible for a refund based on the available order information and refund rules.

### `create_support_ticket`

Creates a support ticket when an issue requires further assistance.

### `escalate_to_human`

Escalates the conversation to a human support representative when the issue cannot be appropriately handled by the AI agent.

## Key Design Decisions

### Tool Registry Pattern

Tools are dynamically registered through the `register_tool()` method instead of using hardcoded tool dispatch logic.

This makes it easier to add new capabilities without modifying the core agent loop.

### Session-Specific Persistent Memory

Each conversation session has its own conversation history.

The agent uses the session ID to create a dedicated memory file:

```text
conversation_<session_id>.json
```

This prevents different user sessions from sharing the same conversation history.

### Agentic Tool-Calling Loop

The agent can determine when a tool is required, execute the tool, process its result, and continue the conversation before returning a final response to the customer.

### Retry Logic

Failed LLM requests are automatically retried before the application reports an error.

### Error Logging

When an API request continues to fail after the available retry attempts, the error is recorded in `errors.log` with a timestamp.

### Modular Tool Design

Each tool is implemented as a separate Python module together with its corresponding tool schema.

## API

The project includes a FastAPI backend that exposes a `/chat` endpoint for communication with the frontend.

### Chat Endpoint

```text
POST /chat
```

Example request:

```json
{
  "query": "Where is my order?",
  "session_id": "optional-session-id"
}
```

Example response:

```json
{
  "session_id": "session-id",
  "reply": "Your order is currently...",
  "tool_used": "check_order_status"
}
```

### Health Check

```text
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

## Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd TechNest-Support-Agent
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

## Running the Agent

### CLI Version

```bash
python main.py
```

### FastAPI Backend

```bash
uvicorn api:app --reload
```

The FastAPI backend can then be connected to the frontend application.

## Tech Stack

* **Python**
* **FastAPI**
* **Pydantic**
* **Requests**
* **Groq API**
* **OpenAI-compatible tool/function calling**
* **python-dotenv**
* **JSON**
* **HTML / CSS / JavaScript** for the frontend

## Local Runtime Files

The following files are generated locally and excluded from Git through `.gitignore`:

* `conversation_*.json` — stores session-specific conversation memory
* `tickets.json` — stores created support tickets
* `escalations.json` — stores human escalation records
* `errors.log` — stores API errors
* `.env` — stores environment variables and API credentials
* `venv/` — local Python virtual environment
* `__pycache__/` — Python cache files

## Known Limitations

* Order data is stored in a mock JSON database for demonstration purposes.
* Conversation memory is currently file-based.
* No automated unit tests are included yet.
* Authentication and production-grade database storage have not yet been implemented.
* The project is intended as a demonstration and learning project rather than a production customer-support system.

## Future Improvements

* Implement order cancellation
* Replace JSON storage with SQLite or PostgreSQL
* Add automated unit and integration tests
* Add authentication and customer profiles
* Improve session and memory management
* Add semantic search over product documentation
* Introduce asynchronous tool execution
* Add monitoring and analytics
