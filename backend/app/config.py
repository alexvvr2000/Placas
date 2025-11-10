import configparser
import os
from dataclasses import dataclass
from typing import List


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    enabled: bool


@dataclass
class AppConfig:
    debug: bool
    host: str
    port: int
    max_file_size: int


@dataclass
class OCRConfig:
    languages: List[str]
    confidence_threshold: float


class Config:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.email = None
        self.app = None
        self.ocr = None
        self.load_config()

    def load_config(self):
        """Cargar configuración desde archivo .ini"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(
                    f"Archivo de configuración {self.config_file} no encontrado"
                )

            self.config.read(self.config_file, encoding="utf-8")

            # Configuración de email
            self.email = EmailConfig(
                smtp_server=self.config.get(
                    "email", "smtp_server", fallback="smtp.gmail.com"
                ),
                smtp_port=self.config.getint("email", "smtp_port", fallback=587),
                username=self.config.get("email", "username", fallback=""),
                password=self.config.get("email", "password", fallback=""),
                from_email=self.config.get("email", "from_email", fallback=""),
                enabled=self.config.getboolean("email", "enabled", fallback=False),
            )

            # Configuración de la app
            self.app = AppConfig(
                debug=self.config.getboolean("app", "debug", fallback=True),
                host=self.config.get("app", "host", fallback="0.0.0.0"),
                port=self.config.getint("app", "port", fallback=5000),
                max_file_size=self.config.getint("app", "max_file_size", fallback=16),
            )

            # Configuración de OCR
            languages_str = self.config.get("ocr", "languages", fallback="es,en")
            self.ocr = OCRConfig(
                languages=[lang.strip() for lang in languages_str.split(",")],
                confidence_threshold=self.config.getfloat(
                    "ocr", "confidence_threshold", fallback=0.4
                ),
            )

            print("✅ Configuración cargada correctamente desde config.ini")

        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            self.set_defaults()

    def set_defaults(self):
        """Configuración por defecto en caso de error"""
        self.email = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="",
            password="",
            from_email="",
            enabled=False,
        )
        self.app = AppConfig(debug=True, host="0.0.0.0", port=5000, max_file_size=16)
        self.ocr = OCRConfig(languages=["es", "en"], confidence_threshold=0.4)

    def reload(self):
        """Recargar configuración"""
        self.load_config()


# Instancia global de configuración
config = Config()
