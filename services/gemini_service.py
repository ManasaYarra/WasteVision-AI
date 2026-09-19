import os
import io
import json
import base64
import requests

def analyze_with_gemini(pil_img, api_key=None):
    """
    Call Google Gemini Vision REST API to analyze a waste image.
    Returns structured dict or None if API key is missing or request fails.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key == "your_gemini_api_key_here":
        return None

    try:
        # Convert PIL Image to JPEG base64 bytes
        buffered = io.BytesIO()
        pil_img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        base64_image = base64.b64encode(img_bytes).decode("utf-8")

        # Prepare Gemini API endpoint and prompt
        # We use Gemini 1.5 Flash REST API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        prompt = """
        Analyze this image for waste identification and disposal guidance.
        Determine if the image clearly contains a waste item or object to dispose of.

        Return ONLY a JSON object with the following exact keys:
        {
          "is_waste": true or false,
          "detected_item": "Name of the detected item (e.g., PET Plastic Bottle, Mobile Charger, Apple Core)",
          "category": "One of: Recyclable, Organic, E-waste, Hazardous, General Waste, or Unrecognized",
          "confidence": confidence score between 0.50 and 0.99,
          "explanation": "Clear short sentence explaining why it belongs to this category",
          "disposal_instructions": ["Step 1", "Step 2", "Step 3"]
        }

        If the image is blurry, contains human faces without waste, or is not a waste item, set "is_waste": false and "category": "Unrecognized".
        Do not include markdown backticks around JSON output if possible.
        """

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text_content = text_content.strip()
                if text_content.startswith("```json"):
                    text_content = text_content.replace("```json", "").replace("```", "").strip()
                
                result = json.loads(text_content)
                return result
        else:
            print(f"Gemini API returned status code {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"Error calling Gemini Vision API: {e}")
        return None
