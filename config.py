"""
Configurações do sistema de integração para imobiliária
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações gerais da aplicação"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Google APIs
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/callback')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    GOOGLE_FORMS_FORM_ID = os.getenv('GOOGLE_FORMS_FORM_ID')
    
    # OpenAI/ChatGPT
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CHATGPT_MODEL = os.getenv('CHATGPT_MODEL', 'gpt-4o-mini')  # Modelo atualizado
    
    # ClickUp
    CLICKUP_API_KEY = os.getenv('CLICKUP_API_KEY')
    CLICKUP_TEAM_ID = os.getenv('CLICKUP_TEAM_ID')
    CLICKUP_SPACE_ID = os.getenv('CLICKUP_SPACE_ID')
    CLICKUP_LIST_ID = os.getenv('CLICKUP_LIST_ID')
    
    # Chaves na Mão
    CHAVES_NA_MAO_API_KEY = os.getenv('CHAVES_NA_MAO_API_KEY')
    CHAVES_NA_MAO_API_URL = os.getenv('CHAVES_NA_MAO_API_URL', 'https://api.chavesnamao.com.br')
    
    # Wasseller (nova API - usa apenas token)
    WASSELLER_TOKEN = os.getenv('WASSELLER_TOKEN')
    WASSELLER_API_URL = os.getenv('WASSELLER_API_URL', 'https://api.waseller.com.br')
    # Mantido para compatibilidade com código antigo
    WASSELLER_API_KEY = os.getenv('WASSELLER_API_KEY')
    WASSELLER_INSTANCE_ID = os.getenv('WASSELLER_INSTANCE_ID')
    
    # Email Fallback (quando Wasseller está indisponível)
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')  # Lista separada por vírgula
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///imobiliaria.db')
    
    # Formulários Google Forms (múltiplos)
    @classmethod
    def get_forms_config(cls):
        """Carrega configuração de formulários do arquivo JSON"""
        forms_config_path = os.path.join(os.path.dirname(__file__), 'forms_config.json')
        try:
            if os.path.exists(forms_config_path):
                with open(forms_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar forms_config.json: {e}")
        return {"forms": []}
    
    @classmethod
    def get_form_ids(cls):
        """Retorna lista de IDs dos formulários configurados"""
        config = cls.get_forms_config()
        return [form['id'] for form in config.get('forms', [])]
    
    @classmethod
    def get_form_by_id(cls, form_id: str):
        """Retorna configuração de um formulário específico"""
        config = cls.get_forms_config()
        for form in config.get('forms', []):
            if form['id'] == form_id:
                return form
        return None
    
    @classmethod
    def validate(cls):
        """Valida se as configurações essenciais estão presentes"""
        required = [
            'OPENAI_API_KEY',
            'CLICKUP_API_KEY',
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET'
        ]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Configurações faltando: {', '.join(missing)}")
        return True


