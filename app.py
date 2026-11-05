import streamlit as st
 
st.set_page_config(
    page_title="Температурен помощник",
    page_icon="🌡️",
    layout="centered",
)
 
# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container { max-width: 640px; padding-top: 2rem; }
 
    .hero {
        text-align: center;
        padding: 2rem 1rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #4facfe 0%, #8e54e9 100%);
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.25);
    }
    .hero h1 { margin: 0; font-size: 2.2rem; color: white; }
    .hero p  { margin: .4rem 0 0; opacity: .9; }
 
    .result-card {
        text-align: center;
        padding: 1.8rem 1rem;
        border-radius: 18px;
        margin-top: 1.2rem;
        border: 2px solid var(--accent);
        background: color-mix(in srgb, var(--accent) 14%, transparent);
        animation: pop .35s ease-out;
    }
    .result-card .emoji { font-size: 3.5rem; line-height: 1; }
    .result-card .temp  { font-size: 2.6rem; font-weight: 800; color: var(--accent); margin: .3rem 0; }
    .result-card .title { font-size: 1.3rem; font-weight: 700; }
    .result-card .tip   { opacity: .85; margin-top: .3rem; }
 
    @keyframes pop {
        from { transform: scale(.92); opacity: 0; }
        to   { transform: scale(1);   opacity: 1; }
    }
 
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: .7rem 1rem;
        font-weight: 700;
        font-size: 1.05rem;
        border: none;
        color: white;
        background: linear-gradient(135deg, #4facfe 0%, #8e54e9 100%);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(142, 84, 233, 0.35);
        color: white;
    }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
        <h1>🌡️ Температурен помощник</h1>
        <p>Въведи температурата и разбери как да се облечеш</p>
    </div>
    """,
    unsafe_allow_html=True,
)
 
# ---------- Input ----------
temperature = st.number_input(
    "Температура в °C",
    min_value=-50.0,
    max_value=60.0,
    value=20.0,
    step=0.5,
)
 
# Visual scale from -50 to 60
st.progress((temperature + 50) / 110)
col1, col2 = st.columns(2)
col1.caption("❄️ -50°C")
col2.markdown("<div style='text-align:right; opacity:.6; font-size:.85rem'>🔥 60°C</div>", unsafe_allow_html=True)
 
# ---------- Categories: (upper limit, emoji, title, tip, color) ----------
CATEGORIES = [
    (10, "🥶", "Студено е!", "Облечи топло яке.", "#3b82f6"),
    (20, "🧥", "Прохладно е.", "Подходящо е леко яке.", "#f59e0b"),
    (30, "😎", "Приятно топло е!", "Идеално време за разходка.", "#22c55e"),
    (float("inf"), "🥵", "Много е горещо!", "Пий повече вода.", "#ef4444"),
]
 
# ---------- Result ----------
if st.button("Провери"):
    for limit, emoji, title, tip, color in CATEGORIES:
        if temperature < limit:
            st.markdown(
                f"""
                <div class="result-card" style="--accent: {color};">
                    <div class="emoji">{emoji}</div>
                    <div class="temp">{temperature:g}°C</div>
                    <div class="title">{title}</div>
                    <div class="tip">{tip}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            break

