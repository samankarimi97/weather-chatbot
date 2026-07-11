# AI Weather Assistant

An academic Python application that turns natural-language weather questions into current conditions or a five-day forecast.

The project uses spaCy named-entity recognition to identify a city in the user's question, requests weather data from OpenWeatherMap, and presents the result in a Streamlit interface.

## What It Demonstrates

- Natural-language location extraction with spaCy and `en_core_web_md`
- Integration with the OpenWeatherMap API
- Current-weather and five-day forecast views
- A small interactive web interface built with Streamlit
- Cached NLP model loading and weather responses

This project was developed for the AI Use Case course in the M.Sc. Artificial Intelligence program at IU International University of Applied Sciences.

## Technologies

- Python 3.11
- Streamlit
- spaCy
- Requests
- OpenWeatherMap API

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/samankarimi97/weather-chatbot.git
cd weather-chatbot
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Create `.streamlit/secrets.toml` and add an active OpenWeatherMap API key:

```toml
openweather_key = "your_api_key"
```

Do not commit this file or share the key publicly.

### 5. Start the application

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, enter a question containing a city name, and choose current weather or the five-day forecast.

Example questions:

- `What is the weather in Berlin?`
- `Show me the five-day forecast for Hamburg.`

## Project Structure

```text
weather-chatbot/
|-- app.py              # NLP, API integration, and Streamlit interface
|-- requirements.txt    # Python dependencies and spaCy language model
|-- runtime.txt         # Python version used by the hosted application
`-- .devcontainer/      # Optional development-container configuration
```

## Limitations

- City detection depends on spaCy recognizing a geographical entity; short or ambiguous input may not be detected.
- Weather data and availability depend on the OpenWeatherMap API and a valid API key.
- The five-day view samples the API's three-hour forecast data once per day; it is not a daily aggregation.
- The application does not train or evaluate a custom machine-learning model.
- Automated tests are not currently included.

## Live Application

The project has a [Streamlit Community Cloud deployment](https://saman-karimi-chatbot-ai-use-case-iu.streamlit.app/). Community Cloud may put inactive applications to sleep, so the page can require a manual wake-up before use.

## Status

Academic project maintained as a portfolio demonstration of applied NLP, API integration, and Python application development.
