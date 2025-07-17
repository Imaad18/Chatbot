import streamlit as st
import google.generativeai as genai
import os

# Configure page
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Gemini Chatbot")
st.write("Simple chatbot to test your Google AI Studio API key")

# API Key input
api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")

if api_key:
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Initialize the model
    try:
        model = genai.GenerativeModel('gemini-pro')
        st.success("✅ API key configured successfully!")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
                # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Thinking..."):
                        response = model.generate_content(prompt)
                        response_text = response.text
                    
                    st.markdown(response_text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
            
    except Exception as e:
        st.error(f"Error configuring API: {str(e)}")
        st.write("Please check your API key and try again.")

else:
    st.info("👆 Please enter your Google AI Studio API key to start chatting")
    st.write("You can get your API key from: https://makersuite.google.com/app/apikey")

# Instructions
with st.expander("How to use"):
    st.write("""
    1. Get your API key from Google AI Studio: https://makersuite.google.com/app/apikey
    2. Enter the API key in the input field above
    3. Start chatting with Gemini!
    4. Use the 'Clear Chat' button to reset the conversation
    """)

# Installation requirements
with st.expander("Installation Requirements"):
    st.code("""
pip install streamlit google-generativeai
    """)
