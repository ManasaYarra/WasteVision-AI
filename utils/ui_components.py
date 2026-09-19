import streamlit as st
import streamlit.components.v1 as components


def inject_custom_css(theme="light"):
    """
    Inject custom CSS for modern green eco-friendly UI supporting
    both Light Mode and Dark Mode with high contrast and smooth transitions.
    """
    is_dark = (theme == "dark")

    if is_dark:
        bg_main = "#0F172A"       # Slate 900
        bg_card = "#1E293B"       # Slate 800
        bg_sidebar = "#1E293B"    # Slate 800
        border_color = "#334155"  # Slate 700
        text_primary = "#F8FAFC"  # Slate 50
        text_secondary = "#94A3B8"  # Slate 400
        hero_grad = "linear-gradient(135deg, #014D40 0%, #0D9488 50%, #14B8A6 100%)"
        pill_bg = "#334155"
        pill_text = "#E2E8F0"
        metric_val_color = "#34D399"  # Emerald 400
        card_hover_shadow = "rgba(0, 0, 0, 0.4)"
        input_bg = "#1E293B"
        input_border = "#475569"
    else:
        bg_main = "#F8FAFC"       # Slate 50
        bg_card = "#FFFFFF"
        bg_sidebar = "#FFFFFF"
        border_color = "#E2E8F0"  # Slate 200
        text_primary = "#0F172A"  # Slate 900
        text_secondary = "#334155"  # Slate 700
        hero_grad = "linear-gradient(135deg, #018749 0%, #10B981 50%, #34D399 100%)"
        pill_bg = "#E2E8F0"
        pill_text = "#0F172A"
        metric_val_color = "#047857"  # Emerald 700
        card_hover_shadow = "rgba(0, 0, 0, 0.08)"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* Global Theme Transitions */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }}

        .stApp {{
            background-color: {bg_main};
            color: {text_primary};
        }}

        /* Headings & Markdown Text */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
            color: {text_primary} !important;
        }}

        .stApp p, .stApp label, .stApp span, .stApp div {{
            color: {text_primary};
        }}

        /* Sidebar Theme */
        [data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
            border-right: 1px solid {border_color};
        }}

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
            color: {text_primary} !important;
        }}

        /* Sidebar navigation item styles */
        [data-testid="stSidebar"] .stRadio > label {{
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            transition: background-color 0.2s ease;
        }}
        [data-testid="stSidebar"] .stRadio > label:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        [data-testid="stSidebar"] .stRadio > label[aria-checked="true"],
        [data-testid="stSidebar"] .stRadio > label[data-selected="true"] {{
            background-color: rgba(0, 120, 80, 0.2);
        }}

        header[data-testid="stHeader"] {{
            background-color: {bg_main} !important;
        }}

        /* Hero Banner Styling */
        .hero-banner {{
            background: {hero_grad};
            color: #FFFFFF !important;
            padding: 3rem 2.5rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 12px 30px -6px rgba(10,120,80,0.35);
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .hero-banner * {{
            color: #FFFFFF !important;
        }}

        .hero-title {{
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
        }}

        .hero-subtitle {{
            font-size: 1.25rem;
            font-weight: 500;
            color: #D1FAE5 !important;
            margin-bottom: 1rem;
        }}

        .hero-tag {{
            display: inline-block;
            background-color: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 0.4rem 1.2rem;
            border-radius: 9999px;
            font-size: 0.9rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        /* Category Card Styling */
        .category-card {{
            background: {bg_card};
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid {border_color};
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.3s ease;
            height: 100%;
        }}

        .category-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px {card_hover_shadow};
        }}

        .category-icon {{
            font-size: 2.2rem;
            margin-bottom: 0.8rem;
        }}

        .category-name {{
            font-size: 1.2rem;
            font-weight: 700;
            color: {text_primary} !important;
            margin-bottom: 0.4rem;
        }}

        /* Result Card Styling */
        .result-card {{
            background: {bg_card};
            border-radius: 16px;
            padding: 2rem;
            border: 2px solid {border_color};
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }}

        .category-badge {{
            display: inline-block;
            padding: 0.4rem 1.2rem;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }}

        .confidence-pill {{
            display: inline-block;
            background-color: {pill_bg};
            color: {pill_text} !important;
            padding: 0.35rem 0.9rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-left: 0.5rem;
            border: 1px solid {border_color};
        }}

        /* Impact Metric Card */
        .metric-card {{
            background: {bg_card};
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid {border_color};
            text-align: center;
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.15);
            transition: background-color 0.3s ease, transform 0.2s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
        }}

        .metric-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: {metric_val_color} !important;
            line-height: 1.2;
        }}

        .metric-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: {text_secondary} !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.3rem;
        }}

        /* Buttons & Forms Theme Overrides */
        .stButton>button {{
            background: linear-gradient(90deg, #047857, #14B8A6);
            color: #FFFFFF !important;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            min-height: 2.5rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }}
        .stButton>button:hover {{
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }}

        .stSelectbox, .stTextInput, .stFileUploader, .stTextArea {{
            background-color: {input_bg};
            border-radius: 8px;
        }}

        div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text_primary} !important;
            border-color: {input_border} !important;
        }}

        input, textarea {{
            color: {text_primary} !important;
        }}

        /* Expanders Theme */
        .stExpander {{
            background-color: {bg_card} !important;
            border: 1px solid {border_color} !important;
            border-radius: 12px !important;
        }}

        .stExpander summary, .stExpander summary * {{
            color: {text_primary} !important;
        }}

        /* Tabs Theme */
        .stTabs [data-baseweb="tab-list"] {{
            border-bottom: 2px solid {border_color};
        }}

        .stTabs [data-baseweb="tab"] {{
            color: {text_secondary} !important;
            font-weight: 600;
        }}

        .stTabs [aria-selected="true"] {{
            color: #059669 !important;
            border-bottom: 3px solid #059669 !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_hero_banner():
    """Render top hero banner on home page."""
    html = """
    <div class="hero-banner">
        <div class="hero-tag">🌱 AI-Powered Recycling Companion</div>
        <div class="hero-title">WasteVision AI</div>
        <div class="hero-subtitle">Smart Waste Identification & Disposal Assistant</div>
        <div style="font-size: 1rem; opacity: 0.95;">"Snap it. Identify it. Dispose of it right."</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_result_badge(category, badge_color="#10B981", badge_bg="#D1FAE5", icon="♻️", is_dark=False):
    """Render colored category badge HTML with high contrast support for dark/light themes."""
    if is_dark:
        dark_badge_bg_map = {
            "#D1FAE5": "rgba(16, 185, 129, 0.25)",  # Recyclable
            "#ECFCCB": "rgba(132, 204, 22, 0.25)",  # Organic
            "#E0F2FE": "rgba(2, 132, 199, 0.25)",   # E-waste
            "#FFE4E6": "rgba(225, 29, 72, 0.25)",   # Hazardous
            "#F1F5F9": "rgba(100, 116, 139, 0.25)"  # General Waste
        }
        dark_badge_text_map = {
            "#10B981": "#34D399",
            "#84CC16": "#A3E635",
            "#0284C7": "#38BDF8",
            "#E11D48": "#FB7185",
            "#64748B": "#94A3B8"
        }
        bg = dark_badge_bg_map.get(badge_bg, "rgba(255, 255, 255, 0.15)")
        text_col = dark_badge_text_map.get(badge_color, "#F8FAFC")
        border_col = text_col
    else:
        # High contrast colors for Light Mode
        light_badge_text_map = {
            "#10B981": "#065F46",  # Dark emerald
            "#84CC16": "#3F6212",  # Dark lime
            "#0284C7": "#075985",  # Dark sky blue
            "#E11D48": "#9F1239",  # Dark rose red
            "#64748B": "#334155"   # Dark slate
        }
        bg = badge_bg
        text_col = light_badge_text_map.get(badge_color, "#0F172A")
        border_col = text_col

    return f"""
    <span class="category-badge" style="background-color: {bg}; color: {text_col}; border: 1px solid {border_col}; font-weight: 700;">
        {icon} {category}
    </span>
    """


def render_metric_card(label, value, icon=""):
    """Render clean metric card HTML."""
    html = f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.2rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_geolocation_button():
    """
    Renders an HTML/JS Geolocation trigger button that requests navigator.geolocation.getCurrentPosition.
    Updates Streamlit query parameters with actual latitude/longitude or 'denied' error state.
    """
    html_code = """
    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
        <button id="geo-btn" onclick="requestGeoLocation()" style="
            background-color: #059669;
            color: white;
            border: none;
            padding: 0.55rem 1.1rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            🎯 Detect My Real Location
        </button>
        <div id="geo-status-msg" style="margin-top: 0.35rem; font-size: 0.82rem; text-align: center;"></div>

        <script>
        function requestGeoLocation() {
            const btn = document.getElementById("geo-btn");
            const statusDiv = document.getElementById("geo-status-msg");
            btn.innerText = "Requesting browser GPS permission...";
            btn.disabled = true;

            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude.toFixed(4);
                        const lon = position.coords.longitude.toFixed(4);
                        statusDiv.style.color = "#059669";
                        statusDiv.innerText = "GPS Location captured (" + lat + ", " + lon + ")! Updating...";

                        try {
                            const parentUrl = new URL(window.parent.location.href);
                            parentUrl.searchParams.set("user_lat", lat);
                            parentUrl.searchParams.set("user_lon", lon);
                            parentUrl.searchParams.set("geo_status", "success");
                            window.parent.location.href = parentUrl.href;
                        } catch(e) {
                            console.error(e);
                        }
                    },
                    function(error) {
                        statusDiv.style.color = "#E11D48";
                        let msg = "Location access denied.";
                        if (error.code === error.PERMISSION_DENIED) {
                            msg = "Location permission denied by user.";
                        } else if (error.code === error.POSITION_UNAVAILABLE) {
                            msg = "Location position unavailable.";
                        } else if (error.code === error.TIMEOUT) {
                            msg = "Location request timed out.";
                        }
                        statusDiv.innerText = "Warning: " + msg;
                        btn.innerText = "Retry GPS Location Access";
                        btn.disabled = false;

                        try {
                            const parentUrl = new URL(window.parent.location.href);
                            parentUrl.searchParams.set("geo_status", "denied");
                            window.parent.location.href = parentUrl.href;
                        } catch(e) {}
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            } else {
                statusDiv.style.color = "#E11D48";
                statusDiv.innerText = "Geolocation is not supported by your browser.";
                btn.innerText = "Geolocation Unsupported";
            }
        }
        </script>
    </div>
    """
    components.html(html_code, height=75)
