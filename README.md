# AQI Analysis Agent

A personalized air quality monitoring app powered by AI that gives real time health recommendations.

## 🖼️ Screenshot
![alt text](image.png)

## ✨ Features
- Real time AQI data from OpenWeather
- EPA formula for accurate AQI calculation
- AI powered health recommendations via Claude
- Personalized advice based on medical conditions
- Dark cyberpunk UI built with Streamlit
- City validation and error handling

## 🧰 Tech Stack
- Python
- Streamlit (UI)
- OpenWeather API (AQI + weather data)
- OpenRouter + Claude (AI recommendations)
- WAQI API (cross check AQI accuracy)

## ⚙️ Setup
1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a .env file with these keys:
   ```bash
   OPENWEATHER_API_KEY=your-key
   OPENROUTER_API_KEY=your-key
   WAQI_API_KEY=your-key
   ```
4. Run:
   ```bash
   streamlit run main.py
   ```

## 🔑 How to Get API Keys
- OpenWeather: openweathermap.org
- OpenRouter: openrouter.ai
- WAQI: aqicn.org/data-platform/token

## 🧠 How It Works
- User enters city and health profile
- App fetches live AQI and weather data
- EPA formula calculates accurate AQI
- Claude AI generates personalized health advice
- Results shown in a dark dashboard UI

## 🗂️ Project Structure
aqi-agent/
├── main.py          # Streamlit UI
├── agent.py         # AI health recommendations
├── aqi_fetcher.py   # Fetches live AQI data
├── .env             # API keys (not committed)
├── .env.example     # Safe template for API keys
└── requirements.txt # Dependencies

Built as a learning project 
