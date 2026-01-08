"""
Integração com ChatGPT/OpenAI
"""
import json
from typing import Dict, List, Optional
from openai import OpenAI
from config import Config


class ChatGPTIntegration:
    """Classe para integração com ChatGPT/OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a integração com ChatGPT
        
        Args:
            api_key: Chave da API OpenAI (usa a configurada se não fornecida)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("Chave da API OpenAI não configurada")
        
        # Inicializa cliente OpenAI
        # Nota: Se der erro de 'proxies', pode ser incompatibilidade de versão
        # Solução: Atualizar openai e httpx ou usar versões compatíveis
        try:
            self.client = OpenAI(api_key=self.api_key)
        except TypeError as e:
            if 'proxies' in str(e):
                # Erro conhecido: versão incompatível de openai/httpx
                # Tenta inicializar de forma mais básica
                import importlib
                import sys
                # Remove httpx se estiver causando problema
                if 'httpx' in sys.modules:
                    # Tenta recarregar sem proxies
                    pass
                raise ValueError(
                    f"Erro de compatibilidade OpenAI/httpx: {e}\n"
                    "Solução: Execute: pip install --upgrade 'openai>=1.12.0' 'httpx>=0.27.0'"
                )
            else:
                raise
        
        self.model = Config.CHATGPT_MODEL
    
    def analyze_form_data(self, form_data: Dict, context: Optional[str] = None) -> Dict:
        """
        Analisa dados de formulário usando ChatGPT
        
        Args:
            form_data: Dados do formulário a serem analisados
            context: Contexto adicional para a análise (opcional)
            
        Returns:
            Análise estruturada dos dados
        """
        prompt = self._build_analysis_prompt(form_data, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em análise de dados imobiliários. "
                                 "Analise os dados fornecidos e extraia informações relevantes de forma estruturada."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Erro ao analisar dados com ChatGPT: {e}")
            return {"error": str(e), "raw_data": form_data}
    
    def _build_analysis_prompt(self, form_data: Dict, context: Optional[str] = None) -> str:
        """Constrói o prompt para análise"""
        prompt = f"""
Analise os seguintes dados de formulário imobiliário e extraia informações estruturadas:

Dados do formulário:
{json.dumps(form_data, indent=2, ensure_ascii=False)}

Por favor, forneça uma análise em JSON com a seguinte estrutura:
{{
    "tipo_lead": "tipo identificado (comprador, vendedor, locatário, etc)",
    "prioridade": "alta/média/baixa",
    "categoria": "categoria do imóvel ou serviço",
    "resumo": "resumo breve da solicitação",
    "informacoes_extraidas": {{
        "nome": "nome do cliente",
        "telefone": "telefone",
        "email": "email",
        "tipo_imovel": "casa/apartamento/terreno/etc",
        "localizacao": "localização desejada",
        "orcamento": "orçamento se mencionado",
        "observacoes": "observações relevantes"
    }},
    "acoes_sugeridas": ["ação 1", "ação 2", "ação 3"]
}}
"""
        if context:
            prompt += f"\n\nContexto adicional: {context}"
        
        return prompt
    
    def generate_task_description(self, analysis: Dict) -> str:
        """
        Gera uma descrição de tarefa baseada na análise
        
        Args:
            analysis: Resultado da análise do ChatGPT
            
        Returns:
            Descrição formatada para tarefa
        """
        info = analysis.get('informacoes_extraidas', {})
        resumo = analysis.get('resumo', 'Nova solicitação recebida')
        
        description = f"""
{resumo}

**Tipo de Lead:** {analysis.get('tipo_lead', 'Não identificado')}
**Prioridade:** {analysis.get('prioridade', 'Média')}

**Informações do Cliente:**
- Nome: {info.get('nome', 'Não informado')}
- Telefone: {info.get('telefone', 'Não informado')}
- Email: {info.get('email', 'Não informado')}

**Detalhes:**
- Tipo de Imóvel: {info.get('tipo_imovel', 'Não especificado')}
- Localização: {info.get('localizacao', 'Não especificada')}
- Orçamento: {info.get('orcamento', 'Não informado')}

**Observações:**
{info.get('observacoes', 'Nenhuma observação adicional')}

**Ações Sugeridas:**
{chr(10).join(f'- {acao}' for acao in analysis.get('acoes_sugeridas', []))}
"""
        return description.strip()
    
    def process_batch(self, form_responses: List[Dict]) -> List[Dict]:
        """
        Processa múltiplas respostas de formulário
        
        Args:
            form_responses: Lista de respostas do formulário
            
        Returns:
            Lista de análises processadas
        """
        results = []
        for response in form_responses:
            analysis = self.analyze_form_data(response)
            results.append({
                'response_id': response.get('response_id'),
                'analysis': analysis,
                'task_description': self.generate_task_description(analysis)
            })
        return results


