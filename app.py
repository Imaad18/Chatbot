import streamlit as st
import openai
from openai import OpenAI

# Configure page
st.set_page_config(
    page_title="GPT Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 GPT Chatbot")
st.write("Simple chatbot to test your OpenAI API key")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Key input
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if api_key:
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
        
        # Test the API key by listing models
        models = client.models.list()
        
        st.success("✅ API key is working!")
        
        # Model selection
        gpt_models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        selected_model = st.selectbox(
            "Select GPT Model:", 
            gpt_models,
            index=0
        )
        
        st.info(f"Using model: {selected_model}")
        
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
                        # Prepare messages for API
                        api_messages = [
                            {"role": "system", "content": "You are a helpful assistant."}
                        ]
                        
                        # Add conversation history (last 10 messages to avoid token limits)
                        recent_messages = st.session_state.messages[-10:]
                        for msg in recent_messages:
                            if msg["role"] in ["user", "assistant"]:
                                api_messages.append({
                                    "role": msg["role"],
                                    "content": msg["content"]
                                })
                        
                        # Make API call
                        response = client.chat.completions.create(
                            model=selected_model,
                            messages=api_messages,
                            max_tokens=1000,
                            temperature=0.7
                        )
                        
                        bot_response = response.choices[0].message.content
                    
                    st.write(bot_response)
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    
                    # Handle common errors
                    if "insufficient_quota" in str(e):
                        st.write("💳 **Quota exceeded** - Check your OpenAI billing")
                    elif "invalid_api_key" in str(e):
                        st.write("🔑 **Invalid API key** - Check your API key")
                    elif "model_not_found" in str(e):
                        st.write("🤖 **Model not available** - Try a different model")
                    
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear chat button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("📊 Token Usage"):
                total_tokens = sum(len(msg["content"].split()) for msg in st.session_state.messages)
                st.info(f"Approximate tokens used: {total_tokens * 1.3:.0f}")
        
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        
        # Provide specific guidance
        if "invalid_api_key" in str(e):
            st.write("**Invalid API Key Issues:**")
            st.write("- Check that you copied the key correctly")
            st.write("- Make sure the API key is active")
            st.write("- Verify you have credits/billing set up")
        elif "insufficient_quota" in str(e):
            st.write("**Quota Issues:**")
            st.write("- Check your OpenAI billing dashboard")
            st.write("- You might need to add credits")
            st.write("- Free tier has usage limits")
        else:
            st.write("**Common Issues:**")
            st.write("- Check your internet connection")
            st.write("- Verify your API key is valid")
            st.write("- Make sure you have OpenAI credits")

else:
    st.info("👆 Please enter your OpenAI API key to start")
    st.write("Get your key: https://platform.openai.com/api-keys")

# Instructions
st.write("---")
st.write("**Instructions:**")
st.write("1. Get API key from OpenAI Platform")
st.write("2. Make sure you have billing/credits set up")
st.write("3. Enter the key above")
st.write("4. Select your preferred GPT model")
st.write("5. Start chatting!")

# Model info
with st.expander("ℹ️ Model Information"):
    st.write("""
    - **gpt-4o**: Latest and most capable model
    - **gpt-4o-mini**: Faster and cheaper version of GPT-4o
    - **gpt-4-turbo**: Previous generation, good performance
    - **gpt-4**: Original GPT-4, high quality
    - **gpt-3.5-turbo**: Fastest and cheapest option
    """)
