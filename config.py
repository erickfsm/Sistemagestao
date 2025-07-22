import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = True

    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'chave-secreta')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'chave-secreta-jwt')

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'comprovantes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)