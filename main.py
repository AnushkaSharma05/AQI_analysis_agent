import os
from typing import Dict, Any, List

import streamlit as st
from dotenv import load_dotenv

from agent import get_health_recommendation
from aqi_fetcher import fetch_aqi_data


GAUGE_TEMPLATE = """
<div style="background: rgba(255,255,255,0.03); border-radius: 20px; padding: 24px; text-align: center;">
    <svg width="240" height="240" viewBox="0 0 240 240" style="display: block; margin: 0 auto;">
        <circle cx="120" cy="120" r="{radius}" stroke="rgba(255,255,255,0.08)" stroke-width="16" fill="none" />
        <circle cx="120" cy="120" r="{radius}" stroke="{ring_color}" stroke-width="16" fill="none"
            stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}"
            transform="rotate(-90 120 120)" />
        <text x="120" y="125" text-anchor="middle" fill="{ring_color}" font-size="52" font-family="Syne, sans-serif" font-weight="700">{aqi_value}</text>
        <text x="120" y="155" text-anchor="middle" fill="{ring_color}" font-size="14" letter-spacing="2" font-family="Syne, sans-serif">{label_text}</text>
    </svg>
</div>
"""

HEALTH_BRIEF_TEMPLATE = """
<div style="background: rgba(255,255,255,0.03); border-left: 4px solid {accent_color}; padding: 20px; border-radius: 16px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="width: 10px; height: 10px; border-radius: 50%; background: #3df5a0; box-shadow: 0 0 12px #3df5a0; animation: pulse 1.6s infinite;"></span>
        <span style="font-family: Syne, sans-serif; font-size: 16px; letter-spacing: 1px;">AI Health Brief</span>
    </div>
    <span style="background: {risk_color}; color: #0b0f1a; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700;">{risk_text}</span>
    <p style="margin-top: 12px; color: #d0d8e8;">{outside_text} | {time_text} | {warning_text}</p>
    <div style="margin-top: 12px;">{chip_html}</div>
</div>
"""

LEGEND_HTML = """
<div style="display: flex; gap: 8px; margin-top: 18px; flex-wrap: wrap;">
    <div style="flex: 1; background: rgba(61,245,160,0.12); padding: 8px; border-radius: 10px; text-align: center; color: #3df5a0;">0-50 Good</div>
    <div style="flex: 1; background: rgba(255,230,0,0.12); padding: 8px; border-radius: 10px; text-align: center; color: #ffe600;">51-100 Moderate</div>
    <div style="flex: 1; background: rgba(249,168,37,0.12); padding: 8px; border-radius: 10px; text-align: center; color: #f9a825;">101-150 Sensitive</div>
    <div style="flex: 1; background: rgba(255,107,53,0.12); padding: 8px; border-radius: 10px; text-align: center; color: #ff6b35;">151-200 Unhealthy</div>
    <div style="flex: 1; background: rgba(180,0,255,0.12); padding: 8px; border-radius: 10px; text-align: center; color: #b400ff;">201-300 Very Bad</div>
    <div style="flex: 1; background: rgba(255,7,58,0.12); padding: 8px; border-radius: 10px; text-align: center; color: #ff073a;">301+ Hazardous</div>
</div>
"""

