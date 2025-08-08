import spacy
import time
import streamlit as st
import requests

nlp = spacy.load("en_core_web_md")

# OpenWeatherMap API setup
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
            'humidity': data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
        }
        return weather
    else:
        return None

# Initialize session state messages list
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI setup
st.set_page_config(page_title="WeatherBot", page_icon="⛅", layout="centered")

st.sidebar.title("About WeatherBot")
st.sidebar.markdown("This is a simple weather forecast chatbot built using Streamlit, spaCy, and the OpenWeatherMap API.")
st.sidebar.markdown("Enter a city name in the main chat area to get the current weather.")
st.sidebar.markdown("---")
st.sidebar.caption("Built by Saman Karimi")
st.sidebar.caption("Data provided by OpenWeatherMap")

st.title("⛅ Weather Forecast Chatbot")
st.markdown("Ask me about the weather anywhere in the world")

# Chat input with key to control value and clear after submit
user_input = st.text_input(
    "You:",
    key="input",
    placeholder="Type a city name, e.g., London, New York, Tokyo"
)

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Extract city using spaCy
    city = extract_city(user_input)

    if city:
        with st.spinner(f"Fetching weather for {city}..."):
            time.sleep(1)  # shorten spinner wait time for better UX
            weather = get_weather(city)

        if weather:
            # Build bot response string with weather details
            bot_message = (
                f"🌍 Weather Forecast for **{city.capitalize()}**:\n\n"
                f"- Description: {weather['description'].capitalize()}\n"
                f"- Temperature: {weather['temperature']} °C\n"
                f"- Humidity: {weather['humidity']}%\n"
                f"- Pressure: {weather['pressure']} hPa\n"
                f"- Wind Speed: {weather['wind_speed']} m/s"
            )
            st.session_state.messages.append({"role": "assistant", "content": bot_message})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"❌ Could not fetch weather data for {city}. Please check the city name and try again."})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "🔎 I couldn't detect a city in your message. Please try rephrasing your question."})

    # Clear the input box after processing
    st.session_state.input = ""

# Display chat history in order
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")

# Footer attribution
st.markdown("---")
st.caption("Built by Saman Karimi for AI Use Case Project - IU International University of Applied Sciences")
