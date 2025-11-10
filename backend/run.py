from app.main import app
from app.config import config
from app.email_service import EmailService
from logging import basicConfig, INFO, getLogger

# Configurar logging
basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = getLogger(__name__)


def main():
    """Función principal para iniciar la aplicación"""

    # Mostrar información de configuración
    logger.info("🚀 Iniciando API de Reconocimiento de Placas")
    logger.info("🔧 Configuración cargada:")
    logger.info(f"   • Host: {config.app.host}")
    logger.info(f"   • Puerto: {config.app.port}")
    logger.info(f"   • Debug: {config.app.debug}")
    logger.info(
        f"   • Email: {'✅ Activado' if config.email.enabled else '❌ Desactivado'}"
    )
    logger.info(f"   • OCR Languages: {config.ocr.languages}")
    logger.info(f"   • Tamaño máximo archivo: {config.app.max_file_size}MB")

    # Probar configuración de email si está activado
    if config.email.enabled:
        logger.info("📧 Probando configuración de email...")
        email_service = EmailService(config.email)
        success, message = email_service.test_connection()
        if success:
            logger.info("✅ Email configurado correctamente")
        else:
            logger.warning(f"❌ Error en configuración de email: {message}")
            logger.warning("⚠️  El servicio de email puede no funcionar correctamente")

    # Iniciar aplicación Flask
    logger.info(f"🌐 Servidor iniciando en: http://{config.app.host}:{config.app.port}")
    logger.info(
        f"📚 Documentación disponible en: http://{config.app.host}:{config.app.port}/api/docs/"
    )

    try:
        app.run(debug=config.app.debug, host=config.app.host, port=config.app.port)
    except KeyboardInterrupt:
        logger.info("👋 Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"💥 Error iniciando la aplicación: {e}")
        raise


if __name__ == "__main__":
    main()
