import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 3000))
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")