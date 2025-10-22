# ☁️ Weather Forecast Chatbot

**Author:** Saman Karimi | **Program:** Master of Science in Artificial Intelligence (AI) | **Institution:** IU International University of Applied Sciences

##  Project Overview

The **Weather Forecast Chatbot** is a data-driven web application that provides real-time, location-specific weather information through a natural language interface.

Developed using **Python** and **Streamlit**, the application leverages **Natural Language Processing (NLP)** via **spaCy** to parse conversational user queries, accurately extract city names, and retrieve current and multi-day forecasts using the **OpenWeatherMap API**. This project demonstrates the integration of NLP and external APIs to create a highly accessible, conversational AI tool for everyday decision-making.

##  Live Demo

The application is deployed and accessible via **Streamlit Cloud**:

👉 [**Launch Weather Forecast Chatbot**](https://saman-karimi-chatbot-ai-use-case-iu.streamlit.app)

## Key Features

* **Real-time Grounding:** Fetches current weather and multi-day forecasts for any city worldwide using the **OpenWeatherMap API**.

* **Intelligent NLP:** Utilizes **spaCy** with the `en_core_web_md` model for robust named-entity recognition and accurate city name extraction from unstructured text.

* **Responsive UI:** Designed with a user-friendly, clean interface using **Streamlit**.

## Checking the latest UI refresh locally

Recent updates introduced a softened gradient background, richer sidebar content, and card-style highlights for current metrics and the five-day outlook. To confirm you are seeing the newest interface locally:

1. Install dependencies (preferably inside a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the application:
   ```bash
   streamlit run app.py
   ```
3. The page title should read **"⛅ Weather Forecast Chatbot"** and the sidebar will display a photo with tips beneath the "About WeatherBot" section. If your browser shows an older layout, force refresh (Ctrl/Cmd+Shift+R) to clear cached assets.

##  Tech Stack

| **Component** | **Technology** | **Role** | 
| :--- | :--- | :--- | 
| **Frontend/UI** | Streamlit | Interactive web application framework | 
| **Backend/Logic** | Python | Core application scripting and logic | 
| **NLP Engine** | spaCy (`en_core_web_md`) | Natural Language Processing and entity extraction | 
| **Data Source** | OpenWeatherMap API | Real-time weather data retrieval | 

##  System Architecture

The chatbot follows a concise, linear workflow to process requests:

1. **Input:** User enters a natural language query (e.g., "What is the weather like in Berlin tomorrow?").

2. **NLP Parsing:** The spaCy model processes the text to identify and extract the geographical entity (city name).

3. **API Request:** The extracted city name is passed to the OpenWeatherMap API to fetch the required weather data.

4. **Data Transformation:** Python process the raw JSON response into a structured, user-friendly format.

5. **Output:** Streamlit renders the interactive results, displaying the forecast to the user.

##  License

This project is intended for academic and educational use as part of the AI Use Case course at IU International University of Applied Sciences.

##  Acknowledgments

* **Streamlit:** For providing a powerful and fast way to build interactive web applications in Python.

* **spaCy:** For its efficient and robust NLP library.

* **OpenWeatherMap:** For supplying comprehensive and reliable weather data.


