import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, config):
        self.config = config
        self.enabled = config.enabled

    def test_connection(self):
        """Probar conexión SMTP"""
        if not self.enabled:
            return False, "Email desactivado"

        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.username, self.config.password)
            return True, "Conexión exitosa"
        except Exception as e:
            logger.error(f"Error SMTP: {e}")
            return False, str(e)

    def send_plate_detection_notification(
        self,
        to_email: str,
        plate_data: dict,
        attach_image: Optional[bytes] = None,
        image_filename: str = "placa.jpg",
    ) -> bool:
        """Enviar notificación con imagen adjunta"""
        if not self.enabled:
            logger.info("Email desactivado, omitiendo notificación")
            return False

        try:
            message = MIMEMultipart()
            message["From"] = self.config.from_email
            message["To"] = to_email
            message["Subject"] = "🚗 Placa Detectada - Sistema de Reconocimiento"

            # Cuerpo del mensaje
            body = self._create_email_body(plate_data)
            message.attach(MIMEText(body, "plain"))

            # Adjuntar imagen si se proporciona
            if attach_image:
                attachment = MIMEApplication(attach_image, Name=image_filename)
                attachment["Content-Disposition"] = (
                    f'attachment; filename="{image_filename}"'
                )
                message.attach(attachment)

            # Enviar email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(message)

            logger.info(f"✅ Email enviado a {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            return False

    def _create_email_body(self, plate_data: dict) -> str:
        """Crear cuerpo del email"""
        return f"""
Sistema de Reconocimiento de Placas

Se ha detectado una placa vehicular:

INFORMACIÓN:
- Placa: {plate_data.get("plate_number", "N/A")}
- Estado: {plate_data.get("status", "N/A")}
- Fecha: {plate_data.get("timestamp", "N/A")}

Este es un mensaje automático.
"""
