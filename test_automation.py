"""
Script de Testes de Automação para o Sistema de Integração Imobiliária
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from integrations.chatgpt import ChatGPTIntegration
from integrations.chaves_na_mao import ChavesNaMaoIntegration


class TestAutomation:
    """Classe para executar testes automatizados"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': []
        }
    
    def log_test(self, name: str, success: bool, message: str = "", warning: bool = False):
        """Registra resultado de um teste"""
        self.results['total'] += 1
        if success:
            self.results['passed'] += 1
            status = "✅ PASS"
        else:
            self.results['failed'] += 1
            status = "❌ FAIL"
        
        if warning:
            self.results['warnings'].append(f"{name}: {message}")
            status = "⚠️  WARN"
        
        test_result = {
            'name': name,
            'status': status,
            'success': success,
            'message': message,
            'warning': warning
        }
        self.results['tests'].append(test_result)
        print(f"{status} - {name}: {message}")
    
    def test_config_loading(self):
        """Testa carregamento de configurações"""
        print("\n" + "="*60)
        print("TESTE 1: Carregamento de Configurações")
        print("="*60)
        
        try:
            # Testa OpenAI
            if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY.startswith('sk-'):
                self.log_test(
                    "Config - OpenAI API Key",
                    True,
                    f"Chave configurada (inicia com sk-)"
                )
            else:
                self.log_test(
                    "Config - OpenAI API Key",
                    False,
                    "Chave não configurada ou inválida"
                )
            
            # Testa Google Drive
            if Config.GOOGLE_DRIVE_FOLDER_ID:
                self.log_test(
                    "Config - Google Drive Folder ID",
                    True,
                    f"ID configurado: {Config.GOOGLE_DRIVE_FOLDER_ID[:20]}..."
                )
            else:
                self.log_test(
                    "Config - Google Drive Folder ID",
                    False,
                    "ID não configurado"
                )
            
            # Testa formulários
            forms_config = Config.get_forms_config()
            forms_count = len(forms_config.get('forms', []))
            if forms_count > 0:
                self.log_test(
                    "Config - Formulários Google Forms",
                    True,
                    f"{forms_count} formulários configurados"
                )
            else:
                self.log_test(
                    "Config - Formulários Google Forms",
                    False,
                    "Nenhum formulário configurado"
                )
            
            # Testa outras configurações (warnings)
            if not Config.GOOGLE_CLIENT_ID or Config.GOOGLE_CLIENT_ID == 'your_google_client_id':
                self.log_test(
                    "Config - Google Client ID",
                    True,
                    "Não configurado (necessário para Google Forms/Drive)",
                    warning=True
                )
            
            if not Config.CLICKUP_API_KEY or Config.CLICKUP_API_KEY == 'your_clickup_api_key':
                self.log_test(
                    "Config - ClickUp API Key",
                    True,
                    "Não configurado (necessário para ClickUp)",
                    warning=True
                )
            
        except Exception as e:
            self.log_test("Config - Carregamento", False, f"Erro: {str(e)}")
    
    def test_openai_connection(self):
        """Testa conexão com OpenAI"""
        print("\n" + "="*60)
        print("TESTE 2: Conexão com OpenAI/ChatGPT")
        print("="*60)
        
        try:
            if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key':
                self.log_test(
                    "OpenAI - Conexão",
                    False,
                    "API Key não configurada"
                )
                return
            
            chatgpt = ChatGPTIntegration()
            
            # Teste simples de análise
            test_data = {
                'nome': 'João Silva',
                'telefone': '11999999999',
                'email': 'joao@example.com',
                'tipo_imovel': 'Apartamento',
                'localizacao': 'São Paulo'
            }
            
            self.log_test(
                "OpenAI - Inicialização",
                True,
                "Integração inicializada com sucesso"
            )
            
            try:
                analysis = chatgpt.analyze_form_data(test_data)
                if analysis and 'informacoes_extraidas' in analysis:
                    self.log_test(
                        "OpenAI - Análise de Dados",
                        True,
                        f"Análise realizada: {analysis.get('tipo_lead', 'N/A')}"
                    )
                else:
                    self.log_test(
                        "OpenAI - Análise de Dados",
                        False,
                        "Resposta inválida da API"
                    )
            except Exception as e:
                self.log_test(
                    "OpenAI - Análise de Dados",
                    False,
                    f"Erro na análise: {str(e)}"
                )
        
        except Exception as e:
            self.log_test(
                "OpenAI - Conexão",
                False,
                f"Erro: {str(e)}"
            )
    
    def test_xml_parsing(self):
        """Testa processamento de XML do Chaves na Mão"""
        print("\n" + "="*60)
        print("TESTE 3: Processamento XML Chaves na Mão")
        print("="*60)
        
        # XML de exemplo fornecido
        xml_example = """<?xml version="1.0" encoding="UTF-8"?>
<Document>
    <imoveis>
        <imovel>
            <referencia>AP01</referencia>
            <codigo_cliente>AP01</codigo_cliente>
            <link_cliente>https://www.imobiliariateste.com.br/imovel/ap01</link_cliente>
            <titulo>Apartamento Exemplo 01</titulo>
            <transacao>V</transacao>
            <transacao2></transacao2>
            <finalidade>RE</finalidade>
            <finalidade2></finalidade2>
            <destaque>1</destaque>
            <tipo>Apartamento</tipo>
            <tipo2></tipo2>
            <valor>210000</valor>
            <valor_locacao></valor_locacao>
            <valor_iptu></valor_iptu>
            <valor_condominio>560</valor_condominio>
            <area_total>70</area_total>
            <area_util>52</area_util>
            <conservacao></conservacao>
            <quartos>1</quartos>
            <suites>1</suites>
            <garagem>1</garagem>
            <banheiro>2</banheiro>
            <closet>1</closet>
            <salas></salas>
            <despensa></despensa>
            <bar></bar>
            <cozinha>1</cozinha>
            <quarto_empregada></quarto_empregada>
            <escritorio></escritorio>
            <area_servico></area_servico>
            <lareira></lareira>
            <varanda></varanda>
            <lavanderia></lavanderia>
            <aceita_pet>1</aceita_pet>
            <estado>PR</estado>
            <cidade>Curitiba</cidade>
            <bairro>Novo Mundo</bairro>
            <cep>88888888</cep>
            <endereco>Rua demonstração</endereco>
            <numero>250</numero>
            <complemento></complemento>
            <esconder_endereco_imovel>1</esconder_endereco_imovel>
            <descritivo><![CDATA[ Essa é uma breve descrição de teste do imóvel. ]]></descritivo>
            <fotos_imovel>
                <foto>
                    <url>https://www.imobiliariateste.com.br/imovel/imagens/ap01-cozinha.jpeg</url>
                    <data_atualizacao>2023-11-15 17:00:00</data_atualizacao>
                </foto>
                <foto>
                    <url>https://www.imobiliariateste.com.br/imovel/imagens/ap01-sala.jpeg</url>
                    <data_atualizacao>2023-11-15 17:00:00</data_atualizacao>
                </foto>
            </fotos_imovel>
            <data_atualizacao></data_atualizacao>
            <latitude></latitude>
            <longitude></longitude>
            <video></video>
            <tour_360></tour_360>
            <area_comum>
                <item>Academia</item>
                <item>Acessibilidade</item>
            </area_comum>
            <area_privativa>
                <item>Adega</item>
                <item>Aquecedor</item>
            </area_privativa>
            <aceita_troca></aceita_troca>
            <periodo_locacao></periodo_locacao>
        </imovel>
    </imoveis>
</Document>"""
        
        try:
            # Testa parse do XML (sem precisar de API Key)
            chaves = ChavesNaMaoIntegration()
            
            # Remove a validação de API Key temporariamente para teste
            original_api_key = chaves.api_key
            chaves.api_key = "test_key"  # Chave temporária para teste de parse
            
            try:
                property_data = chaves.parse_xml_property(xml_example)
                
                # Valida campos importantes
                required_fields = ['referencia', 'titulo', 'valor', 'cidade', 'estado']
                missing_fields = [f for f in required_fields if f not in property_data]
                
                if not missing_fields:
                    self.log_test(
                        "XML - Parse de Imóvel",
                        True,
                        f"Parse realizado: {property_data.get('referencia')} - {property_data.get('titulo')}"
                    )
                    
                    # Valida tipos de dados
                    if isinstance(property_data.get('valor'), (int, float)):
                        self.log_test(
                            "XML - Tipos de Dados",
                            True,
                            f"Valor convertido corretamente: {property_data.get('valor')}"
                        )
                    else:
                        self.log_test(
                            "XML - Tipos de Dados",
                            False,
                            "Valor não convertido para número"
                        )
                    
                    # Valida fotos
                    if 'fotos' in property_data and len(property_data['fotos']) > 0:
                        self.log_test(
                            "XML - Processamento de Fotos",
                            True,
                            f"{len(property_data['fotos'])} fotos processadas"
                        )
                    else:
                        self.log_test(
                            "XML - Processamento de Fotos",
                            False,
                            "Fotos não processadas"
                        )
                    
                    # Valida áreas comuns/privativas
                    if 'area_comum' in property_data and len(property_data['area_comum']) > 0:
                        self.log_test(
                            "XML - Áreas Comuns",
                            True,
                            f"{len(property_data['area_comum'])} áreas comuns"
                        )
                    
                else:
                    self.log_test(
                        "XML - Parse de Imóvel",
                        False,
                        f"Campos faltando: {', '.join(missing_fields)}"
                    )
                
            except Exception as e:
                self.log_test(
                    "XML - Parse de Imóvel",
                    False,
                    f"Erro no parse: {str(e)}"
                )
            finally:
                chaves.api_key = original_api_key
            
        except Exception as e:
            self.log_test(
                "XML - Processamento",
                False,
                f"Erro: {str(e)}"
            )
    
    def test_forms_config(self):
        """Testa configuração de formulários"""
        print("\n" + "="*60)
        print("TESTE 4: Configuração de Formulários")
        print("="*60)
        
        try:
            forms_config = Config.get_forms_config()
            form_ids = Config.get_form_ids()
            
            if len(form_ids) > 0:
                self.log_test(
                    "Forms - Carregamento",
                    True,
                    f"{len(form_ids)} formulários carregados"
                )
                
                # Testa busca de formulário específico
                first_form_id = form_ids[0]
                form_info = Config.get_form_by_id(first_form_id)
                
                if form_info:
                    self.log_test(
                        "Forms - Busca por ID",
                        True,
                        f"Formulário encontrado: {form_info.get('name', 'N/A')}"
                    )
                else:
                    self.log_test(
                        "Forms - Busca por ID",
                        False,
                        "Formulário não encontrado"
                    )
                
                # Lista todos os formulários
                print("\nFormulários configurados:")
                for form in forms_config.get('forms', []):
                    print(f"  - {form.get('name')}: {form.get('id')}")
                
            else:
                self.log_test(
                    "Forms - Carregamento",
                    False,
                    "Nenhum formulário configurado"
                )
        
        except Exception as e:
            self.log_test(
                "Forms - Configuração",
                False,
                f"Erro: {str(e)}"
            )
    
    def test_integrations_initialization(self):
        """Testa inicialização das integrações"""
        print("\n" + "="*60)
        print("TESTE 5: Inicialização de Integrações")
        print("="*60)
        
        try:
            from orchestrator import IntegrationOrchestrator
            
            orchestrator = IntegrationOrchestrator()
            
            # Testa cada integração
            integrations = {
                'ChatGPT': orchestrator.chatgpt,
                'ClickUp': orchestrator.clickup,
                'Chaves na Mão': orchestrator.chaves_na_mao,
                'Wasseller': orchestrator.wasseller,
            }
            
            for name, integration in integrations.items():
                if integration is not None:
                    self.log_test(
                        f"Integration - {name}",
                        True,
                        "Inicializada com sucesso"
                    )
                else:
                    self.log_test(
                        f"Integration - {name}",
                        False,
                        "Não inicializada"
                    )
            
            # Google Forms e Drive precisam de credenciais OAuth2
            if orchestrator.google_forms is None:
                self.log_test(
                    "Integration - Google Forms",
                    True,
                    "Não inicializada (requer OAuth2)",
                    warning=True
                )
            
            if orchestrator.google_drive is None:
                self.log_test(
                    "Integration - Google Drive",
                    True,
                    "Não inicializada (requer OAuth2)",
                    warning=True
                )
        
        except Exception as e:
            self.log_test(
                "Integration - Inicialização",
                False,
                f"Erro: {str(e)}"
            )
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*60)
        print("INICIANDO TESTES DE AUTOMAÇÃO")
        print("="*60)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Executa todos os testes
        self.test_config_loading()
        self.test_openai_connection()
        self.test_xml_parsing()
        self.test_forms_config()
        self.test_integrations_initialization()
        
        # Resumo final
        print("\n" + "="*60)
        print("RESUMO DOS TESTES")
        print("="*60)
        print(f"Total de testes: {self.results['total']}")
        print(f"✅ Aprovados: {self.results['passed']}")
        print(f"❌ Falharam: {self.results['failed']}")
        print(f"⚠️  Avisos: {len(self.results['warnings'])}")
        
        if self.results['warnings']:
            print("\nAvisos:")
            for warning in self.results['warnings']:
                print(f"  - {warning}")
        
        # Salva resultados em arquivo
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResultados salvos em: {results_file}")
        
        return self.results


if __name__ == '__main__':
    tester = TestAutomation()
    results = tester.run_all_tests()
    
    # Exit code baseado nos resultados
    sys.exit(0 if results['failed'] == 0 else 1)

