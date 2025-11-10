from logging import basicConfig, INFO, getLogger
from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from app.recognizer import get_plate
from app.models import PlateResponse, ErrorResponse
import cv2
import numpy as np
import werkzeug
from datetime import datetime
from app.email_service import EmailService
from app.config import config  # Importar configuración

basicConfig(level=INFO)
logger = getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.app.max_file_size * 1024 * 1024

# Configuración de Flask-RESTX
api = Api(
    app,
    version="1.0",
    title="API de Reconocimiento de Placas",
    description="API para reconocimiento de placas vehiculares",
    doc="/api/docs/",
)

# Usar configuración desde archivo .ini
email_service = EmailService(config.email)

# Modelos para Swagger (igual que antes)
plate_model = api.model(
    "PlateResponse",
    {
        "plate_number": fields.String(required=True),
        "status": fields.String(required=True),
        "timestamp": fields.String(),
        "notification_sent": fields.Boolean(),
    },
)

error_model = api.model(
    "ErrorResponse",
    {
        "error": fields.String(required=True),
        "message": fields.String(required=True),
    },
)

# Parser para imágenes
image_parser = reqparse.RequestParser()
image_parser.add_argument(
    "image",
    type=werkzeug.datastructures.FileStorage,
    location="files",
    required=True,
    help="Archivo de imagen (JPG, PNG, etc.)",
)
image_parser.add_argument(
    "notify_email",
    type=str,
    location="form",
    required=False,
    help="Email para enviar notificación (opcional)",
)


def process_image(file_storage):
    """Procesa archivo de imagen a formato OpenCV"""
    img_array = np.frombuffer(file_storage.read(), np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)


def create_response(plate_text, notification_sent=False):
    """Crea respuesta estandarizada"""
    return PlateResponse(
        plate_number=plate_text,
        status="éxito" if plate_text != "Placa no detectada" else "no detectada",
        timestamp=datetime.now().isoformat(),
        notification_sent=notification_sent,
    ).__dict__


@api.route("/api/health")
class HealthCheck(Resource):
    def get(self):
        """Verificar estado de la API"""
        return {
            "status": "correcto",
            "message": "API funcionando correctamente",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "email_enabled": config.email.enabled,
                "ocr_languages": config.ocr.languages,
            },
        }


@api.route("/api/recognize/plate")
class RecognizePlate(Resource):
    @api.doc("recognize_plate")
    @api.expect(image_parser)
    @api.response(200, "Éxito", plate_model)
    @api.response(400, "Error en solicitud", error_model)
    @api.response(500, "Error interno", error_model)
    def post(self):
        """
        Reconocer placa desde imagen JPG/PNG

        Sube una imagen y opcionalmente envía notificación por email
        """
        try:
            args = image_parser.parse_args()
            file = args["image"]
            notify_email = args.get("notify_email")

            if not file.filename:
                return ErrorResponse(
                    error="Archivo inválido", message="Selecciona un archivo válido"
                ).__dict__, 400

            # Procesar imagen
            img = process_image(file)
            if img is None:
                return ErrorResponse(
                    error="Imagen inválida", message="No se pudo procesar la imagen"
                ).__dict__, 400

            # Reconocer placa
            plate_text = get_plate(img)

            # Enviar notificación si se solicita y se detectó placa
            notification_sent = False
            if (
                notify_email
                and plate_text != "Placa no detectada"
                and config.email.enabled
            ):
                # Leer imagen nuevamente para adjuntar (resetear el puntero)
                file.stream.seek(0)
                image_data = file.read()

                plate_data = {
                    "plate_number": plate_text,
                    "status": "éxito",
                    "timestamp": datetime.now().isoformat(),
                }

                notification_sent = email_service.send_plate_detection_notification(
                    to_email=notify_email,
                    plate_data=plate_data,
                    attach_image=image_data,
                    image_filename=file.filename,
                )

            return create_response(plate_text, notification_sent), 200

        except Exception as e:
            logger.error(f"Error procesando imagen: {str(e)}")
            return ErrorResponse(
                error="Error de procesamiento",
                message="Error interno procesando la imagen",
            ).__dict__, 500


@api.route("/api/email/test")
class EmailTest(Resource):
    @api.response(200, "Test exitoso")
    @api.response(400, "Error en configuración", error_model)
    def post(self):
        """Probar configuración de email"""
        if not config.email.enabled:
            return ErrorResponse(
                error="Email desactivado",
                message="Servicio de email desactivado en config.ini",
            ).__dict__, 400

        success, message = email_service.test_connection()

        if success:
            return {"status": "éxito", "message": message}, 200
        else:
            return ErrorResponse(error="Test fallido", message=message).__dict__, 400


@api.route("/api/config/reload")
class ConfigReload(Resource):
    @api.response(200, "Configuración recargada")
    @api.response(500, "Error recargando configuración", error_model)
    def post(self):
        """Recargar configuración desde archivo"""
        try:
            config.reload()
            return {
                "status": "éxito",
                "message": "Configuración recargada correctamente",
                "email_enabled": config.email.enabled,
            }, 200
        except Exception as e:
            return ErrorResponse(
                error="Error recargando configuración", message=str(e)
            ).__dict__, 500


# Manejadores de errores
@app.errorhandler(413)
def too_large(e):
    return ErrorResponse(
        error="Archivo muy grande",
        message=f"La imagen supera el límite de {config.app.max_file_size}MB",
    ).__dict__, 413


@app.errorhandler(404)
def not_found(e):
    return ErrorResponse(
        error="Endpoint no encontrado", message="La ruta solicitada no existe"
    ).__dict__, 404


@app.errorhandler(500)
def internal_error(e):
    return ErrorResponse(
        error="Error interno", message="Error interno del servidor"
    ).__dict__, 500
