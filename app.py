import streamlit as st
import google.generativeai as genai

# Configure page
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Gemini Chatbot")
st.write("Simple chatbot to test your Google AI Studio API key")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Key input
api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")

if api_key:
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Test the API key
    try:
        # Try to list models
        models = list(genai.list_models())
        
        if models:
            st.success("✅ API key is working!")
            
            # Find a working model
            model_name = "gemini-1.5-flash"  # Default fallback
            for model in models:
                if "generateContent" in model.supported_generation_methods:
                    model_name = model.name
                    break
            
            st.info(f"Using model: {model_name}")
            
            # Initialize the model
            model = genai.GenerativeModel(model_name)
            
            # Chat interface
            st.subheader("Chat")
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # Chat input
            user_input = st.chat_input("Type your message...")
            
            if user_input:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Display user message
                with st.chat_message("user"):
                    st.write(user_input)
                
                # Generate and display response
                with st.chat_message("assistant"):
                    try:
                        with st.spinner("Thinking..."):
                            response = model.generate_content(user_input)
                            bot_response = response.text
                        
                        st.write(bot_response)
                        
                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": bot_response})
                        
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            # Clear chat button
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.experimental_rerun()
        
        else:
            st.error("❌ No models available")
            
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        st.write("Please check your API key.")

else:
    st.info("👆 Please enter your API key to start")
    st.write("Get your key: https://makersuite.google.com/app/apikey")

# Simple instructions
st.write("---")
st.write("**Instructions:**")
st.write("1. Get API key from Google AI Studio")
st.write("2. Enter it above")
st.write("3. Start chatting!")
