# LangChain 1.x E-Commerce Support Chatbot

A Python-based e-commerce support chatbot built with LangChain, Streamlit, and SQLite.

## Project Status

✅ **Completed Steps:**
1. ✅ Project initialization with `uv`
2. ✅ Dependencies installed (Streamlit, LangChain, ChromaDB, OAuth tools)
3. ✅ Basic Streamlit UI scaffold
4. ✅ Chat prompt template with LCEL chains
5. ✅ Project package structure (`src/langchain_bot/`)
6. ✅ SQLite database initialization with seed data
7. ✅ User authentication module (`auth.py`)
8. ✅ Multi-thread conversation management with UUIDs
9. ✅ Policy files for RAG (returns, shipping, FAQ)
10. ✅ RAG tool with ChromaDB vector search (`rag_tool.py`)
11. ✅ Single main LangChain agent with RAG capabilities (`agent.py`)
12. ✅ Streamlit app integrated with agent (`app.py`)

### What Works Now
- **Login System**: Email + password authentication for customers and admins
- **Multi-Thread Conversations**: Create and switch between chat threads with UUIDs
- **RAG Policy Search**: Agent can answer policy, shipping, and FAQ questions
- **Session State Management**: Conversation history stored in session
- **Database**: SQLite with seed data for users, orders, products, etc.

## Still To Implement (for full specification compliance)

### Step 11: Conversation Checkpointing
- Add `SqliteSaver` for persistent conversation state
- Load/save thread state instead of session-only storage
- Enable bot to remember conversations across server restarts

### Step 12: Logging Middleware
- Add LangChain callbacks for model and tool logging
- Log to `logs/app.log` with timestamps and user info
- Track tool usage and API calls

### Step 13: SQL Database Toolkit  
- Add `SQLDatabaseToolkit` for order queries
- Enable agent to answer order-specific questions
- Implement security rules to filter by user email

### Step 14: Gmail Integration
- Set up OAuth credentials (or MCP server)
- Send notification emails for returns/cancellations
- Log all emails to database

### Step 15: Human-in-the-Loop & Admin Dashboard
- Interrupt agent for approval-required actions (cancel/return)
- Create `app_admin.py` dashboard for admin review
- Store pending actions in database
- Resume paused agent threads

## Quick Start

### Prerequisites
- Python 3.13+
- OpenAI API key
- Windows PowerShell (or adjust shell commands)

### Setup

```bash
# The project is already initialized, but to replicate:

# 1. Install uv (if not already done)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Add uv to PATH (restart terminal after)
$env:Path = "C:\Users\localadmin\.local\bin;$env:Path"

# 3. Navigate to project
cd langchain-bot

# 4. Verify dependencies
uv run python -c "import streamlit, langchain; print('OK')"

# 5. Set your API key in .env
# Edit .env and replace sk-your-key-here with your actual key
```

### Running the Chatbot

```bash
$env:Path = "C:\Users\localadmin\.local\bin;$env:Path"
cd langchain-bot
uv run streamlit run app.py
```

The app starts on `http://localhost:8501`.

### Seeded Test Users

- **Customer 1**: `sivaprasad.valluru@gmail.com` / `siva@123`
- **Customer 2**: `bob@example.com` / `bob123`
- **Customer 3**: `charlie@example.com` / `charlie123`
- **Admin**: `admin@example.com` / `admin123`

## Project Structure

```
langchain-bot/
├── app.py                           # Main Streamlit app
├── ecommerce.db                     # SQLite business database
├── ecommerce_setup.sql              # SQL seed file
├── .env                             # API keys (gitignored)
├── .gitignore                       # Ignore secrets, DB files
├── pyproject.toml                   # Project manifest
│
├── policies/                        # RAG documents
│   ├── returns_policy.txt
│   ├── shipping_policy.txt
│   └── faq_returns_and_cancellations.txt
│
└── src/langchain_bot/               # Python package
    ├── __init__.py
    ├── agent.py                     # LangChain agent + tools
    ├── auth.py                      # User authentication
    ├── rag_tool.py                  # RAG policy search
    └── db_init.py                   # Database initialization
```

## Module Overview

### `app.py` (Streamlit Frontend)
- Login form and session management
- Multi-thread conversation sidebar
- Chat message rendering
- Agent invocation and result display

### `agent.py` (LangChain Agent)
- Single main agent with tools
- Currently includes: `search_policies` RAG tool
- Uses `CHAT_CONVERSATIONAL_REACT_DESCRIPTION` agent type
- Future: SQL toolkit, Gmail tools

### `auth.py` (Authentication)
- `authenticate_user(email, password, role)` - query SQLite users table
- Returns user record or None

### `rag_tool.py` (RAG System)
- `load_policy_documents()` - load `.txt` files from `policies/`
- `split_documents()` - chunk into ~800 token pieces
- `get_vector_store()` - initialize/load ChromaDB
- `search_policies` tool - semantic search over policy documents
- `initialize_vector_store()` - call on app startup

### `db_init.py` (Database Setup)
- `init_database()` - read SQL seed and create ecommerce.db
- Run once: `uv run python -m langchain_bot.db_init`

## Known Issues & Limitations

1. **No Checkpointer**: Conversations reset on page refresh (Streamlit session-only)
2. **No SQL Queries**: Agent can't answer order-specific questions yet
3. **No Email Sending**: Returns/cancellations don't send confirmations
4. **No HITL**: No admin approval workflow for sensitive actions
5. **No Logging**: Tool calls not logged to file

## Fixes & Next Steps

### To Enable Checkpointing (Step 11)
```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent

checkpointer = SqliteSaver(conn=...)
agent = create_react_agent(llm, tools, checkpointer=checkpointer)
```

### To Add SQL Tools (Step 13)
```python
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=database, llm=llm)
tools += toolkit.get_tools()
```

### To Add Gmail (Step 14)
```python
from langchain_google_community.gmail_toolkit import GmailToolkit

gmail_toolkit = GmailToolkit()
# Wrap send_email tool and add to agent
```

### To Add HITL (Step 15)
```python
from langgraph.prebuilt import create_react_agent
from langgraph.graph import START, StateGraph

# Use HumanInTheLoopMiddleware
# Store pending_actions in DB
# Resume with admin approval
```

## Environment Variables

**`.env` file (gitignored):**
```
OPENAI_API_KEY=sk-...
CHECKPOINTS_DB_PATH=checkpoints.sqlite
```

## Testing

### Syntax Check
```bash
uv run python -m py_compile app.py
uv run python -m py_compile src/langchain_bot/*.py
```

### Database
```bash
uv run python -c "import sqlite3; db = sqlite3.connect('ecommerce.db'); print(db.execute('SELECT COUNT(*) FROM users').fetchone())"
```

### RAG Tool (may have DLL issues on Windows; works fine in full app)
```bash
uv run python -c "from langchain_bot.rag_tool import search_policies; print('RAG tool loaded')"
```

## Architecture Notes

- **Agent-Centric Design**: Streamlit is a thin shell; all logic lives in the agent
- **Tool-Based Actions**: Chatbot decides which tools to call, no hard-coded flows
- **Persistent State**: Session state for conversations; will upgrade to checkpointer
- **Modular Tools**: RAG, SQL, Email—each as independent tool modules

## References

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [ChromaDB](https://www.trychroma.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)

## License

Educational project for capstone demonstration.

---

**Status**: Working prototype with RAG and authentication. Additional features (checkpointing, SQL, email, HITL) documented for future implementation.
