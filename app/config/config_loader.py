import os
import yaml
from dotenv import load_dotenv
from app.config.config_schema import AppConfig, PersonioConfig, ExportConfig, ScheduleConfig, LoggingConfig
from app.utils.errors import ConfigError

def load_config(config_path: str = "config.yml") -> AppConfig:
    """Loads configuration from environment variables and YAML file."""
    # Load .env file if it exists
    load_dotenv()
    
    # 1. Load Environment Variables (Mandatory secrets)
    client_id = os.getenv("PERSONIO_CLIENT_ID")
    client_secret = os.getenv("PERSONIO_CLIENT_SECRET")
    base_url = os.getenv("PERSONIO_BASE_URL", "https://api.personio.de")
    export_output_path = os.getenv("EXPORT_OUTPUT_PATH")
    
    if not client_id or not client_secret:
        raise ConfigError("Missing mandatory environment variables: PERSONIO_CLIENT_ID or PERSONIO_CLIENT_SECRET")
    
    personio_cfg = PersonioConfig(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url
    )
    
    # 2. Load YAML Config
    if not os.path.exists(config_path):
        # Return default config if yaml is missing
        return AppConfig(personio=personio_cfg)
        
    try:
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f) or {}
    except Exception as e:
        raise ConfigError(f"Failed to parse config file {config_path}: {e}")
    
    # Parse sections
    export_data = yaml_data.get("export", {})
    schedule_data = yaml_data.get("schedule", {})
    logging_data = yaml_data.get("logging", {})
    
    return AppConfig(
        personio=personio_cfg,
        export=ExportConfig(
            output_path=export_output_path or export_data.get("output_path", "./output"),
            include_documents=export_data.get("include_documents", True)
        ),
        schedule=ScheduleConfig(
            enabled=schedule_data.get("enabled", True),
            cron=schedule_data.get("cron", "0 2 * * *")
        ),
        logging=LoggingConfig(
            level=logging_data.get("level", "INFO")
        )
    )
