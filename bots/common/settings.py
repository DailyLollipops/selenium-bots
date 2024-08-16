from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    HUB_PORT: int = os.getenv('HUB_PORT') or 4444
    HUB_URL: str = f'http://selenium-hub:{HUB_PORT}/wd/hub'
    LOG_DIR: str = os.getenv('LOG_DIR') or '/usr/src/selenium-bots/logs'
    DOWNLOAD_DIR: str = os.getenv('DOWNLOAD_DIR') or 'temp/downloads'
    PROXYMESH_USERNAME: str = os.getenv('PROXYMESH_USERNAME') or ''
    PROXYMESH_PASSWORD: str = os.getenv('PROXYMESH_PASSWORD') or ''

settings = Settings()
