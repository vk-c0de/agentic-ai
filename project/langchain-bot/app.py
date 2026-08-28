import streamlit as st
from dotenv import load_dotenv
from uuid import uuid4
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_bot.auth import authenticate_user
from langchain_bot.agent import get_agent
from langchain_bot.rag_tool import initialize_vector_store


def get_llm():
    """Returns a ChatOpenAI LLM instance with fixed settings."""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def build_chain(llm):
    """Build a LCEL chain with system prompt, message history placeholder, and human input."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a concise, helpful e-commerce support assistant. Use prior chat history to stay in context."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    return prompt | llm


def init_session():
    """Initialize session state with required keys for authentication and conversations."""
    st.session_state.setdefault("user_email", None)
    st.session_state.setdefault("user_role", None)
    st.session_state.setdefault("conversation_id", None)
    st.session_state.setdefault("conversations", {})  # Dict of {conversation_id: [messages]}
    st.session_state.setdefault("messages", [])  # Current thread's messages
    st.session_state.setdefault("vector_store_ready", False)


def render_history():
    """Render chat history from session state for current conversation."""
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)


def chat_round(user_input):
    """Execute one round of chat with the agent."""
    # Append user message
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    # Prepare chat history for agent (convert to plain dicts)
    chat_history = []
    for msg in st.session_state.messages[:-1]:  # Exclude the message we just added
        if isinstance(msg, HumanMessage):
            chat_history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            chat_history.append({"role": "assistant", "content": msg.content})
    
    # Invoke agent
    agent = get_agent()
    try:
        result = agent.run(input=user_input, chat_history=chat_history)
        response_text = result if isinstance(result, str) else str(result)
    except Exception as e:
        response_text = f"Error: {str(e)}"
    
    # Append assistant response
    st.session_state.messages.append(AIMessage(content=response_text))


def start_new_conversation():
    """Start a new conversation thread."""
    conversation_id = str(uuid4())
    st.session_state.conversation_id = conversation_id
    st.session_state.messages = [
        AIMessage(content="Hi! I'm your e-commerce support assistant. How can I help you today?")
    ]
    st.session_state.conversations[conversation_id] = st.session_state.messages.copy()


def load_conversation(conv_id):
    """Load a previously saved conversation."""
    if conv_id in st.session_state.conversations:
        st.session_state.conversation_id = conv_id
        st.session_state.messages = st.session_state.conversations[conv_id].copy()


def main():
    """Main Streamlit app entry point."""
    st.set_page_config(page_title="LangChain Bot", page_icon="🤖")
    st.title("LangChain Bot")
    st.caption("Your e-commerce support assistant")
    
    load_dotenv()
    init_session()
    
    # Initialize vector store on first load
    if not st.session_state.vector_store_ready:
        with st.spinner("Initializing knowledge base..."):
            try:
                initialize_vector_store()
                st.session_state.vector_store_ready = True
            except Exception as e:
                st.error(f"Failed to initialize knowledge base: {e}")
                st.stop()
    
    # Login flow
    user_email = st.session_state.user_email
    if not user_email:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            role = st.selectbox("Role", ["customer", "admin"], key="login_role")
            submit = st.form_submit_button("Login")
        
        if submit:
            user = authenticate_user(email, password, role)
            if user:
                st.session_state.user_email = user["email"]
                st.session_state.user_role = user["role"]
                # Start a new conversation on login
                start_new_conversation()
                st.success(f"Welcome, {user['full_name']}!")
                st.rerun()
            else:
                st.error("Invalid email, password, or role.")
        return
    
    # Logged-in flow
    with st.sidebar:
        st.header("Conversations")
        
        # List conversations
        conv_ids = list(st.session_state.conversations.keys())
        if conv_ids:
            selected_conv = st.selectbox(
                "Select conversation",
                conv_ids,
                format_func=lambda x: f"Chat {x[:8]}..."
            )
            if selected_conv != st.session_state.conversation_id:
                load_conversation(selected_conv)
                st.rerun()
        else:
            st.write("(no threads yet)")
        
        if st.button("Start new conversation"):
            start_new_conversation()
            st.rerun()
    
    # Main chat area
    st.info(f"**Logged in as:** {user_email} ({st.session_state.user_role})  \n**Conversation ID:** {st.session_state.conversation_id or '—'}")
    
    render_history()
    
    prompt = st.chat_input("Ask a question")
    if prompt:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_round(prompt)
        
        # Update the conversation dict with new messages
        st.session_state.conversations[st.session_state.conversation_id] = st.session_state.messages.copy()
        st.rerun()


if __name__ == "__main__":
    main()
