import streamlit as st
import spacy
import requests
import time

# Load SpaCy model
nlp = spacy.load("en_core_web_md")

API_KEY = st.secrets['openweather_key']
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def extract_city(user_input):
    doc = nlp(user_input)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    return None

def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
        }
        return weather
    else:
        return None

st.set_page_config(page_title="WeatherBot", page_icon="⛅", layout="centered")

# Sidebar
st.sidebar.title("About WeatherBot")
st.sidebar.markdown(
    "This is a simple weather forecast chatbot built using Streamlit, spaCy, and the OpenWeatherMap API."
)
st.sidebar.markdown("Enter a city name in the main chat area to get the current weather.")
st.sidebar.markdown("---")
st.sidebar.caption("Built by Saman Karimi")
st.sidebar.caption("Data provided by OpenWeatherMap")

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("⛅ Weather Forecast Chatbot")
st.markdown("Ask me about the weather anywhere in the world")

# Custom CSS for chat bubbles
st.markdown(
    """
    <style>
    .user-msg {
        background-color: #DCF8C6;
        padding: 12px 15px;
        border-radius: 20px 20px 0 20px;
        max-width: 60%;
        margin-left: auto;
        margin-bottom: 10px;
        font-size: 16px;
        white-space: pre-wrap;
    }
    .bot-msg {
        background-color: #F1F0F0;
        padding: 12px 15px;
        border-radius: 20px 20px 20px 0;
        max-width: 60%;
        margin-right: auto;
        margin-bottom: 10px;
        font-size: 16px;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# Input form with clear on submit
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="e.g., What's the weather in Berlin?")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    city = extract_city(user_input)

    if city:
        with st.spinner(f"Fetching weather for {city}..."):
            time.sleep(1)  # simulate delay
            weather = get_weather(city)

        if weather:
            bot_response = (
                f"🌍 Weather Forecast for **{city.capitalize()}**:\n"
                f"- Description: {weather['description'].capitalize()}\n"
                f"- Temperature: {weather['temperature']}°C\n"
                f"- Pressure: {weather['pressure']} hPa\n"
                f"- Humidity: {weather['humidity']}%\n"
                f"- Wind Speed: {weather['wind_speed']} m/s"
            )
        else:
            bot_response = f"❌ Could not fetch weather data for {city}. Please check the city name."
    else:
        bot_response = "🔎 I couldn't detect a city in your question. Please try rephrasing."

    st.session_state.messages.append({"role": "bot", "content": bot_response})

# Footer
st.markdown("---")
st.caption("Built by Saman Karimi for AI Use Case Project - IU International University of Applied Sciences")
