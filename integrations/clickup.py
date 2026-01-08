"""
Integração com ClickUp
"""
from typing import Dict, List, Optional
import requests
from config import Config


class ClickUpIntegration:
    """Classe para integração com ClickUp"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a integração com ClickUp
        
        Args:
            api_key: Chave da API ClickUp (usa a configurada se não fornecida)
        """
        self.api_key = api_key or Config.CLICKUP_API_KEY
        if not self.api_key:
            raise ValueError("Chave da API ClickUp não configurada")
        
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        self.team_id = Config.CLICKUP_TEAM_ID
        self.space_id = Config.CLICKUP_SPACE_ID
        self.list_id = Config.CLICKUP_LIST_ID
    
    def create_task(
        self,
        name: str,
        description: str,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        assignees: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Cria uma nova tarefa no ClickUp
        
        Args:
            name: Nome da tarefa
            description: Descrição da tarefa
            status: Status inicial (opcional)
            priority: Prioridade (1=urgente, 2=alta, 3=normal, 4=baixa)
            assignees: Lista de IDs de usuários para atribuir
            tags: Lista de tags
            custom_fields: Campos customizados
            
        Returns:
            Dados da tarefa criada
        """
        url = f"{self.base_url}/list/{self.list_id}/task"
        
        payload = {
            "name": name,
            "description": description,
        }
        
        if status:
            payload["status"] = status
        if priority:
            payload["priority"] = priority
        if assignees:
            payload["assignees"] = assignees
        if tags:
            payload["tags"] = tags
        if custom_fields:
            payload["custom_fields"] = custom_fields
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao criar tarefa no ClickUp: {e}")
            if hasattr(e.response, 'text'):
                print(f"Resposta do servidor: {e.response.text}")
            raise
    
    def create_task_from_analysis(
        self,
        analysis: Dict,
        task_description: str,
        response_id: Optional[str] = None
    ) -> Dict:
        """
        Cria uma tarefa no ClickUp baseada na análise do ChatGPT
        
        Args:
            analysis: Análise gerada pelo ChatGPT
            task_description: Descrição formatada da tarefa
            response_id: ID da resposta original (para rastreamento)
            
        Returns:
            Dados da tarefa criada
        """
        info = analysis.get('informacoes_extraidas', {})
        tipo_lead = analysis.get('tipo_lead', 'Lead')
        prioridade = analysis.get('prioridade', 'média')
        
        # Mapeia prioridade para número do ClickUp
        priority_map = {
            'alta': 2,
            'média': 3,
            'baixa': 4
        }
        priority = priority_map.get(prioridade.lower(), 3)
        
        # Nome da tarefa
        nome_cliente = info.get('nome', 'Cliente')
        task_name = f"[{tipo_lead}] {nome_cliente}"
        
        # Tags
        tags = [tipo_lead.lower()]
        if info.get('tipo_imovel'):
            tags.append(info['tipo_imovel'].lower())
        
        # Adiciona ID da resposta como referência
        if response_id:
            task_description += f"\n\n**ID da Resposta:** {response_id}"
        
        return self.create_task(
            name=task_name,
            description=task_description,
            priority=priority,
            tags=tags
        )
    
    def update_task(self, task_id: str, updates: Dict) -> Dict:
        """
        Atualiza uma tarefa existente
        
        Args:
            task_id: ID da tarefa
            updates: Dicionário com campos a atualizar
            
        Returns:
            Dados atualizados da tarefa
        """
        url = f"{self.base_url}/task/{task_id}"
        
        try:
            response = requests.put(url, json=updates, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao atualizar tarefa no ClickUp: {e}")
            raise
    
    def get_task(self, task_id: str) -> Dict:
        """
        Obtém dados de uma tarefa
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Dados da tarefa
        """
        url = f"{self.base_url}/task/{task_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter tarefa do ClickUp: {e}")
            raise


