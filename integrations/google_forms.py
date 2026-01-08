"""
Integração com Google Forms
"""
import json
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config


class GoogleFormsIntegration:
    """Classe para integração com Google Forms"""
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """
        Inicializa a integração com Google Forms
        
        Args:
            credentials: Credenciais OAuth2 do Google (opcional)
        """
        self.credentials = credentials
        self.service = None
        if credentials:
            self.service = build('forms', 'v1', credentials=credentials)
    
    def get_form_responses(self, form_id: Optional[str] = None) -> List[Dict]:
        """
        Obtém todas as respostas de um formulário
        
        Args:
            form_id: ID do formulário (usa o configurado se não fornecido)
            
        Returns:
            Lista de respostas do formulário
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Configure as credenciais primeiro.")
        
        form_id = form_id or Config.GOOGLE_FORMS_FORM_ID
        if not form_id:
            raise ValueError("ID do formulário não fornecido")
        
        try:
            form = self.service.forms().get(formId=form_id).execute()
            responses = self.service.forms().responses().list(formId=form_id).execute()
            
            return responses.get('responses', [])
        except HttpError as error:
            print(f"Erro ao obter respostas do formulário: {error}")
            return []
    
    def get_new_responses(self, form_id: Optional[str] = None, last_sync: Optional[str] = None) -> List[Dict]:
        """
        Obtém apenas respostas novas desde a última sincronização
        
        Args:
            form_id: ID do formulário
            last_sync: Timestamp da última sincronização (ISO format)
            
        Returns:
            Lista de novas respostas
        """
        all_responses = self.get_form_responses(form_id)
        
        if not last_sync:
            return all_responses
        
        # Filtra respostas mais recentes que last_sync
        new_responses = [
            resp for resp in all_responses
            if resp.get('lastSubmittedTime', '') > last_sync
        ]
        
        return new_responses
    
    def format_response_data(self, response: Dict) -> Dict:
        """
        Formata os dados de uma resposta para um formato padronizado
        
        Args:
            response: Resposta bruta do Google Forms
            
        Returns:
            Dados formatados
        """
        formatted = {
            'response_id': response.get('responseId'),
            'submission_time': response.get('lastSubmittedTime'),
            'answers': {}
        }
        
        # Processa as respostas
        answers = response.get('answers', {})
        for question_id, answer_data in answers.items():
            answer = answer_data.get('textAnswers', {}).get('answers', [{}])[0]
            formatted['answers'][question_id] = answer.get('value', '')
        
        return formatted


