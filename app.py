import streamlit as st
import spacy
import requests
import time

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

st.sidebar.title("About WeatherBot")
st.sidebar.markdown("Simple weather forecast chatbot with Streamlit, spaCy & OpenWeatherMap API.")
st.sidebar.markdown("---")
st.sidebar.caption("Built by Saman Karimi")
st.sidebar.caption("Data provided by OpenWeatherMap")

st.title("⛅ Weather Forecast Chatbot")
st.markdown("Ask me about the weather anywhere in the world")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the chat messages from history on the page
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# Accept user input
user_input = st.chat_input("Enter a city name or ask about weather...")

if user_input:
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    city = extract_city(user_input)
    if city:
        with st.spinner(f"Fetching weather for {city}..."):
            time.sleep(1)  # simulate loading
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

    # Append bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Refresh the app to display the new messages
    st.experimental_rerun()
