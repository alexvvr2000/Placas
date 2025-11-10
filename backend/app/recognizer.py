import cv2
import numpy as np
import imutils
import easyocr

def get_plate(img):
    """
    Detecta y extrae el texto de una placa vehicular en una imagen.
    
    Args:
        img: Imagen en formato BGR (como la lee cv2.imread)
    
    Returns:
        str: Texto de la placa detectada o cadena vacía si no se detecta
    """
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Reducción de ruido
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Detección de bordes
    edged = cv2.Canny(bfilter, 30, 200)
    
    # Encontrar contornos
    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    # Buscar contorno rectangular (placa)
    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break
    
    # Si no se encuentra placa, retornar cadena vacía
    if location is None:
        return ""
    
    # Crear máscara y extraer región de la placa
    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [location], 0, 255, -1)
    new_image = cv2.bitwise_and(img, img, mask=mask)
    
    # Recortar la región de la placa
    (x, y) = np.where(mask == 255)
    (x1, y1) = (np.min(x), np.min(y))
    (x2, y2) = (np.max(x), np.max(y))
    cropped_image = gray[x1:x2+1, y1:y2+1]
    
    # Usar EasyOCR para leer el texto
    reader = easyocr.Reader(['en'])
    result = reader.readtext(cropped_image)
    
    # Retornar el texto de la placa (primer resultado)
    if result:
        return result[0][-2]
    else:
        return ""

# Ejemplo de uso:
# img = cv2.imread('image4.jpg')
# plate_text = get_plate(img)
# print(plate_text)