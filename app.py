import os
import sys
import json
import dotenv
import requests
from pathlib import Path
from PIL import Image
import pandas as pd
import altair as alt
import streamlit as st
from streamlit_js_eval import get_geolocation

# Base Directory path resolution
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def reverse_geocode(lat, lon):
    """Convert GPS coordinates into a readable address using OpenStreetMap Nominatim (free, no API key)."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json"}
        headers = {"User-Agent": "WasteVisionAI-Hackathon-App"}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get("display_name")
            if address:
                return address
    except Exception:
        pass
    return f"Lat: {lat}, Lon: {lon}"

# Load environment variables
dotenv.load_dotenv()

from utils.ui_components import (
    inject_custom_css,
    render_hero_banner,
    render_result_badge,
    render_metric_card,
    render_geolocation_button
)
from services.waste_analyzer import analyze_waste, calculate_urgency
from services.database import WasteDatabase
from services.geolocation_service import GeolocationService

# Initialize SQLite database & Geolocation service
db = WasteDatabase()
geo_service = GeolocationService()

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="WasteVision AI - Smart Waste Identification & Disposal",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "🏠 Home"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "target_disposal_category" not in st.session_state:
    st.session_state.target_disposal_category = None

# Sidebar Navigation Header
st.sidebar.image("https://img.icons8.com/isometric-folders/100/recycle.png", width=70)
st.sidebar.title("♻️ WasteVision AI")
st.sidebar.caption("Smart Identification & Disposal")

# Theme Mode Toggle Switch
st.sidebar.markdown("##### 🎨 Display Theme")
theme_choice = st.sidebar.radio(
    "Theme Mode",
    ["☀️ Light", "🌙 Dark"],
    index=0 if st.session_state.theme == "light" else 1,
    horizontal=True,
    key="theme_radio_switch",
    label_visibility="collapsed"
)

selected_theme_mode = "dark" if "Dark" in theme_choice else "light"
if selected_theme_mode != st.session_state.theme:
    st.session_state.theme = selected_theme_mode
    st.rerun()

# Inject Theme-specific CSS styling
inject_custom_css(theme=st.session_state.theme)

# Primary Navigation Options
nav_options = [
    "🏠 Home",
    "🔍 Analyze Waste",
    "📊 AI Result",
    "📖 Disposal Guide",
    "📢 Report Public Waste",
    "🏛️ Municipal Dashboard",
    "📍 Nearby Facilities",
    "🌱 My Impact"
]

selected_tab = st.sidebar.radio("Navigation", nav_options, index=nav_options.index(st.session_state.selected_tab))
st.session_state.selected_tab = selected_tab

# Settings access in top-right corner of main page
if "show_advanced_settings" not in st.session_state:
    st.session_state.show_advanced_settings = False

# Render a right-aligned settings icon using columns
col1, col2 = st.columns([10, 1])
with col2:
    if st.button("⚙️", key="settings_modal"):
        st.session_state.show_advanced_settings = not st.session_state.show_advanced_settings

if st.session_state.show_advanced_settings:
    with st.expander("Advanced Settings", expanded=True):
        gemini_key_input = st.text_input(
            "Google Gemini Vision API Key",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", ""),
            help="Optional API key for cloud vision AI. If left empty, local fallback engine is used."
        )
        if gemini_key_input:
            os.environ["GEMINI_API_KEY"] = gemini_key_input

        st.caption("🔒 Secrets are stored securely in session environment and never logged.")

# -----------------------------------------------------------------------------
# PAGE 1: HOME
# -----------------------------------------------------------------------------
if st.session_state.selected_tab == "🏠 Home":
    render_hero_banner()

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("📤 Upload Waste Image", use_container_width=True, type="primary"):
            st.session_state.selected_tab = "🔍 Analyze Waste"
            st.rerun()
    with col2:
        if st.button("📢 Report Public Dump", use_container_width=True):
            st.session_state.selected_tab = "📢 Report Public Waste"
            st.rerun()
    with col3:
        if st.button("📖 View Disposal Guide", use_container_width=True):
            st.session_state.target_disposal_category = None
            st.session_state.selected_tab = "📖 Disposal Guide"
            st.rerun()
    with col4:
        if st.button("📍 Find Drop-Off Points", use_container_width=True):
            st.session_state.selected_tab = "📍 Nearby Facilities"
            st.rerun()

    st.markdown("---")

    st.subheader("💡 How WasteVision AI Works")
    step_col1, step_col2, step_col3 = st.columns(3)

    with step_col1:
        st.markdown("""
        ### 1. 📷 Snap or Upload
        Capture a photo using your laptop webcam or upload an image file of any waste item (plastic bottle, paper, charger, food scrap).
        """)
    with step_col2:
        st.markdown("""
        ### 2. 🤖 Automatic AI Identification
        Our Computer Vision engine automatically identifies the waste item and categorizes it into Recyclable, Organic, E-waste, Hazardous, or General Waste.
        """)
    with step_col3:
        st.markdown("""
        ### 3. ♻️ Smart Disposal Guidance
        Receive instant disposal steps, safety tips, and locate certified nearby drop-off facilities or report public waste dumps.
        """)

    st.markdown("---")

    st.subheader("🏷️ Waste Classification Categories")
    cat_col1, cat_col2, cat_col3, cat_col4, cat_col5 = st.columns(5)

    categories_data = [
        ("Recyclable", "♻️", "#10B981", "#D1FAE5", "Plastics, Cardboard, Glass, Metals"),
        ("Organic", "🍎", "#84CC16", "#ECFCCB", "Food scraps, Garden waste, Peels"),
        ("E-waste", "🔌", "#0284C7", "#E0F2FE", "Phones, Cables, Chargers, Circuits"),
        ("Hazardous", "☣️", "#E11D48", "#FFE4E6", "Batteries, Chemicals, Paint cans"),
        ("General Waste", "🗑️", "#64748B", "#F1F5F9", "Non-recyclable wrappers, Styrofoam")
    ]

    cols = [cat_col1, cat_col2, cat_col3, cat_col4, cat_col5]
    for idx, (cat_name, icon, color, bg, desc) in enumerate(categories_data):
        with cols[idx]:
            st.markdown(f"""
            <div class="category-card" style="border-top: 4px solid {color};">
                <div class="category-icon">{icon}</div>
                <div class="category-name">{cat_name}</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🌍 Why Waste Sorting Matters")
    imp_col1, imp_col2 = st.columns(2)

    with imp_col1:
        st.markdown("""
        > **Did You Know?**
        > * Over **2.01 billion tonnes** of municipal solid waste are generated globally every year.
        > * Proper recycling of a single aluminum can saves enough energy to run a TV for 3 hours!
        > * Diverting organic waste into compost cuts methane emissions from landfills by over **60%**.
        """)

    with imp_col2:
        st.success("""
        🌱 **Our Hackathon Mission**

        WasteVision AI empowers everyday citizens to make split-second, zero-guesswork recycling choices and report public waste dumps directly from their web browser.
        """)

