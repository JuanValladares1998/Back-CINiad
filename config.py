import os
from pathlib import Path

# Configuracion basica de rutas y base de datos
BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

DATABASE_URL = "sqlite:///./app.db"
APP_TITLE = "Back-CINiad"

# Anchos maximos para conversion de imagenes
NORMAL_MAX_WIDTH = 1600
CARD_MAX_WIDTH = 480

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
