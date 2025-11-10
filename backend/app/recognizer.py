from typing import Optional
from easyocr import Reader  # type: ignore
from cv2 import imread
from dataclasses import dataclass
from enum import Enum
from re import sub, match

from app.config import config  # Importar configuración

# Constantes globales
OCR_READER: Optional[Reader] = None


class PlateFormat(Enum):
    NUEVO = r"^[A-Z]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
    ANTIGUO = r"^[A-Z]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
    MOTOCICLETA = r"^[A-Z]{1}[\s\-]?[0-9]{2}[\s\-]?[A-Z]{2}[\s\-]?[0-9]{2}$"
    OFICIAL = r"^GO[\s\-]?[0-9]{5}$"
    FEDERAL = r"^TF[\s\-]?[0-9]{5}$"
    DIPLOMATICO = r"^CD[\s\-]?[0-9]{5}$"


@dataclass
class OCRResult:
    text: str
    confidence: float


def get_ocr_reader():
    global OCR_READER
    if OCR_READER is None:
        OCR_READER = Reader(config.ocr.languages)
    return OCR_READER


def get_plate(img) -> str:
    reader = get_ocr_reader()

    image = load_image(img)
    if image is None:
        return "Placa no detectada"

    results = reader.readtext(image)

    valid_plates = []
    for bbox, text, confidence in results:
        if confidence >= config.ocr.confidence_threshold:
            cleaned_text = clean_plate_text(text)
            if is_valid_plate(cleaned_text):
                formatted_text = format_plate(cleaned_text)
                valid_plates.append(OCRResult(formatted_text, confidence))

    if valid_plates:
        valid_plates.sort(key=lambda x: x.confidence, reverse=True)
        return valid_plates[0].text

    return "Placa no detectada"


def load_image(img):
    if isinstance(img, str):
        return imread(img)
    return img


def clean_plate_text(text: str) -> str:
    text = text.upper()
    text = sub(r"[^A-Z0-9\- ]", "", text)
    text = sub(r"\s+", " ", text).strip()
    return text


def is_valid_plate(text: str) -> bool:
    return any(match(pattern.value, text) for pattern in PlateFormat)


def format_plate(text: str) -> str:
    clean_text = sub(r"[\s\-]", "", text)

    # Detectar formato específico
    if match(PlateFormat.OFICIAL.value, text):
        return f"GO {clean_text[2:]}"
    elif match(PlateFormat.FEDERAL.value, text):
        return f"TF {clean_text[2:]}"
    elif match(PlateFormat.DIPLOMATICO.value, text):
        return f"CD {clean_text[2:]}"
    elif match(PlateFormat.MOTOCICLETA.value, text) and len(clean_text) == 7:
        return f"{clean_text[:1]} {clean_text[1:3]} {clean_text[3:5]} {clean_text[5:]}"
    elif len(clean_text) == 7:
        return f"{clean_text[:3]} {clean_text[3:5]} {clean_text[5:]}"

    return clean_text
