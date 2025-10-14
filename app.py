import subprocess
import sys
import spacy
import os
import time
import streamlit as st
import requests
nlp = spacy.load("en_core_web_md")

# OpenWeatherMap API setup
API_KEY =st.secrets['openweather_key'] 
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Function to extract city name using spaCy
def extract_city(user_input):
    # Process the user input using the spaCy model
    doc = nlp(user_input)

    # Iterate over the identified entities
    for ent in doc.ents:
        # Check if the entity is a Geo-Political Entity (GPE), which often represents cities
        if ent.label_ == "GPE":
            # Return the extracted city name
            return ent.text

    # If no GPE is found, return None
    return None


# Function to get weather data from OpenWeatherMap API
def get_weather(city):
    # Set up the parameters for the API request
    params = {"q": city, "appid": API_KEY, "units": "metric"} # units=metric for Celsius

    # Make the GET request to the API
    response = requests.get(CURRENT_WEATHER_URL, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract the relevant weather information
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            'humidity' : data["main"]["humidity"],
            "pressure" : data["main"]["pressure"],
            "wind_speed" : data["wind"]["speed"],
            "description": data["weather"][0]["description"],
        }
        return weather
    else:
        # If the request was not successful, return None
        return None
# Get 5-day forecast
def get_forecast(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(FORECAST_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        forecasts = []
        # Pick one forecast per day (every 24h = 8 * 3h)
        for i in range(0, len(data["list"]), 8):
            item = data["list"][i]
            forecasts.append({
                "datetime": item["dt_txt"].split(" ")[0],
                "temp": item["main"]["temp"],
                "desc": item["weather"][0]["description"].capitalize()
            })
        return forecasts
    else:
        return None
# Streamlit User Interface (UI) setup
st.set_page_config(page_title="WeatherBot", page_icon="⛅", layout="centered")

# Add a sidebar
st.sidebar.title("About WeatherBot")
st.sidebar.markdown("This is a simple weather forecast chatbot built using Streamlit, spaCy, and the OpenWeatherMap API.")
st.sidebar.markdown("Enter a city name in the main chat area to get the current weather.")
st.sidebar.markdown("---")
st.sidebar.caption("Built by Saman Karimi")
st.sidebar.caption("Data provided by OpenWeatherMap")


st.title("⛅ Weather Forecast Chatbot")
st.markdown("Ask me about the weather anywhere in the world")


user_input = st.text_input(
    "Enter a city name to get the weather forecast:",
    placeholder="Ask your question about weather, I'm ready to answer",
    help="Type the full name of the city you want the weather forecast for and press Enter."
)

# Forecast mode selector
mode = st.radio("Select forecast type:", ["Current Weather", "5-Day Forecast"])

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
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🌡️ Temperature", f"{weather['temperature']}°C")
                        st.metric("💨 Wind Speed", f"{weather['wind_speed']} m/s")
                    with col2:
                        st.metric("💧 Humidity", f"{weather['humidity']}%")
                        st.metric("🔹 Pressure", f"{weather['pressure']} hPa")
                    st.markdown(f"**Description:** {weather['description'].capitalize()}")
                else:
                    st.error(f"❌ Could not fetch weather data for {city}. Please check the city name.")
            else:
                forecast = get_forecast(city)
                
               if forecast:
                    st.success(f"📅 5-Day Forecast for {city.capitalize()}")
                
                    # visual representation using a DataFrame
                    import pandas as pd
                    forecast_df = pd.DataFrame(forecast)
                    forecast_df.rename(columns={
                        "datetime": "Date",
                        "desc": "Weather Description",
                        "temp": "Temperature (°C)"
                    }, inplace=True)
                
                    # table display
                    st.dataframe(
                        forecast_df.style.set_properties(**{
                            'text-align': 'center',
                            'background-color': '#f9f9f9',
                            'border-color': '#cccccc'
                        }).set_table_styles([{
                            'selector': 'th',
                            'props': [('background-color', '#0078D4'), ('color', 'white'), ('text-align', 'center')]
                        }]),
                        use_container_width=True
                    )
                
                    st.caption("Data updated every 3 hours • Average daily values shown")

                else:
                    st.error(f"❌ Unable to retrieve forecast for {city}. Try again later.")
    else:
        st.warning("🔎 I couldn't detect a city name in your input. Please try again.")
elif user_input.strip() == "":
    st.info("💬 Please enter a city name or question to begin.")


st.markdown("")
st.markdown("---")
st.caption("Built by Saman Karimi for AI Use Case Project - IU International University of Applied Sciences")
