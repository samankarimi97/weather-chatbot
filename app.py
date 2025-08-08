import streamlit as st
import requests
import spacy
import os
import time # Import time for simulating delay for spinner

# Check if the spaCy model exists, download if not
# This check is more suitable for a standalone script
# In a notebook environment, it might be handled differently or assumed pre-installed
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    st.error("SpaCy model 'en_core_web_md' not found. Please ensure it's downloaded.")
    st.warning("You can download it by running: python -m spacy download en_core_web_md")
    st.stop() # Stop execution if model is not found

# OpenWeatherMap API setup
# Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
API_KEY = 'ce8f2aaac5bffc08c84aba9a7d043d6f'
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

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
    response = requests.get(BASE_URL, params=params)

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

# Text input for the user to type their question with improved labeling and guidance
user_input = st.text_input(
    "Enter a city name to get the weather forecast:",
    placeholder="e.g., London, New York, Tokyo",
    help="Type the full name of the city you want the weather forecast for and press Enter."
)

# Process the user input only if it's not empty after stripping whitespace
if user_input and user_input.strip():
    # Extract the city name from the input
    city = extract_city(user_input)

    # If a city was successfully extracted
    if city:
        # Get the weather data for the extracted city with a spinner
        with st.spinner(f"Fetching weather for {city}..."):
            # Simulate fetching time to see the spinner, remove in production if not needed
            time.sleep(3)
            weather = get_weather(city)

        # If weather data was successfully fetched
        if weather:
            # Display the weather information
            st.success(f"🌍 Weather Forcast for {city.capitalize()}")
            st.write(f"**Description:** {weather['description'].capitalize()}")

            # Use columns for detailed weather metrics
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Temperature:** {weather['temperature']}°C")
                st.write(f"**Pressure:** {weather['pressure']} hPa")

            with col2:
                st.write(f"**Humidity:** {weather['humidity']}%")
                st.write(f"**Wind Speed:** {weather['wind_speed']} m/s")

        else:
            # Display an error message if weather data could not be fetched
            st.error(f"❌ Could not fetch weather data for {city}. Please check the city name and try again.")
    else:
        # Display a warning if no city was detected in the input
        st.warning("🔎 I couldn't detect a city in your question. Please try rephrasing your question.")
elif user_input.strip() == "":
     st.info("Please enter a city name to get the weather.")

# Footer section for attribution
st.markdown("")
st.markdown("---")
st.caption("Built by Saman Karimi for AI Use Case Project - IU International University of Applied Sciences")
