"""Application configuration using pydantic-settings.

This module defines the Settings class that loads configuration from environment
variables and .env files. All settings are validated using Pydantic.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables can be defined in a .env file or set directly.
    See .env.example for all available configuration options.
    """

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string with asyncpg driver",
        examples=["postgresql+asyncpg://user:password@host:5432/database"],
    )
    database_pool_size: int = Field(
        default=10, description="Number of connections to maintain in the pool", ge=1, le=100
    )
    database_max_overflow: int = Field(
        default=20,
        description="Maximum number of connections that can be created beyond pool_size",
        ge=0,
        le=100,
    )

    # Application Environment
    app_env: str = Field(
        default="development",
        description="Application environment: development, production, or test",
        pattern="^(development|production|test)$",
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    log_format: str = Field(
        default="json",
        description="Log format: json (structured) or text (human-readable)",
        pattern="^(json|text)$",
    )
    log_file: str | None = Field(
        default=None,
        description="Optional log file path for file-based logging (None = stdout only)",
    )
    log_rotation: str = Field(
        default="100 MB",
        description="Log file rotation size (e.g., '100 MB', '1 GB')",
    )
    log_retention: str = Field(
        default="30 days",
        description="Log file retention period (e.g., '30 days', '1 week')",
    )

    # API Server Configuration
    api_host: str = Field(default="0.0.0.0", description="Host address for the API server")
    api_port: int = Field(
        default=8000, description="Port number for the API server", ge=1, le=65535
    )

    # Authentication Configuration
    better_auth_secret: str = Field(
        ...,
        description="Shared secret for JWT token signing and verification (must match frontend)",
        min_length=32,
        examples=["your-super-secret-key-change-this-in-production-min-32-chars"],
    )

    # CORS Configuration
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend application URL for CORS configuration",
        examples=["http://localhost:3000", "https://app.example.com"],
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials (cookies, authorization headers) in CORS requests",
    )
    cors_max_age: int = Field(
        default=3600,
        description="Maximum time (seconds) browsers can cache CORS preflight responses",
        ge=0,
        le=86400,
    )

    # MCP Server Configuration
    mcp_server_enabled: bool = Field(
        default=True,
        description="Enable MCP server for AI agent tools"
    )
    mcp_server_port: int = Field(
        default=8001,
        description="Port for MCP server",
        ge=1,
        le=65535
    )
    mcp_tool_timeout: int = Field(
        default=30000,
        description="Tool execution timeout in milliseconds",
        ge=1000,
        le=300000
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.app_env == "test"

    def get_log_config(self) -> dict:
        """Get logging configuration based on environment.

        Returns:
            dict: Logging configuration for structlog or standard logging

        Example:
            config = settings.get_log_config()
            logging.config.dictConfig(config)
        """
        # Base configuration
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
                "text": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": self.log_format,
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "uvicorn": {"level": "INFO", "propagate": True},
                "uvicorn.access": {"level": "INFO", "propagate": True},
                "sqlalchemy.engine": {
                    "level": "WARNING" if self.is_production else "INFO",
                    "propagate": True,
                },
            },
        }

        # Add file handler if log_file is specified
        if self.log_file:
            log_config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": self.log_format,
                "filename": self.log_file,
                "maxBytes": self._parse_size(self.log_rotation),
                "backupCount": 10,
            }
            log_config["root"]["handlers"].append("file")

        return log_config

    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes.

        Args:
            size_str: Size string (e.g., '100 MB', '1 GB')

        Returns:
            int: Size in bytes
        """
        units = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
        parts = size_str.strip().split()
        if len(parts) == 2:
            number, unit = parts
            return int(float(number) * units.get(unit.upper(), 1))
        return int(size_str)  # Assume bytes if no unit


# Global settings instance
settings = Settings()
