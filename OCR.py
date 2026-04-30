"""
ocr.py — FIXED for PaddleOCR v3.5+
Compatible with Python 3.13 (as much as possible)
"""

import os
import cv2
import tempfile
import numpy as np
from paddleocr import PaddleOCR

# ✅ FIX 1: correct initialization (NO show_log, NO use_angle_cls)
ocr = PaddleOCR(
    lang="en"
)


# ─────────────────────────────
# IMAGE PREPROCESSING
# ─────────────────────────────
def enhance_image(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # resize
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # denoise
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # threshold (helps OCR a lot)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )

    # back to 3-channel
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


# ─────────────────────────────
# OCR FUNCTION
# ─────────────────────────────
def extract_text(image_path: str, conf_thres: float = 0.4):
    try:
        print("🔥 OCR STARTED")

        img = enhance_image(image_path)

        # temp file (PaddleOCR needs path)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = f.name

        cv2.imwrite(temp_path, img)

        # ✅ FIX 2: correct v3 API usage
        result = ocr.predict(temp_path)

        os.remove(temp_path)

        lines = []

        for page in result:
            # PaddleOCR v3 format
            if hasattr(page, "rec_texts"):
                for text, score in zip(page.rec_texts, page.rec_scores):
                    if score >= conf_thres:
                        lines.append(text.strip())

            # fallback safety
            elif isinstance(page, list):
                for item in page:
                    try:
                        text = item[1][0]
                        score = item[1][1]
                        if score >= conf_thres:
                            lines.append(text.strip())
                    except:
                        continue

        print(f"✅ OCR OUTPUT LINES: {len(lines)}")
        return lines

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return []
