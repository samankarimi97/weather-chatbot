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

API_KEY = st.secrets["openweather_key"]
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def extract_city(user_input: str) -> Optional[str]:
    cleaned = user_input.strip()
    doc = nlp(cleaned)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text

    # Also accept a direct city name such as "Berlin".
    if cleaned and len(cleaned.split()) <= 3:
        return cleaned
    return None


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(city: str) -> Optional[dict]:
    try:
        response = requests.get(
            CURRENT_WEATHER_URL,
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["name"],
            "country": data.get("sys", {}).get("country", ""),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
        }
    except (requests.RequestException, KeyError, ValueError):
        return None


@st.cache_data(ttl=600, show_spinner=False)
def get_forecast(city: str) -> Optional[list]:
    try:
        response = requests.get(
            FORECAST_URL,
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        forecasts = []
        seen_dates = set()
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            hour = item["dt_txt"].split(" ")[1]
            if date not in seen_dates and hour in {"12:00:00", "15:00:00"}:
                seen_dates.add(date)
                forecasts.append(
                    {
                        "date": date,
                        "temp": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "humidity": item["main"]["humidity"],
                        "description": item["weather"][0]["description"].capitalize(),
                        "icon": item["weather"][0]["icon"],
                    }
                )
            if len(forecasts) == 5:
                break
        return forecasts or None
    except (requests.RequestException, KeyError, ValueError):
        return None


st.set_page_config(
    page_title="WeatherBot",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --surface: rgba(17, 32, 53, 0.76);
        --surface-strong: rgba(20, 39, 64, 0.96);
        --border: rgba(148, 163, 184, 0.18);
        --text: #f8fafc;
        --muted: #9fb0c7;
        --accent: #38bdf8;
        --accent-2: #818cf8;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 5%, rgba(56, 189, 248, 0.18), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(129, 140, 248, 0.15), transparent 28%),
            linear-gradient(180deg, #07111f 0%, #0b1423 55%, #07101c 100%);
        color: var(--text);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }

    .main .block-container {
        max-width: 1120px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem 2.2rem;
        border: 1px solid var(--border);
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(17, 32, 53, 0.92), rgba(15, 23, 42, 0.74));
        box-shadow: 0 28px 80px rgba(0, 0, 0, 0.28);
        margin-bottom: 1.6rem;
    }

    .eyebrow {
        color: #7dd3fc;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }

    .hero h1 {
        color: #f8fafc;
        font-size: clamp(2.2rem, 6vw, 4.5rem);
        line-height: 0.98;
        letter-spacing: -0.055em;
        margin: 0 0 0.85rem 0;
    }

    .hero p {
        color: var(--muted);
        font-size: 1.05rem;
        max-width: 720px;
        margin: 0;
    }

    .section-label {
        color: #cbd5e1;
        font-weight: 700;
        margin: 1.1rem 0 0.45rem;
    }

    .weather-summary {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        padding: 1.35rem 1.5rem;
        border-radius: 22px;
        border: 1px solid var(--border);
        background: linear-gradient(135deg, rgba(14, 116, 144, 0.2), rgba(30, 41, 59, 0.82));
        margin: 1.2rem 0;
    }

    .weather-summary img { width: 78px; height: 78px; }
    .weather-summary h2 { margin: 0; color: #f8fafc; font-size: 1.55rem; }
    .weather-summary p { margin: 0.25rem 0 0; color: #a9bad0; }

    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        padding: 1.25rem 1.35rem;
        border-radius: 20px;
        min-height: 132px;
        box-shadow: 0 16px 36px rgba(0,0,0,.16);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #aebed2 !important;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    .forecast-card {
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1.2rem;
        background: var(--surface);
        min-height: 210px;
        box-shadow: 0 14px 32px rgba(0,0,0,.15);
        text-align: center;
    }

    .forecast-card img { width: 70px; height: 70px; }
    .forecast-card .date { color: #e2e8f0; font-weight: 800; }
    .forecast-card .temp { color: white; font-size: 1.65rem; font-weight: 800; margin: .35rem 0; }
    .forecast-card .desc { color: #9fb0c7; font-size: .92rem; }
    .forecast-card .meta { color: #7dd3fc; font-size: .82rem; margin-top: .65rem; }

    .footer {
        color: #718096;
        text-align: center;
        margin-top: 2.5rem;
        font-size: .88rem;
    }

    div[data-baseweb="input"] > div {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(125, 211, 252, 0.25);
        border-radius: 16px;
    }

    div[data-baseweb="input"] input { color: #f8fafc; }
    div[role="radiogroup"] { gap: .65rem; }

    @media (max-width: 700px) {
        .main .block-container { padding: 1rem; }
        .hero { padding: 1.45rem; border-radius: 22px; }
        .weather-summary { align-items: flex-start; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Live weather intelligence</div>
        <h1>WeatherBot</h1>
        <p>Ask naturally, get current conditions and a clean five-day forecast for any city worldwide.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

user_input = st.text_input(
    "Search a city",
    placeholder="Try: Weather in Berlin or Tokyo",
    help="Enter a city name or ask a natural-language weather question.",
)
mode = st.radio(
    "Forecast type",
    ["Current weather", "5-day forecast"],
    horizontal=True,
)

if user_input and user_input.strip():
    city = extract_city(user_input)
    if city:
        with st.spinner(f"Checking the sky over {city}..."):
            time.sleep(0.45)
            if mode == "Current weather":
                weather = get_weather(city)
                if weather:
                    location = weather["city"]
                    if weather["country"]:
                        location += f", {weather['country']}"
                    st.markdown(
                        f"""
                        <div class="weather-summary">
                            <img src="https://openweathermap.org/img/wn/{weather['icon']}@2x.png" alt="Weather icon">
                            <div>
                                <h2>{location}</h2>
                                <p>{weather['description'].capitalize()} · Feels like {weather['feels_like']:.1f}°C</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Temperature", f"{weather['temperature']:.1f}°C")
                    col2.metric("Humidity", f"{weather['humidity']}%")
                    col3.metric("Wind speed", f"{weather['wind_speed']:.1f} m/s")
                    col4.metric("Pressure", f"{weather['pressure']} hPa")
                else:
                    st.error("Weather data could not be loaded. Check the city name and try again.")
            else:
                forecast = get_forecast(city)
                if forecast:
                    st.markdown(f"<div class='section-label'>5-day forecast for {city.title()}</div>", unsafe_allow_html=True)
                    columns = st.columns(len(forecast))
                    for column, day in zip(columns, forecast):
                        with column:
                            st.markdown(
                                f"""
                                <div class="forecast-card">
                                    <div class="date">{day['date']}</div>
                                    <img src="https://openweathermap.org/img/wn/{day['icon']}@2x.png" alt="Weather icon">
                                    <div class="temp">{day['temp']:.1f}°C</div>
                                    <div class="desc">{day['description']}</div>
                                    <div class="meta">Feels {day['feels_like']:.1f}° · Humidity {day['humidity']}%</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                else:
                    st.error("The forecast could not be loaded. Check the city name and try again.")
    else:
        st.warning("I couldn't detect a city. Try entering the city name directly.")
else:
    st.markdown(
        "<div class='section-label'>Popular searches: Berlin · London · Tokyo · New York · Cape Town</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div class='footer'>Built by Saman Karimi · Weather data by OpenWeatherMap</div>", unsafe_allow_html=True)
