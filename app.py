import time
from typing import Optional

import requests
import spacy
import streamlit as st
from spacy.language import Language


@st.cache_resource(show_spinner=False)
def load_nlp_model() -> Language:
    """Load and cache the spaCy model for entity extraction."""
    return spacy.load("en_core_web_md")


nlp = load_nlp_model()

# OpenWeatherMap API setup
API_KEY = st.secrets["openweather_key"]
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"


# Function to extract city name using spaCy
def extract_city(user_input: str) -> Optional[str]:
    doc = nlp(user_input)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    # If no GPE is found, return None
    return None


# Function to get weather data from OpenWeatherMap API
@st.cache_data(ttl=600, show_spinner=False)
def get_weather(city: str) -> Optional[dict]:
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract the relevant weather information
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
        }
        return weather
    return None


# Get 5-day forecast
@st.cache_data(ttl=600, show_spinner=False)
def get_forecast(city: str) -> Optional[list]:
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(FORECAST_URL, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        forecasts = []
        # Pick one forecast per day (every 24h = 8 * 3h)
        for i in range(0, len(data["list"]), 8):
            item = data["list"][i]
            forecasts.append(
                {
                    "datetime": item["dt_txt"].split(" ")[0],
                    "temp": item["main"]["temp"],
                    "desc": item["weather"][0]["description"].capitalize(),
                }
            )
        return forecasts
    return None


# Streamlit User Interface (UI) setup
st.set_page_config(page_title="WeatherBot", page_icon="⛅", layout="centered")

# Inject custom styling to modernize the interface
st.markdown(
    """
    <style>
    body {
        background: radial-gradient(circle at top, #e0f7ff 0%, #f5f7fb 60%, #ffffff 100%);
    }
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 860px;
    }
    .weather-card {
        background: rgba(255, 255, 255, 0.78);
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(135, 206, 250, 0.35);
        box-shadow: 0 18px 35px rgba(135, 206, 250, 0.18);
    }
    .forecast-card {
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        background: linear-gradient(135deg, rgba(135, 206, 250, 0.22), rgba(255, 255, 255, 0.85));
        border: 1px solid rgba(135, 206, 250, 0.35);
        margin-bottom: 0.8rem;
    }
    .stRadio > label {
        font-weight: 600;
        color: #1e3a56 !important;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.05rem;
        border-radius: 14px;
        border: 1px solid rgba(135, 206, 250, 0.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add sidebar content with richer context
st.sidebar.image(
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=400&q=80",
    use_column_width=True,
    caption="Keeping an eye on the skies",
)
st.sidebar.title("About WeatherBot")
st.sidebar.markdown(
    "WeatherBot pairs the OpenWeatherMap API with NLP city detection to deliver accurate, friendly forecasts on demand."
)
st.sidebar.markdown("**Tip:** Try natural questions such as `Do I need an umbrella in Paris today?`.")
st.sidebar.markdown("---")
st.sidebar.caption("Built by Saman Karimi")
st.sidebar.caption("Data provided by OpenWeatherMap")

st.title("⛅ Weather Forecast Chatbot")
st.subheader("Ask about the weather anywhere in the world and get instant answers.")

# Suggested prompts to encourage exploration
st.markdown(
    "**Popular quick asks:** "
    "`Weather in Tokyo right now`, `Is it raining in Seattle?`, `5-day outlook for Cape Town`"
)

user_input = st.text_input(
    "Enter a city name to get the weather forecast:",
    placeholder="Ask your question about weather, I'm ready to answer",
    help="Type the full name of the city you want the weather forecast for and press Enter.",
)

# Forecast mode selector
mode = st.radio("Select forecast type:", ["Current Weather", "5-Day Forecast"], horizontal=True)

# Process input
if user_input and user_input.strip():
    city = extract_city(user_input)

    if city:
        with st.spinner(f"Fetching {mode.lower()} for {city}..."):
            time.sleep(1.5)
            if mode == "Current Weather":
                weather = get_weather(city)
                if weather:
                    st.success(f"🌍 Current Weather in {city.capitalize()}")
                    with st.container():
                        col1, col2 = st.columns(2, gap="large")
                        with col1:
                            st.metric("🌡️ Temperature", f"{weather['temperature']}°C")
                            st.metric("💨 Wind Speed", f"{weather['wind_speed']} m/s")
                        with col2:
                            st.metric("💧 Humidity", f"{weather['humidity']}%")
                            st.metric("🔹 Pressure", f"{weather['pressure']} hPa")
                    st.markdown(
                        f"<div class='weather-card'><strong>Description:</strong> {weather['description'].capitalize()}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(
                        f"❌ Could not fetch weather data for {city}. Please check the city name or try again later."
                    )
            else:
                forecast = get_forecast(city)

                if forecast:
                    st.success(f"📅 5-Day Forecast for {city.capitalize()}")
                    for day in forecast:
                        st.markdown(
                            f"""
                            <div class='forecast-card'>
                                <strong>{day['datetime']}</strong><br/>
                                {day['desc']} • 🌡️ {day['temp']}°C
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.error(f"❌ Unable to retrieve forecast for {city}. Try again later.")
    else:
        st.warning("🔎 I couldn't detect a city name in your input. Please try again.")

st.markdown("---")
st.caption("Built by Saman Karimi for AI Use Case Project - IU International University of Applied Sciences")