# -----------------------------------------------------------------------------
# PAGE 2: ANALYZE WASTE
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "🔍 Analyze Waste":
    st.title("🔍 Analyze Waste Image")
    st.caption("Upload an image file or capture a photo using your webcam for automatic AI waste identification.")

    upload_mode = st.radio("Choose Input Method:", ["📤 File Upload", "📷 Camera Capture"], horizontal=True)

    input_image = None

    if upload_mode == "📤 File Upload":
        uploaded_file = st.file_uploader("Upload waste image (JPG, PNG, WEBP)...", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file is not None:
            try:
                input_image = Image.open(uploaded_file).convert("RGB")
            except Exception as e:
                st.error(f"Error opening uploaded image: {e}")

    elif upload_mode == "📷 Camera Capture":
        st.info("📷 **Webcam Capture**: Please allow browser camera access when prompted. Position the item in front of your camera.")
        camera_file = st.camera_input("Take a photo of the waste item", key="webcam_capture_component")
        if camera_file is not None:
            try:
                input_image = Image.open(camera_file).convert("RGB")
            except Exception as e:
                st.error(f"Error capturing image from camera: {e}")

    if input_image is not None:
        st.session_state.current_image = input_image
        st.markdown("### Image Preview")

        prev_col, btn_col = st.columns([1, 1])
        with prev_col:
            st.image(input_image, caption="Captured / Uploaded Waste Photo", use_container_width=True)
            if st.button("🔄 Retake / Change Photo"):
                st.session_state.current_image = None
                st.session_state.analysis_result = None
                st.rerun()

        with btn_col:
            st.success("Image loaded! Click below to identify the waste item automatically.")
            if st.button("🚀 Analyze Waste Item", type="primary", use_container_width=True):
                with st.spinner("🧠 AI is identifying object characteristics and waste category..."):
                    result = analyze_waste(input_image)
                    st.session_state.analysis_result = result

                    if result.get("is_waste"):
                        db.save_classification(
                            item_name=result.get("detected_item"),
                            category=result.get("category"),
                            confidence=result.get("confidence"),
                            explanation=result.get("explanation"),
                            disposal_instructions=result.get("disposal_instructions"),
                            co2_saved_kg=result.get("co2_saved_kg", 0.45)
                        )

                    st.session_state.selected_tab = "📊 AI Result"
                    st.rerun()

# -----------------------------------------------------------------------------
# PAGE 3: AI RESULT
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "📊 AI Result":
    st.title("📊 Analysis & Disposal Result")

    result = st.session_state.analysis_result

    if result is None:
        st.warning("⚠️ No recent analysis found. Please upload or capture an image on the Analyze Waste page first.")
        if st.button("👈 Go to Analyze Waste"):
            st.session_state.selected_tab = "🔍 Analyze Waste"
            st.rerun()
    else:
        if not result.get("is_waste", True) or result.get("category") == "Unrecognized":
            st.error("❓ Unable to confidently identify this waste item. Please upload a clearer image.")
            st.markdown(f"**Reason:** {result.get('explanation')}")
            st.info("""
            **Tips for better AI analysis:**
            * Ensure adequate lighting on the item.
            * Focus directly on a single waste item.
            * Avoid severe blur, extreme dark shadows, or cluttered backgrounds.
            """)
            if st.button("🔄 Try Another Image"):
                st.session_state.selected_tab = "🔍 Analyze Waste"
                st.rerun()
        else:
            res_col1, res_col2 = st.columns([1, 1])

            with res_col1:
                if st.session_state.current_image:
                    st.image(st.session_state.current_image, caption="Analyzed Waste Item", use_container_width=True)

            with res_col2:
                detected_item = result.get("detected_item", "Waste Item")
                category = result.get("category", "General Waste")
                confidence = int(result.get("confidence", 0.95) * 100)
                explanation = result.get("explanation", "")
                badge_color = result.get("badge_color", "#10B981")
                badge_bg = result.get("badge_bg", "#D1FAE5")
                icon = result.get("icon", "♻️")

                st.markdown(f"### Detected Item: **{detected_item}**")

                badge_html = render_result_badge(
                    category, badge_color, badge_bg, icon,
                    is_dark=(st.session_state.theme == "dark")
                )
                st.markdown(f"{badge_html} <span class='confidence-pill'>🎯 Confidence: {confidence}%</span>", unsafe_allow_html=True)
                st.write("")

                st.markdown(f"**Why this category?**")
                st.write(explanation)

            st.markdown("---")

            st.subheader("💡 What should I do?")
            st.caption("Follow these practical steps to dispose of the item correctly:")

            instructions = result.get("disposal_instructions", [])
            if isinstance(instructions, list):
                for idx, step in enumerate(instructions, 1):
                    st.markdown(f"**{idx}.** {step}")
            else:
                st.write(instructions)

            st.markdown("---")

            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                if st.button("🔄 Analyze Another Item", use_container_width=True, type="primary"):
                    st.session_state.analysis_result = None
                    st.session_state.current_image = None
                    st.session_state.selected_tab = "🔍 Analyze Waste"
                    st.rerun()
            with act_col2:
                # Bug Fix 1: Pass detected category to Disposal Guide page
                if st.button("📖 View Full Disposal Guide", use_container_width=True):
                    st.session_state.target_disposal_category = category
                    st.session_state.selected_tab = "📖 Disposal Guide"
                    st.rerun()
            with act_col3:
                if st.button("📍 Find Nearby Facilities", use_container_width=True):
                    st.session_state.selected_tab = "📍 Nearby Facilities"
                    st.rerun()

# -----------------------------------------------------------------------------
# PAGE 4: DISPOSAL GUIDE (FIX 1: Linked to detected category)
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "📖 Disposal Guide":
    st.title("📖 Waste Disposal Guide")
    st.caption("Learn what belongs in each waste bin and how to handle specialized waste safely.")

    labels_path = BASE_DIR / "model" / "labels.json"
    with open(labels_path, "r", encoding="utf-8") as f:
        category_data = json.load(f)

    category_options = ["Recyclable", "Organic", "E-waste", "Hazardous", "General Waste"]
    category_labels = {
        "Recyclable": "♻️ Recyclable",
        "Organic": "🍎 Organic",
        "E-waste": "🔌 E-waste",
        "Hazardous": "☣️ Hazardous",
        "General Waste": "🗑️ General Waste"
    }

    # Bug Fix 1: Auto-select detected category passed from AI Result page
    target_cat = st.session_state.get("target_disposal_category", "Recyclable")
    if target_cat not in category_options:
        target_cat = "Recyclable"

    default_index = category_options.index(target_cat)

    if st.session_state.get("target_disposal_category"):
        st.success(f"🎯 **Disposal Guide for Analyzed Item**: Automatically showing instructions for **{category_labels[target_cat]}**.")

    selected_cat = st.radio(
        "Select Category Guide:",
        category_options,
        format_func=lambda x: category_labels[x],
        index=default_index,
        horizontal=True,
        key="disposal_guide_radio"
    )

    st.markdown("---")

    data = category_data.get(selected_cat, {})
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown(f"### {data.get('icon')} {selected_cat}")
        st.write(data.get("description"))

        st.markdown("#### ✅ What Belongs Here")
        for item in data.get("items", []):
            st.markdown(f"* {item}")

        st.markdown("#### ❌ What Should NOT Go Here")
        for avoid in data.get("avoid", []):
            st.markdown(f"* {avoid}")

    with col_b:
        st.markdown("#### 📋 Step-by-Step Disposal Instructions")
        for step in data.get("disposal_instructions", []):
            st.markdown(f"1. {step}")

        st.info(f"💡 **Eco Impact**: Recycling 1 kg of {selected_cat.lower()} material saves ~**{data.get('co2_impact_kg', 0.5)} kg** of carbon emissions.")

# -----------------------------------------------------------------------------
# PAGE 5: REPORT PUBLIC WASTE
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "📢 Report Public Waste":
    st.title("📢 Report Public Waste Site")
    st.caption("Report overflowing dustbins, open dumps, or hazardous waste in public areas for municipal cleanup.")

    input_mode = st.radio("Input Photo Method:", ["📤 File Upload", "📷 Camera Capture"], horizontal=True, key="public_input_mode")
    public_img = None

    if input_mode == "📤 File Upload":
        uploaded_pub = st.file_uploader("Upload photo of overflowing bin / public dump site...", type=["jpg", "jpeg", "png", "webp"], key="pub_file_up")
        if uploaded_pub is not None:
            try:
                public_img = Image.open(uploaded_pub).convert("RGB")
            except Exception as e:
                st.error(f"Error opening photo: {e}")
    elif input_mode == "📷 Camera Capture":
        st.info("📷 **Camera Capture**: Point camera at the public waste site.")
        cam_pub = st.camera_input("Take photo of public dump", key="pub_cam_cap")
        if cam_pub is not None:
            try:
                public_img = Image.open(cam_pub).convert("RGB")
            except Exception as e:
                st.error(f"Error reading camera photo: {e}")

    if public_img is not None:
        p_col1, p_col2 = st.columns([1, 1])

        with p_col1:
            st.image(public_img, caption="Public Site Photo", use_container_width=True)

        with p_col2:
            st.markdown("### 🤖 Automatic AI Assessment")
            with st.spinner("Analyzing waste type and calculating priority level..."):
                analysis = analyze_waste(public_img)
                detected_item = analysis.get("detected_item", "Public Waste Dump")
                category = analysis.get("category", "General Waste")
                confidence = analysis.get("confidence", 0.90)

                urgency_info = calculate_urgency(category, confidence)
                urgency_label = urgency_info["urgency"]
                badge_bg = urgency_info["badge_bg"]
                badge_color = urgency_info["badge_color"]

                st.markdown(f"**Detected Type:** {detected_item}")
                st.markdown(f"**Waste Category:** {category}")

                st.markdown(
                    f"<div style='background-color:{badge_bg}; color:{badge_color}; border:1px solid {badge_color}; "
                    f"padding:0.4rem 1rem; border-radius:8px; font-weight:700; display:inline-block; margin-top:0.3rem;'>"
                    f"Priority Score: {urgency_label}</div>",
                    unsafe_allow_html=True
                )
                st.caption("ℹ️ Urgency is automatically estimated based on waste hazard risk and AI confidence.")

        st.markdown("---")
        st.markdown("### 📍 Location & Report Details")

        # --- Report Public Waste: Geolocation handling using streamlit_js_eval ---
        if "public_location" not in st.session_state:
            st.session_state.public_location = ""

        loc_col1, loc_col2 = st.columns([2, 1])
        with loc_col1:
            manual_location = st.text_input(
                "Public Location / Landmark *",
                value=st.session_state.public_location,
                placeholder="e.g. Corner of 5th Avenue & Main Street, near Central Park entrance",
                key="public_location_input"
            )
            st.session_state.public_location = manual_location

        with loc_col2:
            if st.button("🎯 Detect My Real Location", key="detect_gps_report"):
                st.session_state.want_gps_report = True

        if st.session_state.get("want_gps_report"):
            location_data = get_geolocation()
            if location_data and isinstance(location_data, dict) and "coords" in location_data:
                lat = round(location_data["coords"]["latitude"], 4)
                lon = round(location_data["coords"]["longitude"], 4)
                with st.spinner("📍 Finding address name..."):
                    address = reverse_geocode(lat, lon)
                st.session_state.public_location = address
                st.session_state.public_lat = lat
                st.session_state.public_lon = lon
                st.session_state.want_gps_report = False
                st.success(f"✅ Location Captured: {address}")
                st.rerun()
            else:
                st.info("⏳ Waiting for location permission... If nothing happens, allow location access in your browser and click the button again.")
        # End of geolocation block

        notes_input = st.text_area(
            "Additional Notes (Optional):",
            placeholder="e.g. Municipal bin overflowing for 3 days. Blocking pedestrian sidewalk."
        )

        st.markdown("---")

        if st.button("🚀 Submit Public Waste Report", type="primary", use_container_width=True):
            if not manual_location:
                st.error("Please enter a location landmark or use browser GPS detection before submitting.")
            else:
                ref_id = db.save_public_report(
                    item_name=detected_item,
                    category=category,
                    confidence=confidence,
                    urgency=urgency_label,
                    priority_rank=urgency_info["priority_rank"],
                    location=manual_location,
                    latitude=st.session_state.get("public_lat"),
                    longitude=st.session_state.get("public_lon"),
                    notes=notes_input
                )
                st.session_state.public_report_submitted = ref_id
                st.balloons()
                st.success(f"🎉 **Report Submitted Successfully!** Reference ID: **{ref_id}**")
                st.info("Municipal sanitation teams have been notified. You can track this report on the Municipal Dashboard.")

# -----------------------------------------------------------------------------
# PAGE 6: MUNICIPAL DASHBOARD
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "🏛️ Municipal Dashboard":
    st.title("🏛️ Municipal Waste Command Dashboard")
    st.caption("Real-time public sanitation monitoring and incident resolution prototype.")

    st.warning("ℹ️ **DEMO — Municipal Integration Prototype**: This dashboard demonstrates how city sanitation departments receive, prioritize, and dispatch cleanup crews for citizen-reported public waste sites.")

    stats = db.get_public_reports_stats()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Total Reports", stats["total"], "📢")
    with m2:
        render_metric_card("High Priority Open", stats["high_open"], "🔴")
    with m3:
        render_metric_card("In Progress", stats["in_progress"], "🚚")
    with m4:
        render_metric_card("Resolved", stats["resolved"], "✅")

    st.markdown("---")

    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        status_filter = st.selectbox("Filter by Status:", ["All", "New", "In Progress", "Resolved"])
    with f_col2:
        urgency_filter = st.selectbox("Filter by Urgency:", ["All", "🔴 High Priority", "🟠 Medium Priority", "🟢 Low Priority"])

    reports = db.get_public_reports(status_filter=status_filter, urgency_filter=urgency_filter)

    st.markdown(f"### Submitted Reports ({len(reports)})")

    if not reports:
        st.info("No public reports match the selected filters. Submit a new report on the 'Report Public Waste' page!")
    else:
        for rep in reports:
            rep_id = rep["id"]
            ref_id = rep["ref_id"]
            urgency = rep["urgency"]
            status = rep["status"]

            status_colors = {
                "New": ("#FEF3C7", "#92400E"),
                "In Progress": ("#E0F2FE", "#0369A1"),
                "Resolved": ("#D1FAE5", "#065F46")
            }
            s_bg, s_fg = status_colors.get(status, ("#F1F5F9", "#334155"))

            with st.expander(f"📍 **{ref_id}** | {rep['location']} — **{urgency}** [{status}]", expanded=True):
                r_col1, r_col2 = st.columns([2, 1])

                with r_col1:
                    st.markdown(f"**Detected Type:** {rep['item_name']} ({rep['category']})")
                    st.markdown(f"**Location Landmark:** {rep['location']}")
                    st.markdown(f"**Timestamp:** `{rep['timestamp']}`")
                    if rep.get("notes"):
                        st.markdown(f"**Citizen Notes:** {rep['notes']}")

                with r_col2:
                    st.markdown(f"**Current Status:** <span style='background-color:{s_bg}; color:{s_fg}; padding:0.3rem 0.8rem; border-radius:9999px; font-weight:700;'>{status}</span>", unsafe_allow_html=True)
                    st.write("")

                    new_status = st.selectbox(
                        "Update Status:",
                        ["New", "In Progress", "Resolved"],
                        index=["New", "In Progress", "Resolved"].index(status),
                        key=f"status_select_{rep_id}"
                    )

                    if new_status != status:
                        db.update_report_status(rep_id, new_status)
                        st.success(f"Updated status for {ref_id} to '{new_status}'!")
                        st.rerun()

# -----------------------------------------------------------------------------
# PAGE 7: NEARBY FACILITIES (FIX 3: Real Geolocation)
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "📍 Nearby Facilities":
    st.title("📍 Nearby Recycling & Waste Facilities")
    st.caption("Locate verified collection centers, e-waste drop-off kiosks, and municipal waste stations.")

    st.warning("ℹ️ **DEMO / FALLBACK DATA**: The facilities listed below are simulated sample collection centers for demonstration purposes. Use real browser GPS detection below to calculate actual distances.")

    # --- Nearby Facilities: Geolocation handling using streamlit_js_eval ---
    if "curr_lat" not in st.session_state:
        st.session_state.curr_lat = 12.9716
    if "curr_lon" not in st.session_state:
        st.session_state.curr_lon = 77.5946
    if "gps_status" not in st.session_state:
        st.session_state.gps_status = "fallback"

    g_col1, g_col2 = st.columns([2, 1])
    with g_col1:
        if st.session_state.gps_status == "success":
            addr = st.session_state.get("curr_address", f"Lat {st.session_state.curr_lat}, Lon {st.session_state.curr_lon}")
            st.success(f"✅ Location Captured: {addr}")
        elif st.session_state.gps_status == "denied":
            st.warning("⚠️ Location access denied. Using fallback coordinates.")
        elif st.session_state.gps_status == "unsupported":
            st.warning("⚠️ Geolocation not supported. Using fallback coordinates.")
        else:
            st.info("📍 Click 'Detect My Real Location' to calculate exact distances to your actual physical position.")
    with g_col2:
        if st.button("🎯 Detect My Real Location", key="detect_gps_nearby"):
            st.session_state.want_gps_nearby = True

    if st.session_state.get("want_gps_nearby"):
        location_data = get_geolocation()
        if location_data and isinstance(location_data, dict) and "coords" in location_data:
            st.session_state.curr_lat = round(location_data["coords"]["latitude"], 4)
            st.session_state.curr_lon = round(location_data["coords"]["longitude"], 4)
            with st.spinner("📍 Finding address name..."):
                st.session_state.curr_address = reverse_geocode(st.session_state.curr_lat, st.session_state.curr_lon)
            st.session_state.gps_status = "success"
            st.session_state.want_gps_nearby = False
            st.success(f"✅ Location Captured: {st.session_state.curr_address}")
            st.rerun()
        else:
            st.info("⏳ Waiting for location permission... If nothing happens, allow location access in your browser and click the button again.")
        # End of geolocation block

    st.markdown("---")

    filter_col1, filter_col2 = st.columns([1, 1])
    with filter_col1:
        cat_filter = st.selectbox("Filter by Accepted Category:", ["All", "Recyclable", "Organic", "E-waste", "Hazardous", "General Waste"])
    with filter_col2:
        user_city = st.selectbox("Area Center:", ["Current GPS / Central District (Default)", "Industrial Tech Park", "North Greenbelt"])

    if user_city == "Industrial Tech Park":
        curr_lat, curr_lon = 12.9352, 77.6245
    elif user_city == "North Greenbelt":
        curr_lat, curr_lon = 12.9856, 77.6057
    else:
        curr_lat, curr_lon = st.session_state.curr_lat, st.session_state.curr_lon

    facilities = geo_service.get_nearby_facilities(
        user_lat=curr_lat,
        user_lon=curr_lon,
        category_filter=cat_filter
    )

    st.markdown(f"### Found {len(facilities)} Collection Centers")

    for fac in facilities:
        with st.expander(f"📍 **{fac['name']}** — {fac['distance_km']} km away ({fac['type']})", expanded=True):
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                st.markdown(f"**Address:** {fac['address']}, {fac['city']}")
                st.markdown(f"**Hours:** {fac['hours']}")
                st.markdown(f"**Contact:** `{fac['phone']}`")
                st.markdown(f"**Accepted Items:** {', '.join(fac['accepted_items'])}")
                st.write(f"_*Note:*_ {fac['notes']}")
            with f_col2:
                st.markdown(f"[🗺️ Open Directions in Google Maps]({fac['map_url']})")

# -----------------------------------------------------------------------------
# PAGE 8: MY IMPACT
# -----------------------------------------------------------------------------
elif st.session_state.selected_tab == "🌱 My Impact":
    st.title("🌱 My Impact Dashboard")
    st.caption("Track your waste-sorting activity and environmental footprint over time.")

    stats = db.get_stats()
    history = db.get_history(limit=50)

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        render_metric_card("Total Items Analyzed", stats["total_items"], "📦")
    with m_col2:
        render_metric_card("Estimated CO2 Diverted (kg)", stats["total_co2_saved_kg"], "🌿")
    with m_col3:
        cat_counts = stats["category_counts"]
        recycled_total = cat_counts["Recyclable"] + cat_counts["Organic"] + cat_counts["E-waste"]
        recycling_rate = int((recycled_total / stats["total_items"] * 100)) if stats["total_items"] > 0 else 0
        render_metric_card("Diversion Rate", f"{recycling_rate}%", "♻️")

    st.markdown("---")

    st.success("🌟 **\"Every correctly sorted item is a small step toward better waste management.\"**")

    st.subheader("📊 Category Breakdown")

    if stats["total_items"] == 0:
        st.info("No items analyzed yet! Scan your first waste item on the 'Analyze Waste' page to start tracking your impact.")
    else:
        ch_col1, ch_col2 = st.columns([1, 1])

        df_counts = pd.DataFrame([
            {"Category": k, "Count": v} for k, v in stats["category_counts"].items()
        ])

        text_color = "#F8FAFC" if st.session_state.theme == "dark" else "#0F172A"
        axis_color = "#CBD5E1" if st.session_state.theme == "dark" else "#334155"

        with ch_col1:
            st.markdown("#### Waste Items by Category")
            bar_chart = alt.Chart(df_counts).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Category", sort=None, axis=alt.Axis(labelColor=axis_color, titleColor=text_color)),
                y=alt.Y("Count", axis=alt.Axis(labelColor=axis_color, titleColor=text_color)),
                color=alt.Color("Category", scale=alt.Scale(
                    domain=["Recyclable", "Organic", "E-waste", "Hazardous", "General Waste"],
                    range=["#10B981", "#84CC16", "#0284C7", "#E11D48", "#64748B"]
                ))
            ).properties(height=300, background='transparent').configure_view(stroke=None)
            st.altair_chart(bar_chart, use_container_width=True)

        with ch_col2:
            st.markdown("#### Distribution")
            pie_chart = alt.Chart(df_counts).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Category", type="nominal", scale=alt.Scale(
                    domain=["Recyclable", "Organic", "E-waste", "Hazardous", "General Waste"],
                    range=["#10B981", "#84CC16", "#0284C7", "#E11D48", "#64748B"]
                ))
            ).properties(height=300, background='transparent').configure_view(stroke=None)
            st.altair_chart(pie_chart, use_container_width=True)

    st.markdown("---")

    st.subheader("📋 Classification History Log")

    if history:
        df_hist = pd.DataFrame(history)
        df_display = df_hist[["timestamp", "item_name", "category", "confidence", "co2_saved_kg"]]
        df_display.columns = ["Timestamp", "Item Name", "Category", "Confidence", "CO2 Saved (kg)"]

        st.dataframe(df_display, use_container_width=True)

        if st.button("🗑️ Clear History Log"):
            db.clear_history()
            st.success("History log reset successfully.")
            st.rerun()
    else:
        st.write("History log is empty.")