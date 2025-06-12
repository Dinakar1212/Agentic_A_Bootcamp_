import streamlit as st
import requests

# --- Replace with your actual n8n webhook URL ---
WEBHOOK_URL = "https://dinakar.app.n8n.cloud/webhook-test/7600346f-243e-44ed-90fa-09ab52118aca"

# --- Replace with your actual credentials ---
USER_CREDENTIALS = {
    "Dinakar": "Dinakar123",
    "Dino": "Dino123"
}

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- Login Functionality ---
def login():
    st.title("Event Portal - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
           
        else:
            st.error("Invalid username or password")

# --- Logout Functionality ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
   

# --- Form to Submit Meeting Action Items ---
def action_item_form():
    st.title("Submit Meeting Action Items")

    with st.form("action_form"):
        name = st.text_input("Name")
        email_id = st.text_area("Email ID")
        due_date = st.date_input("Due Date")
        phone = st.text_input("Phone")
        submit = st.form_submit_button("Submit")


        if submit:
            payload = {
                "name": name,
                "email id": email_id,
                "phone number": phone,
                "event_date": str(due_date),
            }
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    st.success("Action item submitted successfully!")
                else:
                    st.error(f"Failed to submit. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    if st.button("Logout"):
        logout()

# --- Main App ---
def main():
    if not st.session_state.logged_in:
        login()
    else:
        action_item_form()

if __name__ == "__main__":
    main()
