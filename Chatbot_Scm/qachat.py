
import streamlit as st
import os
import google.generativeai as genai

# Keep only one page config at the start
st.set_page_config(
    page_title="Indian Healthcare Supply Chain Management Assistant",
    page_icon="🏥",
    layout="wide"
)

# Directly set API key
api_key = "AIzaSyAc42dDURKVVSUc6KG-8ZDZ3tAtAK959es"
genai.configure(api_key=api_key)

# Update to use Gemini 2.0 Flash model
model = genai.GenerativeModel('models/gemini-2.0-flash')
chat = model.start_chat(history=[])

# Simplify the get_gemini_response function
def get_gemini_response(question):
    # Remove healthcare context from the actual query
    response = chat.send_message(question, stream=True)
    return response

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Update page configuration
# Remove the duplicate set_page_config() from here
# Continue with the rest of your UI elements
st.title("🏥 Indian Healthcare Supply Chain Management Assistant")
st.markdown("""
### Features:
- State-wise budget allocation recommendations
- Population-based resource distribution
- Supply chain optimization suggestions
- Healthcare infrastructure planning
""")

# Sidebar for state selection and population input
with st.sidebar:
    st.header("Quick Access")
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Budget Allocation", "Supply Chain Optimization", "Infrastructure Planning", "Resource Distribution"]
    )
    
    st.subheader("State-wise Population Data")
    indian_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]
    selected_state = st.selectbox("Select State/UT", indian_states)

# Main chat interface
st.header("💬 Chat Interface")
input_text = st.text_input("Ask your question:", key="input")
submit = st.button("Submit Question")

if submit and input_text:
    response = get_gemini_response(input_text)
    st.session_state['chat_history'].append(("You", input_text))
    
    st.subheader("Response:")
    response_placeholder = st.empty()
    full_response = ""
    
    for chunk in response:
        full_response += chunk.text
        response_placeholder.markdown(full_response)
    
    st.session_state['chat_history'].append(("Assistant", full_response))

# Display chat history
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    if role == "You":
        st.markdown(f"**User:** {text}")
    else:
        st.markdown(f"**Assistant:** {text}")
    



    
