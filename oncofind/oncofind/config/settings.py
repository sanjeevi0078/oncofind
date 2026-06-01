from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for oncofind, loaded from env variables or defaults."""
    
    model_config = SettingsConfigDict(
        env_prefix="ONCOFIND_",
        case_sensitive=False,
    )
    
    data_dir: Path = Path.home() / ".oncofind" / "data"
    cache_dir: Path = Path.home() / ".oncofind" / "cache"
    output_dir: Path = Path("./oncofind_results")
    gdc_api_url: str = "https://api.gdc.cancer.gov"
    
    def create_dirs(self) -> None:
        """Create configuration directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
