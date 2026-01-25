from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PersonioConfig:
    client_id: str
    client_secret: str
    base_url: str = "https://api.personio.de"

@dataclass
class ExportConfig:
    output_path: str = "./output"
    include_documents: bool = True

@dataclass
class ScheduleConfig:
    enabled: bool = True
    cron: str = "0 2 * * *"

@dataclass
class LoggingConfig:
    level: str = "INFO"

@dataclass
class AppConfig:
    personio: PersonioConfig
    export: ExportConfig = field(default_factory=ExportConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
