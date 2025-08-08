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

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages as markdown chat bubbles
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<p style="background-color:#DCF8C6; padding:10px; border-radius:10px; '
            f'text-align:right; max-width:60%; margin-left:auto;">{msg["content"]}</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p style="background-color:#F1F0F0; padding:10px; border-radius:10px; '
            f'text-align:left; max-width:60%;">{msg["content"]}</p>',
            unsafe_allow_html=True,
        )

# User input
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    city = extract_city(user_input)
    if city:
        with st.spinner(f"Fetching weather for {city}..."):
            time.sleep(1)
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

    # Clear the input box by resetting session state variable instead of rerun
    st.session_state["input"] = ""

# Footer
st.markdown("")
st.markdown("---")
st.caption("Built by Saman Karimi for AI Use Case Project - IU International University of Applied Sciences")