RECOMMENDATION_TEMPLATE = """
<div style="background:rgba(255,255,255,0.03);
            border-left: 4px solid {color};
            border-radius:14px;padding:20px;
            font-family:'DM Sans',sans-serif;">
    <div style="display:flex;justify-content:space-between;
                align-items:center;margin-bottom:14px;">
        <span style="color:#5a7aaa;font-size:12px;
                     letter-spacing:2px;">AI HEALTH BRIEF</span>
        <span style="background:rgba(255,255,255,0.05);
                     border:1px solid {color};color:{color};
                     padding:3px 12px;border-radius:20px;
                     font-size:12px;">{risk} Risk</span>
    </div>
    <p style="color:#aaa;font-size:13px;margin:0 0 4px;">
        <strong style="color:#fff;">Go outside?</strong>
        {outside}
    </p>
    <p style="color:#aaa;font-size:13px;margin:0 0 4px;">
        <strong style="color:#fff;">Best time:</strong>
        {best_time}
    </p>
    <p style="color:#aaa;font-size:13px;margin:0 0 12px;">
        <strong style="color:#fff;">Warning:</strong>
        {warning}
    </p>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.04);
                     border:1px solid rgba(255,255,255,0.08);
                     border-radius:20px;padding:4px 12px;
                     font-size:11px;color:#5a7aaa;">
            {measure1}
        </span>
        <span style="background:rgba(255,255,255,0.04);
                     border:1px solid rgba(255,255,255,0.08);
                     border-radius:20px;padding:4px 12px;
                     font-size:11px;color:#5a7aaa;">
            {measure2}
        </span>
        <span style="background:rgba(255,255,255,0.04);
                     border:1px solid rgba(255,255,255,0.08);
                     border-radius:20px;padding:4px 12px;
                     font-size:11px;color:#5a7aaa;">
            {measure3}
        </span>
    </div>
</div>
"""

CSS_TEXT = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: #080c14; }
[data-testid="stSidebar"] {
    background: #0c1020;
    border-right: 1px solid rgba(255,255,255,0.05);
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #d0d8e8;
}
.stTextInput input, .stSelectbox select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #c0cce0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #1a6fff, #0aafff) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 16px;
}
@keyframes pulse {
    0% { transform: scale(1); opacity: 0.6; }
    50% { transform: scale(1.3); opacity: 1; }
    100% { transform: scale(1); opacity: 0.6; }
}
</style>
"""


# Load environment variables for Streamlit runtime.
def load_environment() -> None:
    load_dotenv()


# Determine the color and label for the AQI value.
def get_aqi_label_and_color(aqi_value: int) -> Dict[str, str]:
    if aqi_value <= 50:
        return {"label": "GOOD", "color": "#3df5a0"}
    if aqi_value <= 100:
        return {"label": "MODERATE", "color": "#ffe600"}
    if aqi_value <= 150:
        return {"label": "SENSITIVE", "color": "#f9a825"}
    if aqi_value <= 200:
        return {"label": "UNHEALTHY", "color": "#ff6b35"}
    if aqi_value <= 300:
        return {"label": "VERY BAD", "color": "#b400ff"}
    return {"label": "HAZARDOUS", "color": "#ff073a"}


# Convert a raw AQI string into a safe integer.
def parse_aqi_value(raw_value: Any) -> int:
    return parse_numeric_value(raw_value)


# Convert a raw metric value into a safe integer.
def parse_numeric_value(raw_value: Any) -> int:
    try:
        cleaned = str(raw_value).replace("%", "").strip()
        return int(float(cleaned))
    except (TypeError, ValueError):
        return 0


# Build the SVG gauge HTML for the AQI value.
def build_aqi_gauge_svg(aqi_value: int) -> str:
        gauge_values = build_gauge_ring_values(aqi_value)
        return build_gauge_svg_html(aqi_value, gauge_values)


# Build the circle math and color values for the AQI gauge.
def build_gauge_ring_values(aqi_value: int) -> Dict[str, Any]:
        label_info = get_aqi_label_and_color(aqi_value)
        max_aqi = 300
        clamped_value = min(aqi_value, max_aqi)
        radius = 90
        circumference = 2 * 3.1416 * radius
        fill_ratio = clamped_value / max_aqi
        dash_offset = circumference * (1 - fill_ratio)

        return {
                "ring_color": label_info["color"],
                "label_text": label_info["label"],
                "radius": radius,
                "circumference": circumference,
                "dash_offset": dash_offset,
        }


# Build the SVG markup for the AQI gauge using prepared values.
def build_gauge_svg_html(aqi_value: int, values: Dict[str, Any]) -> str:
        ring_color = values["ring_color"]
        label_text = values["label_text"]
        radius = values["radius"]
        circumference = values["circumference"]
        dash_offset = values["dash_offset"]
        return GAUGE_TEMPLATE.format(
                radius=radius,
                ring_color=ring_color,
                circumference=circumference,
                dash_offset=dash_offset,
                aqi_value=aqi_value,
                label_text=label_text,
        )


# Build a small HTML progress bar for a metric card.
def build_progress_bar(value: int, max_value: int, color: str) -> str:
    safe_value = min(max(value, 0), max_value)
    width_percent = int((safe_value / max_value) * 100)
    bar_html = f"""
    <div style="background: rgba(255,255,255,0.06); border-radius: 12px; height: 8px;">
      <div style="width: {width_percent}%; background: {color}; height: 8px; border-radius: 12px;"></div>
    </div>
    """
    return bar_html


# Parse the agent response into a simple key-value dictionary.
def parse_recommendation(text: str) -> Dict[str, str]:
    # reads each line and builds a dictionary
    result = {}
    for line in text.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


# Turn text into a list of non-empty lines.
def get_non_empty_lines(text: str) -> List[str]:
    lines = []
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line:
            lines.append(clean_line)
    return lines


# Pull a fixed number of bullet-style lines into a list.
def extract_measures(lines: List[str], start_index: int, count: int) -> List[str]:
    measures = []
    end_index = min(start_index + count, len(lines))
    index = start_index

    while index < end_index:
        measures.append(lines[index].lstrip("- "))
        index += 1

    return measures


# Pick a badge color based on the risk text.
def get_risk_badge_color(risk_text: str) -> str:
    lower_text = risk_text.lower()
    if "low" in lower_text:
        return "#3df5a0"
    if "moderate" in lower_text:
        return "#f9a825"
    if "high" in lower_text:
        return "#ff6b35"
    return "#ff073a"


# Display a styled error card in the main panel.
def render_error_card(message: str) -> None:
    card_html = f"""
    <div style="background: rgba(255,7,58,0.12); border: 1px solid rgba(255,7,58,0.25); padding: 18px; border-radius: 14px; color: #ff9fb3;">
      {message}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# Display a styled info card in the main panel.
