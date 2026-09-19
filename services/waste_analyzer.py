import os
import json
from pathlib import Path
from utils.image_processing import load_image_from_input, evaluate_image_quality, extract_image_features
from model.waste_classifier import LocalWasteClassifier
from services.gemini_service import analyze_with_gemini

BASE_DIR = Path(__file__).resolve().parent.parent

# Global singleton
_local_classifier = None

def get_local_classifier():
    global _local_classifier
    if _local_classifier is None:
        _local_classifier = LocalWasteClassifier()
    return _local_classifier

def analyze_waste(image_input, api_key=None):
    """
    Main Computer Vision / AI Analysis pipeline for WasteVision AI.
    
    Architecture:
    1. Image Quality Validation (OpenCV Laplacian blur check).
    2. Cloud AI Mode (Google Gemini Vision REST API when API key configured).
    3. Local Demo Fallback Engine (PyTorch MobileNetV2 mapped to waste taxonomy + OpenCV feature matcher).

    Returns:
        Structured dictionary containing:
        - detected_item
        - category
        - confidence
        - explanation
        - disposal_instructions
        - is_waste
    """
    # 1. Load & standardize image
    pil_img, cv_bgr = load_image_from_input(image_input)

    if pil_img is None or cv_bgr is None:
        return {
            "is_waste": False,
            "detected_item": "Unrecognized Input",
            "category": "Unrecognized",
            "confidence": 0.0,
            "explanation": "No valid image data was provided or the file format is unsupported.",
            "disposal_instructions": ["Please upload a valid JPEG, PNG, or WEBP photo."],
            "badge_color": "#64748B",
            "badge_bg": "#F1F5F9",
            "icon": "⚠️"
        }

    # 2. Image Quality & Blur Evaluation
    is_clear, quality_reason, _ = evaluate_image_quality(cv_bgr)
    if not is_clear:
        return {
            "is_waste": False,
            "detected_item": "Unclear Image",
            "category": "Unrecognized",
            "confidence": 0.30,
            "explanation": f"Unable to confidently identify this waste item. {quality_reason}",
            "disposal_instructions": [
                "Ensure adequate lighting on the item.",
                "Hold camera steady to avoid blur.",
                "Place the waste item clearly in the center of the frame and try again."
            ],
            "badge_color": "#E11D48",
            "badge_bg": "#FFE4E6",
            "icon": "❓"
        }

    # Load category reference info using pathlib
    labels_path = BASE_DIR / "model" / "labels.json"
    category_info = {}
    if labels_path.exists():
        with open(labels_path, "r", encoding="utf-8") as f:
            category_info = json.load(f)

    # 3. Cloud AI Mode (Google Gemini Vision REST API)
    gemini_result = analyze_with_gemini(pil_img, api_key)
    if gemini_result and isinstance(gemini_result, dict):
        cat = gemini_result.get("category", "General Waste")
        cat_meta = category_info.get(cat, category_info.get("General Waste", {}))

        return {
            "is_waste": gemini_result.get("is_waste", True),
            "detected_item": gemini_result.get("detected_item", "Waste Item"),
            "category": cat,
            "confidence": round(float(gemini_result.get("confidence", 0.95)), 2),
            "explanation": gemini_result.get("explanation", "AI analyzed visual components of the item."),
            "disposal_instructions": gemini_result.get("disposal_instructions", cat_meta.get("disposal_instructions", [])),
            "badge_color": cat_meta.get("badge_color", "#10B981"),
            "badge_bg": cat_meta.get("badge_bg", "#D1FAE5"),
            "icon": cat_meta.get("icon", "♻️"),
            "co2_saved_kg": cat_meta.get("co2_impact_kg", 0.45)
        }

    # 4. Local Demo Fallback Classifier (PyTorch + OpenCV)
    classifier = get_local_classifier()
    local_result = classifier.classify_pil_image(pil_img)

    if local_result and local_result.get("is_waste"):
        features = extract_image_features(cv_bgr)
        cat = local_result["category"]
        
        # Color feature refinement: High green ratio -> Organic
        if features.get("green_ratio", 0.0) > 0.35 and cat == "General Waste":
            cat = "Organic"
            local_result["category"] = "Organic"
            local_result["detected_item"] = "Fruit / Vegetable Waste"
            local_result["explanation"] = "OpenCV color feature extraction detected high organic plant matter green hue signature."

        cat_meta = category_info.get(cat, category_info.get("General Waste", {}))
        local_result["badge_color"] = cat_meta.get("badge_color", "#10B981")
        local_result["badge_bg"] = cat_meta.get("badge_bg", "#D1FAE5")
        local_result["icon"] = cat_meta.get("icon", "♻️")
        local_result["co2_saved_kg"] = cat_meta.get("co2_impact_kg", 0.45)

        return local_result

    # 5. Fallback for unrecognized items
    return {
        "is_waste": False,
        "detected_item": "Unrecognized Item",
        "category": "Unrecognized",
        "confidence": 0.40,
        "explanation": "Unable to confidently identify this waste item. Please upload a clearer image.",
        "disposal_instructions": [
            "Ensure the item is clearly visible in the center of the photo.",
            "Avoid dark backgrounds, severe blur, or multiple overlapping objects."
        ],
        "badge_color": "#E11D48",
        "badge_bg": "#FFE4E6",
        "icon": "❓"
    }

def calculate_urgency(category, confidence):
    """
    Calculate public waste report urgency level based on detected waste category and AI confidence.
    
    Priority Heuristics:
    - High Priority (🔴 Rank 1): Hazardous or E-waste detected (or confidence >= 0.88).
    - Medium Priority (🟠 Rank 2): Recyclable or Organic waste detected.
    - Low Priority (🟢 Rank 3): General Waste or low confidence detection.
    """
    cat = (category or "").strip().title()
    conf = float(confidence or 0.0)

    if cat in ["Hazardous", "E-Waste", "E-waste"] or conf >= 0.88:
        return {
            "urgency": "🔴 High Priority",
            "priority_rank": 1,
            "badge_color": "#E11D48",
            "badge_bg": "#FFE4E6"
        }
    elif cat in ["Recyclable", "Organic"]:
        return {
            "urgency": "🟠 Medium Priority",
            "priority_rank": 2,
            "badge_color": "#F59E0B",
            "badge_bg": "#FEF3C7"
        }
    else:
        return {
            "urgency": "🟢 Low Priority",
            "priority_rank": 3,
            "badge_color": "#10B981",
            "badge_bg": "#D1FAE5"
        }
