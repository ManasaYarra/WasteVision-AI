# WasteVision AI – Smart Waste Identification & Disposal Assistant

**WasteVision AI** is a student hackathon web application designed to help everyday citizens identify waste items from uploaded images or camera captures and understand how to dispose of them correctly.

> *"Snap it. Identify it. Dispose of it right."*

---

## 🌟 Key Features

1. **AI/CV Waste Analysis**: Multi-tiered Computer Vision pipeline (PyTorch MobileNetV2 + OpenCV feature extractor + optional Google Gemini Vision API).
2. **5 Core Waste Categories**: Recyclable, Organic, E-waste, Hazardous, and General Waste.
3. **Quality & Non-Waste Detection**: Gracefully detects blurry, dark, blank, or non-waste images and prompts for clearer input.
4. **Step-by-Step Disposal Instructions**: Clear, practical binning guidance and safety notes for each category.
5. **Nearby Facilities Finder**: Geolocation-based recycling & drop-off center search calculated using Haversine formulas with Google Maps direction links.
6. **Personal Impact Dashboard**: SQLite-backed activity tracking showing total items analyzed, category distribution charts (Altair), and estimated CO2 diverted.

---

## 📂 Project Structure

```
WasteVision-AI/
├── app.py                     # Main Streamlit web application (Navigation, UI Layout, Pages)
├── requirements.txt           # Python package dependencies
├── README.md                  # Complete documentation, setup, and deployment guide
├── .gitignore                 # Git ignore rules
├── .env.example               # Template environment variables (GEMINI_API_KEY, MAPS_API_KEY)
├── model/
│   ├── waste_classifier.py    # Local PyTorch + OpenCV classifier engine
│   └── labels.json            # Waste categories, item definitions & disposal steps
├── services/
│   ├── waste_analyzer.py      # Main analyze_waste(image) API entrypoint
│   ├── gemini_service.py      # Google Gemini Vision REST API integration
│   ├── geolocation_service.py # Facility lookup & Haversine distance calculator
│   └── database.py            # SQLite history manager & impact metrics tracker
├── data/
│   ├── facilities.json        # Pre-loaded fallback recycling & drop-off center dataset
│   └── waste_history.db       # Local SQLite database (created automatically)
├── utils/
│   ├── ui_components.py       # Custom CSS styling, hero banner, badges, metric cards
│   └── image_processing.py    # OpenCV Laplacian blur check & feature extraction
└── tests/
    ├── test_classifier.py     # Tests for image validation & classification
    ├── test_database.py       # Tests for SQLite database operations
    └── test_facilities.py     # Tests for geolocation distance calculation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Clone / Open Directory
```bash
cd WasteVision-AI
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧠 How the AI Analysis Currently Works

The image classification system uses a **multi-tiered hybrid approach**:

1. **Quality Check (`utils/image_processing.py`)**: 
   - Uses OpenCV (`cv2.Laplacian`) to analyze edge variance and contrast. Extremely blurry, pitch black, or solid color images trigger a helpful warning requesting a clearer photo.
2. **Tier 1 - Gemini Vision API (`services/gemini_service.py`)**:
   - If `GEMINI_API_KEY` is provided in `.env` or settings, the app sends a request to Google's Gemini Vision REST API for cloud AI identification.
3. **Tier 2 - Local Computer Vision (`model/waste_classifier.py`)**:
   - Uses a PyTorch `MobileNetV2` neural network pretrained on ImageNet.
   - Maps predicted object classes (e.g. bottles, cans, fruit, phones, batteries) to the 5 target waste categories.
4. **Tier 3 - OpenCV Feature Matcher**:
   - Analyzes HSV color histograms (green ratio for organic matter, gray/metallic for e-waste) and edge density to refine classifications.

---

## 🔌 Where to Add Custom AI Models / APIs

- **Custom PyTorch / YOLO Model**:
  Edit `model/waste_classifier.py`. You can load custom YOLO weights (`ultralytics`) or fine-tuned PyTorch `.pt`/`.pth` weights in `_init_vision_model()`.
- **Alternative Cloud Vision APIs (e.g., OpenAI GPT-4o, AWS Rekognition, Google Cloud Vision)**:
  Edit `services/waste_analyzer.py` or add a new service file under `services/` and integrate it into the `analyze_waste(image)` function pipeline.

---

## 🧪 Running Tests

Run the test suite using `pytest`:
```bash
pytest tests/
```

---

## 🌐 How to Deploy

### Streamlit Community Cloud (Recommended & Free)
1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/).
3. Connect your repo and set main file path to `app.py` (or `WasteVision-AI/app.py`).
4. Add environment variables (e.g. `GEMINI_API_KEY`) under Advanced Settings.

### Render / Heroku / Docker
- A `Procfile` command: `web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

---

## 📋 Hackathon Submission Checklist

- [x] Functional 6-page navigation (Home, Analyze Waste, AI Result, Disposal Guide, Nearby Facilities, My Impact).
- [x] Local PyTorch + OpenCV computer vision engine.
- [x] SQLite classification logging and impact analytics dashboard.
- [x] Geolocation distance calculation using Haversine formula.
- [x] Blurry/non-waste image handling.
- [ ] *Optional for Hackathon Submission*: Add real Google Maps API key in `.env` if live maps map rendering is required.