def render_info_card(message: str) -> None:
    card_html = f"""
    <div style="background: rgba(61,245,160,0.08); border: 1px solid rgba(61,245,160,0.2); padding: 18px; border-radius: 14px; color: #b7f5d9;">
      {message}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# Render the AI health brief card using the clean response format.
def render_health_brief(recommendation_text: str) -> None:
    rec = parse_recommendation(recommendation_text)
    risk_colors = {
        "Low": "#3df5a0",
        "Moderate": "#ffe600",
        "High": "#ff6b35",
        "Very High": "#ff073a",
    }
    risk = rec.get("RISK", "Unknown")
    color = risk_colors.get(risk, "#888")
    st.markdown(build_recommendation_html(rec, risk, color), unsafe_allow_html=True)


# Build the HTML block for the clean recommendation card.
def build_recommendation_html(rec: Dict[str, str], risk: str, color: str) -> str:
    return RECOMMENDATION_TEMPLATE.format(
        color=color,
        risk=risk,
        outside=rec.get("OUTSIDE", "?"),
        best_time=rec.get("BEST_TIME", "?"),
        warning=rec.get("WARNING", "None"),
        measure1=rec.get("MEASURE1", ""),
        measure2=rec.get("MEASURE2", ""),
        measure3=rec.get("MEASURE3", ""),
    )


# Build the HTML for chips representing protective measures.
def build_chip_html(chips: List[str]) -> str:
        html_parts = []
        for chip in chips:
                html_parts.append(
                        "<span style=\"background: rgba(255,255,255,0.08); padding: 6px 10px; border-radius: 999px; margin-right: 8px; font-size: 12px;\">"
                        + chip
                        + "</span>"
                )
        return "".join(html_parts)


# Build the HTML for the AI health brief card.
def build_health_brief_html(parsed: Dict[str, Any], accent_color: str) -> str:
        risk_color = get_risk_badge_color(parsed.get("risk", ""))
        chips = parsed.get("measures", [])
        chip_html = build_chip_html(chips)
        return HEALTH_BRIEF_TEMPLATE.format(
                accent_color=accent_color,
                risk_color=risk_color,
                risk_text=parsed.get("risk"),
                outside_text=parsed.get("outside"),
                time_text=parsed.get("time"),
                warning_text=parsed.get("warning"),
                chip_html=chip_html,
        )


# Render the AQI legend bar with six colored segments.
def render_aqi_legend() -> None:
        st.markdown(LEGEND_HTML, unsafe_allow_html=True)


# Inject the custom CSS styles into the Streamlit app.
def inject_custom_css() -> None:
        css_text = get_css_text()
        st.markdown(css_text, unsafe_allow_html=True)


# Return the custom CSS used for the dark UI theme.
def get_css_text() -> str:
        return CSS_TEXT


# Show the sidebar inputs and return user selections.
def render_sidebar() -> Dict[str, Any]:
    render_sidebar_title()
    return collect_sidebar_inputs()


# Render the sidebar title text.
def render_sidebar_title() -> None:
    st.sidebar.markdown(
        '<div style="font-family: Syne, sans-serif; font-size: 28px; font-weight: 700; margin-bottom: 16px;">AQI Agent</div>',
        unsafe_allow_html=True,
    )


# Collect sidebar input widgets and return user selections.
def collect_sidebar_inputs() -> Dict[str, Any]:
    city_name = st.sidebar.text_input("City", value="Delhi")
    medical_conditions = st.sidebar.multiselect(
        "Medical Conditions",
        options=["None", "Asthma", "Heart Disease", "Pregnant", "Elderly", "Child"],
        default=["None"],
    )
    activity = st.sidebar.selectbox(
        "Activity",
        options=["Walking", "Running", "Cycling", "Outdoor Work", "Indoor Only"],
    )
    analyze_clicked = st.sidebar.button("Analyze Air Quality")

    return {
        "city": city_name,
        "medical_conditions": medical_conditions,
        "activity": activity,
        "analyze_clicked": analyze_clicked,
    }


# Render the metric cards row with progress bars.
def render_metric_cards(aqi_data: Dict[str, Any]) -> None:
    metrics = get_metric_values(aqi_data)
    columns = st.columns(4)

    render_metric_column(columns[0], "PM2.5", metrics["pm25"], 200, metrics["pm25_color"])
    render_metric_column(columns[1], "PM10", metrics["pm10"], 300, metrics["pm10_color"])
    render_metric_column(columns[2], "Humidity", f"{metrics['humidity']}%", 100, metrics["humidity_color"])
    render_metric_column(columns[3], "Wind Speed", metrics["wind"], 100, metrics["wind_color"])


# Convert AQI data into metric values and colors for display.
def get_metric_values(aqi_data: Dict[str, Any]) -> Dict[str, Any]:
    pm25_value = parse_numeric_value(aqi_data.get("pm25", 0) or 0)
    pm10_value = parse_numeric_value(aqi_data.get("pm10", 0) or 0)
    humidity_value = parse_numeric_value(aqi_data.get("humidity", 0) or 0)
    wind_value = parse_numeric_value(aqi_data.get("wind_speed", 0) or 0)

    return {
        "pm25": pm25_value,
        "pm10": pm10_value,
        "humidity": humidity_value,
        "wind": wind_value,
        "pm25_color": "#f9a825" if pm25_value > 35 else "#3df5a0",
        "pm10_color": "#ff6b35" if pm10_value > 50 else "#3df5a0",
        "humidity_color": "#0aafff",
        "wind_color": "#3df5a0",
    }


# Render a single metric column with its progress bar.
def render_metric_column(column: Any, label: str, value: Any, max_value: int, color: str) -> None:
    with column:
        st.metric(label, value)
        st.markdown(build_progress_bar(parse_numeric_value(value), max_value, color), unsafe_allow_html=True)


# Run the Streamlit app layout and behavior.
def main() -> None:
    print("Starting AQI Agent UI...")
    load_environment()
    inject_custom_css()
    user_inputs = render_sidebar()

    if not user_inputs["analyze_clicked"]:
        show_intro_message()
        return

    if missing_api_keys():
        render_info_card("Missing API keys. Please add OPENWEATHER_API_KEY and OPENROUTER_API_KEY in your .env file.")
        return

    city = user_inputs["city"]
    aqi_data = fetch_aqi_with_spinner(city)

    # Check if city name is too short to be real
    if len(city.strip()) < 3:
        st.error("Please enter a valid city name (at least 3 characters)")
        st.stop()

    # Check if the API returned an error
    if "error" in aqi_data:
        st.error(f"City not found: {aqi_data['error']}")
        st.stop()

    # Check if all values are suspiciously zero or very low
    if aqi_data["pm25"] == 0 and aqi_data["pm10"] == 0:
        st.error("Could not get real data for this city. Please try a different city name.")
        st.stop()

    if aqi_data["aqi"] == 0:
        st.warning("AQI data unavailable for this city, try again")
        st.stop()

    if aqi_data["pm25"] == 0 and aqi_data["pm10"] == 0:
        st.warning("Pollution sensors offline for this city")
        st.stop()

    if aqi_data["temperature"] == 0:
        st.warning("Weather data incomplete for this city")

    agent_text = run_agent_with_spinner(
        aqi_data,
        user_inputs["medical_conditions"],
        user_inputs["activity"],
    )
    render_results(aqi_data, agent_text)


# Show the intro card when the user has not started analysis yet.
def show_intro_message() -> None:
    print("Waiting for user input...")
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    render_info_card("Enter a city and press Analyze Air Quality to begin.")


# Check if the required API keys are missing.
def missing_api_keys() -> bool:
    is_missing = not os.getenv("OPENWEATHER_API_KEY") or not os.getenv("OPENROUTER_API_KEY")
    if is_missing:
        print("API keys are missing in the .env file.")
    return is_missing


# Fetch AQI data while showing the loading spinner.
def fetch_aqi_with_spinner(city_name: str) -> Dict[str, Any]:
    print("Fetching AQI data from OpenWeather...")
    with st.spinner("Scanning atmosphere..."):
        return fetch_aqi_data(city_name)


# Run the agent call while showing the loading spinner.
def run_agent_with_spinner(
    aqi_data: Dict[str, Any],
    medical_conditions: List[str],
    activity: str,
) -> str:
    print("Requesting AI health brief...")
    with st.spinner("Agent analyzing..."):
        return get_health_recommendation(aqi_data, medical_conditions, activity)


# Render all results after the agent response is ready.
def render_results(aqi_data: Dict[str, Any], agent_text: str) -> None:
    print("Rendering UI results...")
    aqi_value = parse_aqi_value(aqi_data.get("aqi"))

    st.markdown(build_aqi_gauge_svg(aqi_value), unsafe_allow_html=True)
    if aqi_data["aqi"] < 50:
        st.caption("✅ High confidence reading")
    elif aqi_data["aqi"] < 150:
        st.caption("⚠️ Moderate confidence reading")
    else:
        st.caption("⚠️ High pollution — reading may vary ±15%")
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    render_metric_cards(aqi_data)
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    render_health_brief(agent_text)
    render_aqi_legend()


if __name__ == "__main__":
    main()
