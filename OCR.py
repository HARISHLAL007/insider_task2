import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'], verbose=False)


def enhance_image(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found or unreadable: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(gray, h=15)

    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )

    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return cleaned


def extract_text(image_path: str, confidence_threshold: float = 0.3) -> list[str]:
    try:
        enhanced = enhance_image(image_path)
        results = reader.readtext(enhanced, detail=1)

        lines = []
        for (bbox, text, confidence) in results:
            text = text.strip()
            if not text:
                continue
            if confidence >= confidence_threshold or len(text) <= 15:
                lines.append(text)

        return lines

    except FileNotFoundError as e:
        print(f"[OCR] {e}")
        return []
    except cv2.error as e:
        print(f"[OCR] Image processing error: {e}")
        return []
    except Exception as e:
        print(f"[OCR] Unexpected error: {e}")
        return []
