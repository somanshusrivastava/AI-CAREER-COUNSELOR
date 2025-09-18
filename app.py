import streamlit as st
import google.generativeai as genai
import database

# --- Database Initialization ---
database.init_db()


# --- Gemini API Function ---
def get_gemini_response(api_key, conversation_history):
    """Calls the Gemini API with the conversation history."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(conversation_history)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}. Please check your API key.")
        return None


# --- Streamlit App UI ---
st.set_page_config(page_title="AI Career Counselor", page_icon="🤖", layout="centered")

st.title("🤖 AI Career Counselor")

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

# --- Authentication UI in Sidebar ---
st.sidebar.title("👤 Account")

if st.session_state.logged_in:
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
else:
    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                user_id = database.check_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.sidebar.error("Invalid username or password.")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Email (will be your username)")
            new_password = st.text_input("Choose a Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                if database.add_user(new_username, new_password):
                    st.sidebar.success("Account created successfully! Please login.")
                else:
                    st.sidebar.error("This email is already registered.")

# --- Main Chat Interface ---
if st.session_state.logged_in:
    # Load and display chat history
    history = database.load_history(st.session_state.user_id)
    st.session_state.messages = [{"role": msg["role"], "content": msg["parts"][0]} for msg in history]

    # Display initial message if history is empty
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I am your AI Career Counselor. How can I help you today?"
        }]

    for message in st.session_state.messages:
        with st.chat_message("assistant" if message["role"] != "user" else "user"):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Ask about your career..."):
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            st.warning("API Key not configured. Please contact the administrator.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            database.save_message(st.session_state.user_id, "user", prompt)

            with st.spinner("Thinking..."):
                api_history = [{"role": msg["role"] if msg["role"] == "user" else "model", "parts": [msg["content"]]}
                               for msg in st.session_state.messages]
                response_content = get_gemini_response(api_key, api_history)

            if response_content:
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)
                database.save_message(st.session_state.user_id, "assistant", response_content)
else:
    st.info("Welcome! Please log in or register using the sidebar to start your conversation.")