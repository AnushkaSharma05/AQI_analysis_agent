# AQI Analysis Agent

This Streamlit app fetches live air quality and weather data for a city, then turns it into a clean, readable health brief. It is beginner-friendly, heavily commented, and designed for quick AQI checks with simple guidance.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your keys:
   ```bash
   OPENWEATHER_API_KEY=your_openweather_key
   OPENROUTER_API_KEY=your_openrouter_key
   ```
3. Run the app:
   ```bash
   streamlit run main.py
   ```

## How It Works
- OpenWeather provides AQI and weather data for the selected city.
- The app builds a clean summary for the AI model.
- The AI returns a strict, UI-friendly response that is rendered as a styled card.

## File Overview
- main.py: Streamlit UI, styles, layout, and validation.
- agent.py: Builds the AI prompt and calls OpenRouter.
- aqi_fetcher.py: Calls OpenWeather APIs and returns AQI + weather data.
- requirements.txt: Python dependencies list.
- .env: API keys for OpenWeather and OpenRouter.
