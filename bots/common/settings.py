from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    HUB_URL: str = os.getenv('HUB_URL') or 'http://selenium-hub:4444/wd/hub'
    LOG_DIR: str = os.getenv('LOG_DIR') or '/usr/src/selenium-bots/logs'
    PROXYMESH_USERNAME: str = os.getenv('PROXYMESH_USERNAME') or ''
    PROXYMESH_PASSWORD: str = os.getenv('PROXYMESH_PASSWORD') or ''

settings = Settings()
