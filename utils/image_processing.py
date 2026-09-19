import io
import cv2
import numpy as np
from PIL import Image

def load_image_from_input(image_input):
    """
    Standardize various image input types (UploadedFile, bytes, PIL Image, or numpy array)
    into both PIL.Image and OpenCV (BGR numpy array) formats.
    """
    if image_input is None:
        return None, None

    try:
        if isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        elif isinstance(image_input, bytes):
            pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif hasattr(image_input, "read"):
            # Streamlit UploadedFile or BytesIO
            bytes_data = image_input.read()
            # Reset pointer if possible
            if hasattr(image_input, "seek"):
                image_input.seek(0)
            pil_img = Image.open(io.BytesIO(bytes_data)).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            # Assume BGR or RGB array
            if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
            else:
                pil_img = Image.fromarray(image_input).convert("RGB")
        else:
            return None, None

        # Convert PIL Image to OpenCV BGR numpy array
        rgb_array = np.array(pil_img)
        cv_bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

        return pil_img, cv_bgr

    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

def evaluate_image_quality(cv_bgr):
    """
    Evaluate if an image is clear, sufficiently detailed, and valid for computer vision.
    Uses Laplacian variance for blur detection and standard deviation for contrast/detail check.
    
    Returns:
        is_valid (bool), reason (str), variance (float)
    """
    if cv_bgr is None or cv_bgr.size == 0:
        return False, "Empty or invalid image data.", 0.0

    height, width = cv_bgr.shape[:2]
    if height < 50 or width < 50:
        return False, "Image resolution is too low. Please upload a larger image.", 0.0

    # Convert to grayscale
    gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Variance of Laplacian for blur detection
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 2. Standard deviation of pixel intensities for contrast check
    std_dev = np.std(gray)

    # Thresholds for unusable images (extreme blur or blank/solid color)
    if laplacian_var < 8.0 and std_dev < 12.0:
        return False, "The image appears extremely blurry or has uniform color with no clear object visible.", laplacian_var

    if std_dev < 5.0:
        return False, "The image lacks contrast (appears blank or pitch dark). Please upload a clearer photo.", laplacian_var

    return True, "Image quality is acceptable.", laplacian_var

def extract_image_features(cv_bgr):
    """
    Extract color HSV histogram and edge density features from an OpenCV BGR image.
    Used for local computer vision heuristics.
    """
    if cv_bgr is None:
        return {}

    # Convert to HSV
    hsv = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2HSV)
    
    # Calculate dominant color ranges
    h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
    v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])

    # Green range (Organic/Plant matter): Hue ~ 35 to 85
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    green_ratio = np.count_nonzero(green_mask) / (cv_bgr.shape[0] * cv_bgr.shape[1])

    # Metallic / Gray range (E-waste / Cans): Low saturation, mid value
    gray_mask = cv2.inRange(hsv, (0, 0, 50), (180, 50, 220))
    gray_ratio = np.count_nonzero(gray_mask) / (cv_bgr.shape[0] * cv_bgr.shape[1])

    # Canny Edge Density
    gray_img = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_img, 50, 150)
    edge_density = np.count_nonzero(edges) / (cv_bgr.shape[0] * cv_bgr.shape[1])

    return {
        "green_ratio": green_ratio,
        "gray_ratio": gray_ratio,
        "edge_density": edge_density
    }
