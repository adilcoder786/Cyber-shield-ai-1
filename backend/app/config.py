"""
Central configuration for CyberShield AI backend.
All secrets/config are loaded from environment variables (.env file).
Never hardcode credentials or API keys here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend/ root regardless of current working directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # --- App ---
    APP_NAME: str = "CyberShield AI"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # --- Security ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-insecure-secret-change-me")
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # --- Database (MySQL) ---
    # Falls back to a local SQLite file ONLY if USE_SQLITE_FALLBACK=true, so the
    # project can still be demoed instantly on a machine without MySQL installed.
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "cybershield_ai")
    USE_SQLITE_FALLBACK: bool = os.getenv("USE_SQLITE_FALLBACK", "false").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        if self.USE_SQLITE_FALLBACK:
            return f"sqlite:///{BASE_DIR / 'cybershield_demo.db'}"
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # --- Threat Intelligence (optional, external APIs) ---
    # If keys are missing/blank, the platform automatically runs in
    # "offline heuristic mode" so the demo always works without internet.
    GOOGLE_SAFE_BROWSING_API_KEY: str = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")

    # --- Upload limits ---
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    ALLOWED_UPLOAD_EXTENSIONS: set = {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar", ".7z",
        ".exe", ".js", ".vbs", ".bat", ".sh", ".jar", ".apk", ".txt",
        ".png", ".jpg", ".jpeg", ".html", ".htm", ".msi", ".ps1", ".lnk", ".iso",
    }


settings = Settings()
