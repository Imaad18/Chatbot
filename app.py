import streamlit as st
from streamlit_option_menu import option_menu
import openai
import requests
import json
import pandas as pd
import datetime
import time
from PIL import Image
import io
import base64
import plotly.express as px
import plotly.graph_objects as go

# Custom CSS styling
def inject_custom_css():
    st.markdown("""
    <style>
        /* Main styling */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid #e6e6e6;
        }
        
        /* Chat containers */
        .stChatMessage {
            border-radius: 15px !important;
            padding: 12px 15px !important;
            margin: 5px 0 !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        }
        
        /* User message */
        [data-testid="stChatMessage"]:has(div:first-child > .stMarkdown:contains('You')) {
            background-color: #e3f2fd !important;
        }
        
        /* AI message */
        [data-testid="stChatMessage"]:has(div:first-child > .stMarkdown:contains('AI Assistant')) {
            background-color: #ffffff !important;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 20px !important;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            padding: 8px 20px !important;
        }
        
        /* Input fields */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 15px !important;
            padding: 10px 15px !important;
            border: 1px solid #ddd !important;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0 !important;
            padding: 8px 20px !important;
            background-color: #f0f0f0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea !important;
            color: white !important;
        }
        
        /* Custom cards */
        .custom-card {
            border-radius: 15px;
            padding: 20px;
            background-color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        /* Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stChatMessage {
            animation: fadeIn 0.3s ease-out;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "image_prompt" not in st.session_state:
        st.session_state.image_prompt = ""
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None
    if "pixels_query" not in st.session_state:
        st.session_state.pixels_query = ""
    if "pixels_results" not in st.session_state:
        st.session_state.pixels_results = []
    if "stock_symbol" not in st.session_state:
        st.session_state.stock_symbol = "AAPL"
    if "crypto_symbol" not in st.session_state:
        st.session_state.crypto_symbol = "BTC"
    if "news_query" not in st.session_state:
        st.session_state.news_query = "technology"
    if "news_results" not in st.session_state:
        st.session_state.news_results = []

# Chat Tab
def chat_tab():
    st.header("💬 AI Chat Assistant")
    
    if not st.session_state.get("openai_api_key"):
        openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key
            openai.api_key = openai_api_key
            st.success("API key saved!")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                for response in openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": m["role"], "content": m["content"]} 
                              for m in st.session_state.chat_history],
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

# Image Generation Tab
def image_generation_tab():
    st.header("🖼️ AI Image Generation")
    
    if not st.session_state.get("together_api_key"):
        together_api_key = st.text_input("Enter your Together.ai API key:", type="password", key="together_key")
        if together_api_key:
            st.session_state.together_api_key = together_api_key
            st.success("API key saved!")
        return
    
    st.markdown("""
    <div class="custom-card">
        <h3>Generate images from text prompts</h3>
        <p>Enter a detailed description of the image you want to generate. The more specific you are, the better the results!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.image_prompt = st.text_area(
            "Image prompt:", 
            value=st.session_state.image_prompt,
            placeholder="A futuristic cityscape at night with flying cars and neon lights..."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Image"):
            if st.session_state.image_prompt:
                with st.spinner("Generating image... (this may take a few moments)"):
                    try:
                        headers = {
                            "Authorization": f"Bearer {st.session_state.together_api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        payload = {
                            "prompt": st.session_state.image_prompt,
                            "model": "stability-ai/sdxl",
                            "steps": 30,
                            "width": 1024,
                            "height": 1024
                        }
                        
                        response = requests.post(
                            "https://api.together.xyz/v1/images/generate",
                            headers=headers,
                            data=json.dumps(payload))
                        
                        if response.status_code == 200:
                            image_data = response.json()
                            if "output" in image_data and image_data["output"]:
                                image_url = image_data["output"][0]
                                st.session_state.generated_image = image_url
                                st.success("Image generated successfully!")
                            else:
                                st.error("Image generation failed. Please try again.")
                        else:
                            st.error(f"API Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error generating image: {str(e)}")
            else:
                st.warning("Please enter an image prompt")
    
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image)
        st.download_button(
            label="Download Image",
            data=requests.get(st.session_state.generated_image).content,
            file_name="generated_image.png",
            mime="image/png"
        )

# Video Search Tab
def video_search_tab():
    st.header("📹 Video Search")
    
    if not st.session_state.get("pixels_api_key"):
        pixels_api_key = st.text_input("Enter your Pexels API key:", type="password", key="pixels_key")
        if pixels_api_key:
            st.session_state.pixels_api_key = pixels_api_key
            st.success("API key saved!")
        return
    
    st.markdown("""
    <div class="custom-card">
        <h3>Search for high-quality stock videos</h3>
        <p>Find professional videos for your projects from Pexels' extensive library.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.pixels_query = st.text_input(
            "Search videos:", 
            value=st.session_state.pixels_query,
            placeholder="nature, business, technology..."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search Videos"):
            if st.session_state.pixels_query:
                with st.spinner("Searching videos..."):
                    try:
                        headers = {
                            "Authorization": st.session_state.pixels_api_key
                        }
                        
                        response = requests.get(
                            f"https://api.pexels.com/videos/search?query={st.session_state.pixels_query}&per_page=10",
                            headers=headers)
                        
                        if response.status_code == 200:
                            st.session_state.pixels_results = response.json().get("videos", [])
                            if not st.session_state.pixels_results:
                                st.warning("No videos found. Try a different search term.")
                        else:
                            st.error(f"API Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error searching videos: {str(e)}")
            else:
                st.warning("Please enter a search query")
    
    if st.session_state.pixels_results:
        st.subheader("Search Results")
        cols = st.columns(2)
        
        for idx, video in enumerate(st.session_state.pixels_results[:6]):
            with cols[idx % 2]:
                # Find the HD quality video if available
                hd_video = next((v for v in video['video_files'] if v['quality'] == 'hd'), video['video_files'][0])
                st.video(hd_video["link"])
                st.caption(f"Duration: {video['duration']}s | By: {video['user']['name']}")
                st.download_button(
                    label="Download",
                    data=requests.get(hd_video["link"]).content,
                    file_name=f"video_{idx}.mp4",
                    mime="video/mp4",
                    key=f"download_{idx}"
                )

# Finance Tab
def finance_tab():
    st.header("📈 Finance Dashboard")
    
    if not st.session_state.get("finhub_api_key") or not st.session_state.get("twelve_api_key"):
        col1, col2 = st.columns(2)
        with col1:
            finhub_api_key = st.text_input("Enter your Finnhub API key:", type="password", key="finhub_key")
            if finhub_api_key:
                st.session_state.finhub_api_key = finhub_api_key
        with col2:
            twelve_api_key = st.text_input("Enter your Twelve Data API key:", type="password", key="twelve_key")
            if twelve_api_key:
                st.session_state.twelve_api_key = twelve_api_key
        
        if st.session_state.get("finhub_api_key") and st.session_state.get("twelve_api_key"):
            st.success("API keys saved!")
        else:
            return
    
    tab1, tab2 = st.tabs(["Stocks", "Crypto"])
    
    with tab1:
        st.subheader("Stock Market Data")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.session_state.stock_symbol = st.text_input(
                "Stock Symbol:", 
                value=st.session_state.stock_symbol,
                placeholder="AAPL, MSFT, GOOGL..."
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Get Stock Data"):
                if st.session_state.stock_symbol:
                    with st.spinner("Fetching stock data..."):
                        try:
                            # Get basic stock info
                            response = requests.get(
                                f"https://finnhub.io/api/v1/stock/profile2?symbol={st.session_state.stock_symbol}&token={st.session_state.finhub_api_key}")
                            
                            if response.status_code == 200:
                                stock_info = response.json()
                                
                                # Get stock quote
                                quote_response = requests.get(
                                    f"https://finnhub.io/api/v1/quote?symbol={st.session_state.stock_symbol}&token={st.session_state.finhub_api_key}")
                                
                                if quote_response.status_code == 200:
                                    quote_data = quote_response.json()
                                    
                                    # Display stock info
                                    st.markdown(f"""
                                    <div class="custom-card">
                                        <h3>{stock_info.get('name', 'N/A')} ({st.session_state.stock_symbol})</h3>
                                        <p><strong>Current Price:</strong> ${quote_data.get('c', 'N/A'):,.2f}</p>
                                        <p><strong>Change:</strong> <span style="color: {'red' if quote_data.get('d', 0) < 0 else 'green'}">
                                            {quote_data.get('d', 'N/A'):,.2f} ({quote_data.get('dp', 'N/A'):,.2f}%)
                                        </span></p>
                                        <p><strong>High:</strong> ${quote_data.get('h', 'N/A'):,.2f}</p>
                                        <p><strong>Low:</strong> ${quote_data.get('l', 'N/A'):,.2f}</p>
                                        <p><strong>Exchange:</strong> {stock_info.get('exchange', 'N/A')}</p>
                                        <p><strong>Industry:</strong> {stock_info.get('finnhubIndustry', 'N/A')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Get historical data for chart
                                    end_date = datetime.datetime.now()
                                    start_date = end_date - datetime.timedelta(days=365)
                                    
                                    hist_response = requests.get(
                                        f"https://api.twelvedata.com/time_series?symbol={st.session_state.stock_symbol}&interval=1day&start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&apikey={st.session_state.twelve_api_key}")
                                    
                                    if hist_response.status_code == 200:
                                        hist_data = hist_response.json().get("values", [])
                                        if hist_data:
                                            df = pd.DataFrame(hist_data)
                                            df['datetime'] = pd.to_datetime(df['datetime'])
                                            df['close'] = pd.to_numeric(df['close'])
                                            
                                            fig = px.line(df, x='datetime', y='close', 
                                                         title=f"{st.session_state.stock_symbol} Price (1 Year)")
                                            st.plotly_chart(fig, use_container_width=True)
                                        else:
                                            st.warning("No historical data available")
                                    else:
                                        st.error(f"Historical data error: {hist_response.text}")
                                else:
                                    st.error(f"Quote error: {quote_response.text}")
                            else:
                                st.error(f"Stock info error: {response.text}")
                        
                        except Exception as e:
                            st.error(f"Error fetching stock data: {str(e)}")
                else:
                    st.warning("Please enter a stock symbol")
    
    with tab2:
        st.subheader("Cryptocurrency Data")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.session_state.crypto_symbol = st.text_input(
                "Crypto Symbol:", 
                value=st.session_state.crypto_symbol,
                placeholder="BTC, ETH, SOL..."
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Get Crypto Data"):
                if st.session_state.crypto_symbol:
                    with st.spinner("Fetching crypto data..."):
                        try:
                            if not st.session_state.get("coinapi_api_key"):
                                coinapi_api_key = st.text_input("Enter your CoinAPI key:", type="password", key="coinapi_key")
                                if coinapi_api_key:
                                    st.session_state.coinapi_api_key = coinapi_api_key
                                    st.rerun()
                                return
                            
                            headers = {
                                "X-CoinAPI-Key": st.session_state.coinapi_api_key
                            }
                            
                            # Get current price
                            response = requests.get(
                                f"https://rest.coinapi.io/v1/exchangerate/{st.session_state.crypto_symbol}/USD",
                                headers=headers)
                            
                            if response.status_code == 200:
                                crypto_data = response.json()
                                
                                # Get historical data
                                end_time = datetime.datetime.now()
                                start_time = end_time - datetime.timedelta(days=30)
                                
                                hist_response = requests.get(
                                    f"https://rest.coinapi.io/v1/ohlcv/{st.session_state.crypto_symbol}/USD/history?period_id=1DAY&time_start={start_time.strftime('%Y-%m-%dT%H:%M:%S')}&time_end={end_time.strftime('%Y-%m-%dT%H:%M:%S')}",
                                    headers=headers)
                                
                                if hist_response.status_code == 200:
                                    hist_data = hist_response.json()
                                    
                                    # Display crypto info
                                    st.markdown(f"""
                                    <div class="custom-card">
                                        <h3>{st.session_state.crypto_symbol}/USD</h3>
                                        <p><strong>Current Price:</strong> ${crypto_data.get('rate', 'N/A'):,.2f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if hist_data:
                                        df = pd.DataFrame(hist_data)
                                        df['time_period_start'] = pd.to_datetime(df['time_period_start'])
                                        df['price_close'] = pd.to_numeric(df['price_close'])
                                        
                                        fig = px.line(df, x='time_period_start', y='price_close', 
                                                     title=f"{st.session_state.crypto_symbol} Price (30 Days)")
                                        st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.warning("No historical data available")
                                else:
                                    st.error(f"Historical data error: {hist_response.text}")
                            else:
                                st.error(f"Crypto data error: {response.text}")
                        
                        except Exception as e:
                            st.error(f"Error fetching crypto data: {str(e)}")
                else:
                    st.warning("Please enter a crypto symbol")

# News Tab
def news_tab():
    st.header("📰 News Explorer")
    
    if not st.session_state.get("news_api_key"):
        news_api_key = st.text_input("Enter your NewsAPI key:", type="password", key="news_key")
        if news_api_key:
            st.session_state.news_api_key = news_api_key
            st.success("API key saved!")
        return
    
    st.markdown("""
    <div class="custom-card">
        <h3>Stay updated with the latest news</h3>
        <p>Search for news articles from thousands of sources worldwide.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.news_query = st.text_input(
            "Search news:", 
            value=st.session_state.news_query,
            placeholder="technology, business, sports..."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search News"):
            if st.session_state.news_query:
                with st.spinner("Searching news..."):
                    try:
                        response = requests.get(
                            f"https://newsapi.org/v2/everything?q={st.session_state.news_query}&pageSize=10&apiKey={st.session_state.news_api_key}")
                        
                        if response.status_code == 200:
                            st.session_state.news_results = response.json().get("articles", [])
                            if not st.session_state.news_results:
                                st.warning("No news found. Try a different search term.")
                        else:
                            st.error(f"API Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error searching news: {str(e)}")
            else:
                st.warning("Please enter a search query")
    
    if st.session_state.news_results:
        st.subheader("Top News Articles")
        for article in st.session_state.news_results[:5]:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <h4><a href="{article['url']}" target="_blank">{article['title']}</a></h4>
                    <p><em>{article['source']['name']} • {article['publishedAt'][:10]}</em></p>
                    <p>{article['description']}</p>
                </div>
                """, unsafe_allow_html=True)

# Main App
def main():
    inject_custom_css()
    init_session_state()
    
    st.title("🤖 Multi-Purpose AI Assistant")
    st.markdown("""
    <div class="custom-card">
        <p>Your all-in-one AI assistant with chat, image generation, video search, stock market data, and news capabilities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with API key management
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50.png?text=AI+Assistant", width=150)
        st.title("Settings")
        
        # API Key Management
        with st.expander("🔑 API Key Management", expanded=False):
            st.markdown("""
            <p style="font-size: small;">Enter your API keys to enable all features. Keys are stored in your session and never saved on our servers.</p>
            """, unsafe_allow_html=True)
            
            if "openai_api_key" in st.session_state:
                st.success("OpenAI API key configured")
            if "together_api_key" in st.session_state:
                st.success("Together.ai API key configured")
            if "pixels_api_key" in st.session_state:
                st.success("Pexels API key configured")
            if "finhub_api_key" in st.session_state:
                st.success("Finnhub API key configured")
            if "twelve_api_key" in st.session_state:
                st.success("Twelve Data API key configured")
            if "coinapi_api_key" in st.session_state:
                st.success("CoinAPI key configured")
            if "news_api_key" in st.session_state:
                st.success("NewsAPI key configured")
        
        # Clear all button
        if st.button("Clear All API Keys"):
            for key in ["openai_api_key", "together_api_key", "pixels_api_key", 
                       "finhub_api_key", "twelve_api_key", "coinapi_api_key", "news_api_key"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size: small;">
            <p><strong>Note:</strong> This application requires API keys for various services.</p>
            <p>You'll need to sign up for:</p>
            <ul>
                <li>OpenAI (Chat)</li>
                <li>Together.ai (Image Generation)</li>
                <li>Pexels (Video Search)</li>
                <li>Finnhub & Twelve Data (Finance)</li>
                <li>CoinAPI (Crypto)</li>
                <li>NewsAPI (News)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main tabs
    tabs = [
        "AI Chat",
        "Image Generation",
        "Video Search",
        "Finance Dashboard",
        "News Explorer"
    ]
    
    selected_tab = option_menu(
        None,
        tabs,
        icons=["chat", "image", "camera-video", "graph-up", "newspaper"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#667eea", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )
    
    if selected_tab == "AI Chat":
        chat_tab()
    elif selected_tab == "Image Generation":
        image_generation_tab()
    elif selected_tab == "Video Search":
        video_search_tab()
    elif selected_tab == "Finance Dashboard":
        finance_tab()
    elif selected_tab == "News Explorer":
        news_tab()

if __name__ == "__main__":
    main()
