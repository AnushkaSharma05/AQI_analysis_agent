import os
from typing import Dict, Any, List

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from the .env file.
def load_environment() -> None:
    load_dotenv()


# Build the OpenRouter client using the OpenAI SDK.
def create_openrouter_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")


# Build the cleaner prompt for the UI-friendly response format.
def build_clean_prompt(aqi_data: Dict[str, Any], medical_conditions: List[str], activity: str) -> str:
    return f"""
You are an air quality health advisor.

Air Quality in {aqi_data['city']} ({aqi_data.get('time_of_day', 'now')}):
- AQI: {aqi_data['aqi']}
- PM2.5: {aqi_data['pm25']} µg/m³
- PM10: {aqi_data['pm10']} µg/m³
- Temperature: {aqi_data['temperature']}°C
- Humidity: {aqi_data['humidity']}%

User has: {medical_conditions}
Wants to: {activity}

Reply in EXACTLY this format, nothing else:

RISK: Low
OUTSIDE: Yes
MEASURE1: Carry a water bottle
MEASURE2: Wear sunscreen
MEASURE3: Take breaks if tired
BEST_TIME: Early morning or evening
WARNING: None specific for current conditions
"""


# Send the prompt to OpenRouter and return the raw response object.
def send_openrouter_request(client: OpenAI, prompt_text: str) -> Any:
    return client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.4,
        max_tokens=400,
    )


# Extract the response text from the OpenRouter response.
def extract_response_text(response: Any) -> str:
    return response.choices[0].message.content


# Ask Claude for a health recommendation and return the response text.
def get_health_recommendation(
    aqi_data: Dict[str, Any],
    medical_conditions: List[str],
    activity: str,
) -> str:
    print("Loading environment for OpenRouter...")
    load_environment()
    client = create_openrouter_client()
    prompt_text = build_clean_prompt(aqi_data, medical_conditions, activity)

    print("Sending request to Claude through OpenRouter...")
    response = send_openrouter_request(client, prompt_text)

    print("Response received from Claude.")
    return extract_response_text(response)
