import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Температурен помощник",
    page_icon="🌡️",
    layout="centered",
)

# ---------- Styling & animations ----------
st.markdown(
    """
    <style>
    .block-container { max-width: 720px; padding-top: 1.5rem; }
    #MainMenu, footer { visibility: hidden; }

    /* Animated gradient hero */
    .hero {
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 2.2rem 1rem;
        border-radius: 22px;
        color: white;
        margin-bottom: 1.2rem;
        background: linear-gradient(120deg, #4facfe, #8e54e9, #f857a6, #4facfe);
        background-size: 300% 300%;
        animation: gradientShift 10s ease infinite;
        box-shadow: 0 12px 34px rgba(142, 84, 233, 0.3);
    }
    .hero h1 { margin: 0; font-size: 2.2rem; color: white; }
    .hero p  { margin: .4rem 0 0; opacity: .92; }
    .hero .float {
        display: inline-block;
        font-size: 2.6rem;
        animation: float 3s ease-in-out infinite;
    }
    .hero::after {  /* soft shimmer sweep */
        content: "";
        position: absolute; top: 0; left: -60%;
        width: 40%; height: 100%;
        background: linear-gradient(100deg, transparent, rgba(255,255,255,.25), transparent);
        transform: skewX(-20deg);
        animation: shimmer 5s ease-in-out infinite;
    }

    /* Result card */
    .result-card {
        text-align: center;
        padding: 1.8rem 1rem 1.4rem;
        border-radius: 20px;
        margin-top: 1rem;
        border: 2px solid var(--accent);
        background: color-mix(in srgb, var(--accent) 14%, transparent);
        animation: popIn .45s cubic-bezier(.2,.9,.3,1.3);
    }
    .result-card .place { font-size: .95rem; opacity: .75; margin-bottom: .2rem; }
    .result-card .emoji { font-size: 3.6rem; line-height: 1; animation: bounce 1.8s ease-in-out infinite; }
    .result-card .temp  { font-size: 3rem; font-weight: 800; color: var(--accent); margin: .2rem 0; }
    .result-card .title { font-size: 1.3rem; font-weight: 700; }
    .result-card .tip   { opacity: .85; margin-top: .25rem; }

    .chips { display: flex; gap: .6rem; justify-content: center; flex-wrap: wrap; margin-top: 1rem; }
    .chip {
        padding: .35rem .8rem;
        border-radius: 999px;
        font-size: .85rem;
        background: color-mix(in srgb, var(--accent) 18%, transparent);
        animation: fadeUp .6s ease-out both;
    }
    .chip:nth-child(2) { animation-delay: .1s; }
    .chip:nth-child(3) { animation-delay: .2s; }
    .chip:nth-child(4) { animation-delay: .3s; }

    /* Hint banner */
    .hint {
        text-align: center;
        padding: .7rem 1rem;
        border-radius: 14px;
        margin: .6rem 0;
        background: rgba(142, 84, 233, .12);
        animation: pulseGlow 2.4s ease-in-out infinite;
    }

    /* Button */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: .7rem 1rem;
        font-weight: 700;
        border: none;
        color: white;
        background: linear-gradient(135deg, #4facfe, #8e54e9);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(142, 84, 233, .35);
        color: white;
    }

    /* Map frame */
    iframe[title="streamlit_folium.st_folium"] {
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,.18);
    }

    @keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    @keyframes float   { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
    @keyframes shimmer { 0%{left:-60%} 60%,100%{left:130%} }
    @keyframes popIn   { from{transform:scale(.88);opacity:0} to{transform:scale(1);opacity:1} }
    @keyframes bounce  { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
    @keyframes fadeUp  { from{transform:translateY(10px);opacity:0} to{transform:translateY(0);opacity:1} }
    @keyframes pulseGlow { 0%,100%{box-shadow:0 0 0 0 rgba(142,84,233,.35)} 50%{box-shadow:0 0 0 10px rgba(142,84,233,0)} }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="float">🌡️</div>
        <h1>Температурен помощник</h1>
        <p>Кликни върху картата или въведи градуси и разбери как да се облечеш</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Data ----------
# (upper limit, emoji, title, tip, color)
CATEGORIES = [
    (0, "🥶", "Мраз!", "Облечи зимно яке, шапка и ръкавици.", "#60a5fa"),
    (10, "🧣", "Студено е!", "Облечи топло яке.", "#3b82f6"),
    (20, "🧥", "Прохладно е.", "Подходящо е леко яке.", "#f59e0b"),
    (30, "😎", "Приятно топло е!", "Идеално време за разходка.", "#22c55e"),
    (float("inf"), "🥵", "Много е горещо!", "Пий повече вода и търси сянка.", "#ef4444"),
]

WEATHER_CODES = {
    0: "☀️ Ясно", 1: "🌤️ Предимно ясно", 2: "⛅ Частична облачност", 3: "☁️ Облачно",
    45: "🌫️ Мъгла", 48: "🌫️ Мъгла", 51: "🌦️ Ръмеж", 53: "🌦️ Ръмеж", 55: "🌦️ Ръмеж",
    61: "🌧️ Дъжд", 63: "🌧️ Дъжд", 65: "🌧️ Силен дъжд", 71: "🌨️ Сняг", 73: "🌨️ Сняг",
    75: "❄️ Силен сняг", 80: "🌦️ Превалявания", 81: "🌦️ Превалявания", 82: "⛈️ Поройни превалявания",
    95: "⛈️ Гръмотевична буря", 96: "⛈️ Буря с градушка", 99: "⛈️ Буря с градушка",
}


def category_for(temp: float):
    for limit, emoji, title, tip, color in CATEGORIES:
        if temp < limit:
            return emoji, title, tip, color


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(lat: float, lon: float):
    """Current weather from Open-Meteo (free, no API key)."""
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["current"]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_place_name(lat: float, lon: float) -> str:
    """Best-effort reverse geocoding via OpenStreetMap Nominatim."""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 10, "accept-language": "bg"},
            headers={"User-Agent": "temperature-helper-streamlit/1.0"},
            timeout=6,
        )
        addr = r.json().get("address", {})
        name = next(
            (addr[k] for k in ("city", "town", "village", "municipality", "county", "state") if k in addr),
            None,
        )
        country = addr.get("country")
        return ", ".join(p for p in (name, country) if p) or "Неизвестно място"
    except Exception:
        return "Неизвестно място"


def render_card(temp: float, place: str | None = None, chips: list[str] | None = None):
    emoji, title, tip, color = category_for(temp)
    place_html = f'<div class="place">📍 {place}</div>' if place else ""
    chips_html = ""
    if chips:
        chips_html = '<div class="chips">' + "".join(f'<span class="chip">{c}</span>' for c in chips) + "</div>"
    st.markdown(
        f"""
        <div class="result-card" style="--accent: {color};">
            {place_html}
            <div class="emoji">{emoji}</div>
            <div class="temp">{temp:g}°C</div>
            <div class="title">{title}</div>
            <div class="tip">{tip}</div>
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Tabs ----------
tab_map, tab_manual = st.tabs(["🗺️ Карта", "⌨️ Ръчно въвеждане"])

# ===== Map tab =====
with tab_map:
    if "point" not in st.session_state:
        st.session_state.point = None

    point = st.session_state.point
    center = [point["lat"], point["lng"]] if point else [45.0, 15.0]
    zoom = 6 if point else 4

    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron", control_scale=True)

    if point:
        pulse_icon = folium.DivIcon(
            html="""
            <style>
              .pulse{width:18px;height:18px;border-radius:50%;background:#8e54e9;border:3px solid #fff;
                     box-shadow:0 0 0 0 rgba(142,84,233,.7);animation:p 1.6s infinite;margin:-9px 0 0 -9px}
              @keyframes p{70%{box-shadow:0 0 0 18px rgba(142,84,233,0)}100%{box-shadow:0 0 0 0 rgba(142,84,233,0)}}
            </style>
            <div class="pulse"></div>
            """,
            icon_size=(0, 0),
        )
        folium.Marker([point["lat"], point["lng"]], icon=pulse_icon).add_to(m)

    if not point:
        st.markdown('<div class="hint">👆 Кликни където и да е по картата</div>', unsafe_allow_html=True)

    out = st_folium(m, height=430, use_container_width=True, returned_objects=["last_clicked"], key="map")

    clicked = out.get("last_clicked") if out else None
    if clicked and (not point or clicked["lat"] != point["lat"] or clicked["lng"] != point["lng"]):
        st.session_state.point = {"lat": clicked["lat"], "lng": clicked["lng"]}
        st.rerun()

    if point:
        lat, lon = point["lat"], point["lng"]
        try:
            with st.spinner("Взимам температурата..."):
                cur = fetch_weather(round(lat, 3), round(lon, 3))
                place = fetch_place_name(round(lat, 2), round(lon, 2))
            temp = float(cur["temperature_2m"])
            chips = [
                WEATHER_CODES.get(cur.get("weather_code"), "🌍 Времето"),
                f"🤒 Усеща се: {cur['apparent_temperature']:g}°C",
                f"💧 Влажност: {cur['relative_humidity_2m']}%",
                f"💨 Вятър: {cur['wind_speed_10m']:g} км/ч",
            ]
            render_card(temp, place=f"{place} ({lat:.2f}, {lon:.2f})", chips=chips)
        except Exception:
            st.error("Не успях да взема температурата. Провери интернет връзката и опитай пак.")

# ===== Manual tab =====
with tab_manual:
    temperature = st.number_input(
        "Температура в °C",
        min_value=-50.0,
        max_value=60.0,
        value=20.0,
        step=0.5,
    )
    st.progress((temperature + 50) / 110)
    c1, c2 = st.columns(2)
    c1.caption("❄️ -50°C")
    c2.markdown("<div style='text-align:right;opacity:.6;font-size:.85rem'>🔥 60°C</div>", unsafe_allow_html=True)

    if st.button("Провери"):
        render_card(temperature)
