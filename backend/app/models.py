from dataclasses import dataclass
from typing import Optional


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    enabled: bool = True


@dataclass
class PlateResponse:
    plate_number: str
    status: str
    timestamp: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    notification_sent: Optional[bool] = None


@dataclass
class ErrorResponse:
    error: str
    message: str
