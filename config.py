import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.getenv('FLASK_ENV') == 'development':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev.db')
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'comprovantes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}

    SSW_API_PASSWORD_TG = os.getenv("SSW_API_PASSWORD_TG")
    SSW_API_PASSWORD_AMPLA = os.getenv("SSW_API_PASSWORD_AMPLA")
    SSW_BASE_URL = os.getenv("SSW_BASE_URL")

    BRASPRESS_BASE_URL = os.getenv("BRASPRESS_BASE_URL")
    BRASPRESS_USER_1 = os.getenv("BRASPRESS_USER_1")
    BRASPRESS_PASS_1 = os.getenv("BRASPRESS_PASS_1")
    BRASPRESS_AUTH_BASE64_1 = os.getenv("BRASPRESS_AUTH_BASE64_1")

    BRASPRESS_USER_2 = os.getenv("BRASPRESS_USER_2")
    BRASPRESS_PASS_2 = os.getenv("BRASPRESS_PASS_2")
    BRASPRESS_AUTH_BASE64_2 = os.getenv("BRASPRESS_AUTH_BASE64_2")

    BRASPRESS_USER_3 = os.getenv("BRASPRESS_USER_3")
    BRASPRESS_PASS_3 = os.getenv("BRASPRESS_PASS_3")
    BRASPRESS_AUTH_BASE64_3 = os.getenv("BRASPRESS_AUTH_BASE64_3")

    MIX_LOGIN_URL = os.getenv("MIX_LOGIN_URL")
    MIX_USER = os.getenv("MIX_USER")
    MIX_PASS = os.getenv("MIX_PASS")
    MIX_TRACKING_URL = os.getenv("MIX_TRACKING_URL")

    EVS_LOGIN_URL = os.getenv("EVS_LOGIN_URL")
    EVS_USER = os.getenv("EVS_USER")
    EVS_PASS = os.getenv("EVS_PASS")
    EVS_SIGLA = os.getenv("EVS_SIGLA")
    EVS_BASE_API_URL = os.getenv("EVS_BASE_API_URL")
    EVS_API_VERSION = os.getenv("EVS_API_VERSION")

    TARGG_LOGIN_URL = os.getenv("TARGG_LOGIN_URL")
    TARGG_USER = os.getenv("TARGG_USER")
    TARGG_PASS = os.getenv("TARGG_PASS")
    TARGG_TRACKING_URL = os.getenv("TARGG_TRACKING_URL")

    TM_LOGIN_URL = os.getenv("TM_LOGIN_URL")
    TM_USER = os.getenv("TM_USER")
    TM_PSS = os.getenv("TM_PSS")
    TM_TRACKING_URL = os.getenv("TM_TRACKING_URL")

    ACETTE_LOGIN_URL = os.getenv("ACETTE_LOGIN_URL")
    ACETTE_USER = os.getenv("ACETTE_USER")
    ACETTE_PASS = os.getenv("ACETTE_PASS")
    ACETTE_TRACKING_URL = os.getenv("ACETTE_TRACKING_URL")

    COMPROVANTE_BRUDAM = os.getenv("&comprovante=1")

    BSB_LOGIN_URL = os.getenv("BSB_LOGIN_URL")
    BSB_ID_AMBIENTE = os.getenv("BSB_ID_AMBIENTE")
    BSB_PSS = os.getenv("BSB_PSS")
    BSB_USER = os.getenv("BSB_USER")

    LOG_FILE = os.path.join(os.getcwd(), 'logs', 'app.log')
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'comprovantes')
    COMPROVANTES_DIR = os.path.join(os.getcwd(), 'comprovantes_entregas')

    COMPROVANTES_DIR = os.path.join(os.getcwd(), 'comprovantes_entregas')

    if not os.path.exists(COMPROVANTES_DIR):
        os.makedirs(COMPROVANTES_DIR)

    FILIAL_CNPJ_MAP = {
        1: os.getenv("FILIAL_1"),
        2: os.getenv("FILIAL_2"),
        3: os.getenv("FILIAL_3"),
    }

config = Config()
    