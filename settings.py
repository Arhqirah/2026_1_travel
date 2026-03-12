import os


class Settings:
    def __init__(self):
        self.FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
        self.SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
        self.MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))


settings = Settings()
