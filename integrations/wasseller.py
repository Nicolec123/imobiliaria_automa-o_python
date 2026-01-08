"""
Integração com Waseller (WhatsApp)
API atualizada - usa apenas token (não precisa de API Key ou Instance ID)
"""
from typing import Dict, List, Optional
import requests
import json
import os
from config import Config


class WassellerIntegration:
    """Classe para integração com Waseller para WhatsApp"""
    
    def __init__(self, token: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa a integração com Waseller
        
        Args:
            token: Token da API Waseller (usa o configurado se não fornecido)
            api_url: URL base da API (usa a configurada se não fornecida)
        """
        # Prioriza token (nova API), mas mantém compatibilidade com api_key antiga
        self.token = token or Config.WASSELLER_TOKEN or Config.WASSELLER_API_KEY
        self.api_url = (api_url or Config.WASSELLER_API_URL).rstrip('/')
        
        if not self.token:
            raise ValueError("Token Waseller não configurado. Configure WASSELLER_TOKEN no .env")
        
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Carrega configuração de grupos e exceções
        self.config = self._load_config()
    
    def send_message(
        self,
        phone_number: str,
        message: str,
        instance_id: Optional[str] = None  # Mantido para compatibilidade, mas não é usado
    ) -> Dict:
        """
        Envia uma mensagem via WhatsApp usando a API Waseller
        
        Args:
            phone_number: Número de telefone (formato: 5511999999999)
            message: Mensagem a ser enviada
            instance_id: Ignorado (mantido para compatibilidade)
            
        Returns:
            Resposta da API com formato:
            {
                "success": true/false,
                "message": "Mensagem enviada com sucesso" ou mensagem de erro
            }
        """
        # Remove caracteres não numéricos do telefone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Garante que o telefone tenha DDI (55 para Brasil)
        if not phone_number.startswith('55'):
            phone_number = '55' + phone_number
        
        # Endpoint da nova API: /api/enviar-texto/{token}
        url = f"{self.api_url}/api/enviar-texto/{self.token}"
        
        payload = {
            "phone": phone_number,
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            
            # Trata diferentes códigos de status conforme documentação
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json() if response.text else {}
                raise ValueError(f"Erro na requisição: {error_data.get('message', 'phone e message são obrigatórios')}")
            elif response.status_code == 404:
                error_data = response.json() if response.text else {}
                raise ValueError(f"Token inválido: {error_data.get('message', 'Token não cadastrado')}")
            elif response.status_code == 501:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('message', 'Página do Whatsapp não aberta ou API desconectada.')
                raise ValueError(
                    f"WhatsApp desconectado: {error_msg}\n"
                    f"⚠️  AÇÃO NECESSÁRIA: Acesse o painel Waseller e conecte/autentique o WhatsApp.\n"
                    f"   O token está válido, mas o WhatsApp precisa estar online no painel para enviar mensagens."
                )
            else:
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar mensagem via Waseller: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta do servidor: {e.response.text}")
            raise
    
    def send_template_message(
        self,
        phone_number: str,
        template_name: str,
        parameters: List[str],
        instance_id: Optional[str] = None  # Mantido para compatibilidade
    ) -> Dict:
        """
        Envia uma mensagem de template via WhatsApp
        
        NOTA: A API atual do Waseller não suporta templates diretamente.
        Este método constrói uma mensagem formatada com os parâmetros.
        
        Args:
            phone_number: Número de telefone
            template_name: Nome do template (usado apenas para referência)
            parameters: Lista de parâmetros para inserir na mensagem
            instance_id: Ignorado (mantido para compatibilidade)
            
        Returns:
            Resposta da API
        """
        # Constrói mensagem formatada com parâmetros
        message = template_name
        for i, param in enumerate(parameters):
            message = message.replace(f"{{{i}}}", str(param))
        
        # Usa send_message para enviar
        return self.send_message(phone_number, message)
    
    def send_welcome_message(self, analysis: Dict, form_data: Optional[Dict] = None) -> Dict:
        """
        Envia mensagem de boas-vindas baseada na análise
        
        Args:
            analysis: Análise gerada pelo ChatGPT
            form_data: Dados originais do formulário (opcional)
            
        Returns:
            Resposta da API
        """
        info = analysis.get('informacoes_extraidas', {})
        telefone = info.get('telefone', '')
        nome = info.get('nome', 'Cliente')
        
        if not telefone:
            raise ValueError("Telefone não encontrado nos dados")
        
        # Remove caracteres não numéricos e adiciona código do país se necessário
        telefone = ''.join(filter(str.isdigit, telefone))
        if not telefone.startswith('55'):  # Código do Brasil
            telefone = '55' + telefone
        
        message = f"""
Olá {nome}! 👋

Obrigado por entrar em contato conosco!

Recebemos sua solicitação e nossa equipe já está analisando suas necessidades.

Em breve entraremos em contato para dar continuidade ao seu atendimento.

Atenciosamente,
Equipe Imobiliária
"""
        
        return self.send_message(telefone, message.strip())
    
    def send_notification_to_team(
        self,
        team_phone: str,
        analysis: Dict,
        response_id: str
    ) -> Dict:
        """
        Envia notificação para a equipe sobre novo lead
        
        Args:
            team_phone: Telefone da equipe
            analysis: Análise do lead
            response_id: ID da resposta
            
        Returns:
            Resposta da API
        """
        info = analysis.get('informacoes_extraidas', {})
        
        message = f"""
🔔 NOVO LEAD RECEBIDO

ID: {response_id}
Nome: {info.get('nome', 'Não informado')}
Telefone: {info.get('telefone', 'Não informado')}
Tipo: {analysis.get('tipo_lead', 'Lead')}
Prioridade: {analysis.get('prioridade', 'Média')}

Ação: Verificar no ClickUp
"""
        
        telefone = ''.join(filter(str.isdigit, team_phone))
        if not telefone.startswith('55'):
            telefone = '55' + telefone
        
        return self.send_message(telefone, message.strip())
    
    def _load_config(self) -> Dict:
        """Carrega configuração de grupos e exceções"""
        # Tenta carregar do diretório raiz do projeto
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wasseller_config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar wasseller_config.json: {e}")
        
        # Retorna configuração padrão se arquivo não existir
        return {
            "notificacoes": {
                "grupos": [],
                "pessoas": []
            },
            "excecoes": {
                "telefones_bloqueados": [],
                "grupos_bloqueados": []
            },
            "mensagens": {
                "template_novo_lead": "🔔 NOVO LEAD RECEBIDO\n\nID: {response_id}\nNome: {nome}\nTelefone: {telefone}\nTipo: {tipo_lead}\nPrioridade: {prioridade}\n\nAção: Verificar no ClickUp"
            }
        }
    
    def _is_blocked(self, phone_number: str, group_id: Optional[str] = None) -> bool:
        """
        Verifica se um telefone ou grupo está na lista de exceções
        
        Args:
            phone_number: Número de telefone
            group_id: ID do grupo (opcional)
            
        Returns:
            True se estiver bloqueado, False caso contrário
        """
        excecoes = self.config.get('excecoes', {})
        
        # Normaliza telefone para comparação
        phone_normalized = ''.join(filter(str.isdigit, phone_number))
        if not phone_normalized.startswith('55'):
            phone_normalized = '55' + phone_normalized
        
        # Verifica se telefone está bloqueado
        telefones_bloqueados = excecoes.get('telefones_bloqueados', [])
        for bloqueado in telefones_bloqueados:
            bloqueado_normalized = ''.join(filter(str.isdigit, bloqueado))
            if not bloqueado_normalized.startswith('55'):
                bloqueado_normalized = '55' + bloqueado_normalized
            if phone_normalized == bloqueado_normalized:
                return True
        
        # Verifica se grupo está bloqueado
        if group_id:
            grupos_bloqueados = excecoes.get('grupos_bloqueados', [])
            if group_id in grupos_bloqueados:
                return True
        
        return False
    
    def list_groups(self) -> List[Dict]:
        """
        Lista todos os grupos do WhatsApp conectado
        
        Tenta buscar grupos via API. Se a API não suportar, retorna lista vazia.
        
        Returns:
            Lista de grupos com id e nome
        """
        try:
            # Tenta endpoint comum para listar grupos
            # Formato pode variar: /api/grupos/{token} ou /api/groups/{token}
            endpoints_tentativas = [
                f"{self.api_url}/api/grupos/{self.token}",
                f"{self.api_url}/api/groups/{self.token}",
                f"{self.api_url}/api/listar-grupos/{self.token}",
                f"{self.api_url}/api/list-groups/{self.token}"
            ]
            
            for endpoint in endpoints_tentativas:
                try:
                    response = requests.get(endpoint, headers=self.headers, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # Tenta diferentes formatos de resposta
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict):
                            grupos = data.get('grupos', data.get('groups', data.get('data', [])))
                            if isinstance(grupos, list):
                                return grupos
                        return []
                except:
                    continue
            
            # Se nenhum endpoint funcionou, retorna vazio
            return []
        except Exception as e:
            print(f"Aviso: Não foi possível listar grupos automaticamente: {e}")
            return []
    
    def send_to_groups(
        self,
        message: str,
        group_ids: Optional[List[str]] = None,
        auto_discover: bool = True
    ) -> Dict:
        """
        Envia mensagem para grupos do WhatsApp
        
        Args:
            message: Mensagem a ser enviada
            group_ids: Lista de IDs dos grupos (se None, tenta descobrir automaticamente)
            auto_discover: Se True, tenta descobrir grupos automaticamente se group_ids for None
            
        Returns:
            Resultado com sucessos e falhas
        """
        resultado = {
            'enviados': [],
            'falhas': [],
            'bloqueados': [],
            'total_tentativas': 0
        }
        
        # Se não especificou grupos, tenta descobrir automaticamente ou usa config
        if group_ids is None:
            if auto_discover:
                # Tenta descobrir grupos automaticamente
                grupos_descobertos = self.list_groups()
                if grupos_descobertos:
                    # Extrai IDs dos grupos descobertos
                    group_ids = []
                    for grupo in grupos_descobertos:
                        grupo_id = grupo.get('id') or grupo.get('groupId') or grupo.get('jid')
                        if grupo_id:
                            group_ids.append(grupo_id)
                    
                    if group_ids:
                        print(f"✅ {len(group_ids)} grupos descobertos automaticamente")
            
            # Se ainda não tem grupos, usa os da configuração
            if not group_ids:
                grupos_config = self.config.get('notificacoes', {}).get('grupos', [])
                group_ids = [
                    grupo['id'] 
                    for grupo in grupos_config 
                    if grupo.get('ativo', True)
                ]
        
        resultado['total_tentativas'] = len(group_ids) if group_ids else 0
        
        if not group_ids:
            print("⚠️  Nenhum grupo encontrado para enviar mensagem")
            return resultado
        
        for group_id in group_ids:
            # Verifica se grupo está bloqueado
            if self._is_blocked('', group_id):
                resultado['bloqueados'].append({
                    'grupo': group_id,
                    'motivo': 'Grupo na lista de exceções'
                })
                continue
            
            try:
                # Para grupos, o ID geralmente é o número do grupo
                # A API do Waseller pode usar o mesmo endpoint, mas com formato diferente
                # Se a API suportar grupos diretamente, ajuste aqui
                response = self.send_message(group_id, message)
                resultado['enviados'].append({
                    'grupo': group_id,
                    'response': response
                })
            except Exception as e:
                resultado['falhas'].append({
                    'grupo': group_id,
                    'erro': str(e)
                })
        
        return resultado
    
    def send_to_team(
        self,
        message: str,
        exclude_owner: bool = True,
        owner_phone: Optional[str] = None
    ) -> Dict:
        """
        Envia mensagem para todas as pessoas da equipe configuradas
        
        Args:
            message: Mensagem a ser enviada
            exclude_owner: Se True, não envia para o dono do número (cliente)
            owner_phone: Telefone do dono (para excluir se exclude_owner=True)
            
        Returns:
            Resultado com sucessos e falhas
        """
        resultado = {
            'enviados': [],
            'falhas': [],
            'bloqueados': []
        }
        
        pessoas_config = self.config.get('notificacoes', {}).get('pessoas', [])
        
        for pessoa in pessoas_config:
            if not pessoa.get('ativo', True):
                continue
            
            telefone = pessoa.get('telefone', '')
            nome = pessoa.get('nome', 'Desconhecido')
            
            if not telefone:
                continue
            
            # Normaliza telefone
            telefone_normalized = ''.join(filter(str.isdigit, telefone))
            if not telefone_normalized.startswith('55'):
                telefone_normalized = '55' + telefone_normalized
            
            # Exclui dono se solicitado
            if exclude_owner and owner_phone:
                owner_normalized = ''.join(filter(str.isdigit, owner_phone))
                if not owner_normalized.startswith('55'):
                    owner_normalized = '55' + owner_normalized
                if telefone_normalized == owner_normalized:
                    resultado['bloqueados'].append({
                        'telefone': telefone,
                        'nome': nome,
                        'motivo': 'Dono do número (excluído)'
                    })
                    continue
            
            # Verifica se está bloqueado
            if self._is_blocked(telefone):
                resultado['bloqueados'].append({
                    'telefone': telefone,
                    'nome': nome,
                    'motivo': 'Na lista de exceções'
                })
                continue
            
            try:
                response = self.send_message(telefone, message)
                resultado['enviados'].append({
                    'telefone': telefone,
                    'nome': nome,
                    'response': response
                })
            except Exception as e:
                resultado['falhas'].append({
                    'telefone': telefone,
                    'nome': nome,
                    'erro': str(e)
                })
        
        return resultado
    
    def send_notification_to_all(
        self,
        analysis: Dict,
        response_id: str,
        exclude_owner: bool = True,
        owner_phone: Optional[str] = None,
        auto_discover_groups: bool = True
    ) -> Dict:
        """
        Envia notificação para grupos e equipe sobre novo lead
        
        Args:
            analysis: Análise do lead
            response_id: ID da resposta
            exclude_owner: Se True, não envia para o dono do número
            owner_phone: Telefone do dono (para excluir)
            auto_discover_groups: Se True, tenta descobrir grupos automaticamente
            
        Returns:
            Resultado completo com envios para grupos e equipe
        """
        info = analysis.get('informacoes_extraidas', {})
        
        # Monta mensagem usando template da configuração
        template = self.config.get('mensagens', {}).get('template_novo_lead', 
            "🔔 NOVO LEAD RECEBIDO\n\nID: {response_id}\nNome: {nome}\nTelefone: {telefone}\nTipo: {tipo_lead}\nPrioridade: {prioridade}\n\nAção: Verificar no ClickUp")
        
        message = template.format(
            response_id=response_id,
            nome=info.get('nome', 'Não informado'),
            telefone=info.get('telefone', 'Não informado'),
            tipo_lead=analysis.get('tipo_lead', 'Lead'),
            prioridade=analysis.get('prioridade', 'Média')
        )
        
        resultado_completo = {
            'grupos': {},
            'equipe': {},
            'timestamp': None
        }
        
        # Envia para grupos (tenta descobrir automaticamente se auto_discover_groups=True)
        try:
            # Verifica se deve descobrir automaticamente (padrão da config ou parâmetro)
            auto_discover = auto_discover_groups
            if auto_discover_groups:
                config_auto = self.config.get('notificacoes', {}).get('auto_descobrir_grupos', True)
                auto_discover = config_auto
            
            if auto_discover:
                print("🔍 Tentando descobrir grupos automaticamente...")
            else:
                print("📋 Usando grupos configurados manualmente...")
            
            resultado_grupos = self.send_to_groups(message, auto_discover=auto_discover)
            resultado_completo['grupos'] = resultado_grupos
            
            if resultado_grupos.get('total_tentativas', 0) > 0:
                print(f"📤 Enviado para {len(resultado_grupos.get('enviados', []))} grupos")
                if resultado_grupos.get('falhas'):
                    print(f"⚠️  {len(resultado_grupos.get('falhas', []))} grupos falharam")
        except Exception as e:
            print(f"❌ Erro ao enviar para grupos: {e}")
            resultado_completo['grupos'] = {'erro': str(e)}
        
        # Envia para equipe
        try:
            resultado_equipe = self.send_to_team(message, exclude_owner, owner_phone)
            resultado_completo['equipe'] = resultado_equipe
            
            if resultado_equipe.get('enviados'):
                print(f"📤 Enviado para {len(resultado_equipe.get('enviados', []))} pessoas da equipe")
        except Exception as e:
            print(f"❌ Erro ao enviar para equipe: {e}")
            resultado_completo['equipe'] = {'erro': str(e)}
        
        return resultado_completo


