
from dotenv import load_dotenv
import streamlit as st
import os
import time
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Keep only one page config at the start
st.set_page_config(
    page_title="Indian Healthcare Supply Chain Management Assistant",
    page_icon="🏥",
    layout="wide"
)

# Get API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found in environment variables")
    st.stop()

genai.configure(api_key=api_key)

# Update to use Gemini 2.0 Flash model
model = genai.GenerativeModel('gemini-2.0-flash')
chat = model.start_chat(history=[])

# Rate limiting configuration
REQUEST_WINDOW = 60  # seconds
MAX_REQUESTS = 10
request_timestamps = []

# Enhanced get_gemini_response function with rate limiting and improved error handling
def get_gemini_response(question):
    max_retries = 5
    retry_delay = 3  # seconds
    
    # Rate limiting check
    current_time = time.time()
    request_timestamps[:] = [ts for ts in request_timestamps if current_time - ts < REQUEST_WINDOW]
    
    if len(request_timestamps) >= MAX_REQUESTS:
        st.warning(f"Rate limit exceeded. Please wait {int(REQUEST_WINDOW - (current_time - request_timestamps[0]))} seconds.")
        return None
    
    request_timestamps.append(current_time)
    
    for attempt in range(max_retries):
        try:
            response = chat.send_message(question, stream=True)
            return response
        except google.api_core.exceptions.ServiceUnavailable as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                st.warning(f"Model is overloaded. Attempt {attempt + 1}/{max_retries}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                st.error("The model is currently overloaded. Please try again in a few minutes.")
                return None
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1}/{max_retries} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                st.error(f"Failed to get response after {max_retries} attempts. Please try again later.\n\nError: {str(e)}")
                return None

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Update page configuration
st.title("🏥 Indian Healthcare Supply Chain Management Assistant")
st.markdown("""
### Features:
- State-wise budget allocation recommendations
- Population-based resource distribution
- Supply chain optimization suggestions
- Healthcare infrastructure planning
""")

# Initialize session state for selected state and analysis type
if 'previous_state' not in st.session_state:
    st.session_state['previous_state'] = None
if 'previous_analysis' not in st.session_state:
    st.session_state['previous_analysis'] = None

# Sidebar for state selection and analysis type
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
    
    # Add a button to generate analysis with loading state
    if st.button("📊 Generate Analysis", key="generate_analysis"):
        with st.spinner(f"Generating {analysis_type.lower()} analysis for {selected_state}..."):
            query = f"Provide {analysis_type.lower()} analysis for {selected_state} in healthcare sector"
            response = get_gemini_response(query)
            
            if response is not None:
                st.session_state['chat_history'].append(("System", f"Analysis requested for {selected_state}: {analysis_type}"))
                
                try:
                    full_response = ""
                    for chunk in response:
                        full_response += chunk.text
                    
                    if full_response:
                        st.session_state['chat_history'].append(("Assistant", full_response))
                        st.success("Analysis generated successfully!")
                except Exception as e:
                    st.error(f"Error while generating analysis: {str(e)}")
                    if full_response:
                        st.session_state['chat_history'].append(("Assistant", full_response))

# Main chat interface
st.header("💬 Chat Interface")
input_text = st.text_input("Ask your question:", key="input")
submit = st.button("Submit Question")

if submit and input_text:
    response = get_gemini_response(input_text)
    if response is not None:
        st.session_state['chat_history'].append(("You", input_text))
        
        st.subheader("Response:")
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            for chunk in response:
                full_response += chunk.text
                response_placeholder.markdown(full_response)
            
            st.session_state['chat_history'].append(("Assistant", full_response))
        except Exception as e:
            st.error(f"Error while streaming response: {str(e)}")
            if full_response:
                st.session_state['chat_history'].append(("Assistant", full_response))

# Display chat history
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    if role == "You":
        st.markdown(f"**User:** {text}")
    else:
        st.markdown(f"**Assistant:** {text}")
    



    
