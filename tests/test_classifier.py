import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.waste_analyzer import analyze_waste, calculate_urgency
from utils.image_processing import evaluate_image_quality, load_image_from_input

def test_evaluate_image_quality_valid():
    array = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    img = Image.fromarray(array)
    _, cv_bgr = load_image_from_input(img)
    is_valid, reason, _ = evaluate_image_quality(cv_bgr)
    assert is_valid is True

def test_evaluate_image_quality_blank():
    array = np.zeros((100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(array)
    _, cv_bgr = load_image_from_input(img)
    is_valid, reason, _ = evaluate_image_quality(cv_bgr)
    assert is_valid is False

def test_analyze_waste_returns_structured_dict():
    array = np.random.randint(50, 200, (300, 300, 3), dtype=np.uint8)
    img = Image.fromarray(array)
    result = analyze_waste(img)
    
    assert isinstance(result, dict)
    assert "detected_item" in result
    assert "category" in result
    assert "confidence" in result
    assert "explanation" in result
    assert "disposal_instructions" in result

def test_calculate_urgency():
    u_high = calculate_urgency("Hazardous", 0.95)
    assert u_high["priority_rank"] == 1
    assert "High" in u_high["urgency"]

    u_med = calculate_urgency("Recyclable", 0.80)
    assert u_med["priority_rank"] == 2
    assert "Medium" in u_med["urgency"]

    u_low = calculate_urgency("General Waste", 0.50)
    assert u_low["priority_rank"] == 3
    assert "Low" in u_low["urgency"]

if __name__ == "__main__":
    test_evaluate_image_quality_valid()
    test_evaluate_image_quality_blank()
    test_analyze_waste_returns_structured_dict()
    test_calculate_urgency()
    print("[SUCCESS] Classifier tests passed!")
