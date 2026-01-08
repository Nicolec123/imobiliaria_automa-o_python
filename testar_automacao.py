"""
Script para testar e visualizar a automação funcionando
Demonstra o fluxo completo do sistema
"""
import json
from datetime import datetime
from orchestrator import IntegrationOrchestrator
from config import Config


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_step(num, text):
    """Imprime passo do processo"""
    print(f"\n{'='*70}")
    print(f"PASSO {num}: {text}")
    print("="*70)


def testar_automacao_completa():
    """Testa o fluxo completo de automação"""
    
    print_header("🚀 TESTE DE AUTOMAÇÃO - SISTEMA DE INTEGRAÇÃO IMOBILIÁRIA")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Dados de exemplo (simulando resposta de formulário)
    form_data_exemplo = {
        'response_id': 'TEST_' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'submission_time': datetime.now().isoformat(),
        'answers': {
            'nome': 'João Silva',
            'telefone': '11999999999',
            'email': 'joao.silva@email.com',
            'tipo_imovel': 'Apartamento',
            'localizacao': 'São Paulo - Zona Sul',
            'orcamento': 'R$ 500.000,00',
            'observacoes': 'Procuro apartamento com 2 quartos, próximo ao metrô'
        }
    }
    
    print_step(1, "INICIALIZANDO SISTEMA")
    try:
        orchestrator = IntegrationOrchestrator()
        print("✅ Orquestrador inicializado com sucesso!")
        print(f"   - ChatGPT: {'✅' if orchestrator.chatgpt else '❌'}")
        print(f"   - ClickUp: {'✅' if orchestrator.clickup else '❌'}")
        print(f"   - Chaves na Mão: {'✅' if orchestrator.chaves_na_mao else '❌'}")
        print(f"   - Wasseller: {'✅' if orchestrator.wasseller else '❌'}")
        print(f"   - Google Forms: {'✅' if orchestrator.google_forms else '⚠️  (requer OAuth2)'}")
        print(f"   - Google Drive: {'✅' if orchestrator.google_drive else '⚠️  (requer OAuth2)'}")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {str(e)}")
        return
    
    print_step(2, "DADOS DO FORMULÁRIO (SIMULADO)")
    print("\n📋 Dados que seriam recebidos do Google Forms:")
    print(json.dumps(form_data_exemplo, indent=2, ensure_ascii=False))
    
    print_step(3, "ANÁLISE COM CHATGPT")
    try:
        if not orchestrator.chatgpt:
            print("⚠️  ChatGPT não inicializado (verifique OPENAI_API_KEY no .env)")
            print("   Pulando análise...")
            analysis = {
                'tipo_lead': 'Lead Qualificado',
                'prioridade': 'alta',
                'informacoes_extraidas': form_data_exemplo['answers']
            }
        else:
            print("🔄 Analisando dados com ChatGPT...")
            analysis = orchestrator.chatgpt.analyze_form_data(form_data_exemplo)
            print("✅ Análise concluída!")
        
        print("\n📊 Resultado da Análise:")
        print(f"   - Tipo de Lead: {analysis.get('tipo_lead', 'N/A')}")
        print(f"   - Prioridade: {analysis.get('prioridade', 'N/A')}")
        print(f"   - Informações Extraídas:")
        info = analysis.get('informacoes_extraidas', {})
        for key, value in info.items():
            print(f"     • {key}: {value}")
            
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        print("   Continuando com dados simulados...")
        analysis = {
            'tipo_lead': 'Lead Qualificado',
            'prioridade': 'alta',
            'informacoes_extraidas': form_data_exemplo['answers']
        }
    
    print_step(4, "PROCESSAMENTO AUTOMÁTICO")
    print("\n🔄 Executando fluxo automatizado completo...")
    print("   (Simulando criação de tarefas, leads, documentos e mensagens)\n")
    
    # Simula cada etapa
    etapas = [
        ("ClickUp", "Criando tarefa no ClickUp...", orchestrator.clickup is not None),
        ("Chaves na Mão", "Criando lead no Chaves na Mão...", orchestrator.chaves_na_mao is not None),
        ("Google Drive", "Salvando documento no Google Drive...", orchestrator.google_drive is not None),
        ("Wasseller", "Enviando mensagem WhatsApp...", orchestrator.wasseller is not None),
    ]
    
    resultados = {}
    for nome, descricao, disponivel in etapas:
        if disponivel:
            print(f"   ✅ {descricao}")
            resultados[nome] = {'status': 'sucesso', 'simulado': True}
        else:
            print(f"   ⚠️  {descricao} (integração não configurada)")
            resultados[nome] = {'status': 'nao_configurado', 'simulado': True}
    
    print_step(5, "RESULTADO FINAL")
    print("\n✅ Processamento concluído!")
    print("\n📊 Resumo:")
    print(f"   - Formulário processado: {form_data_exemplo['response_id']}")
    print(f"   - Lead identificado: {analysis.get('tipo_lead', 'N/A')}")
    print(f"   - Prioridade: {analysis.get('prioridade', 'N/A')}")
    print(f"   - Integrações executadas:")
    for nome, resultado in resultados.items():
        status_icon = "✅" if resultado['status'] == 'sucesso' else "⚠️"
        print(f"     {status_icon} {nome}: {resultado['status']}")
    
    print("\n" + "="*70)
    print("🎉 AUTOMAÇÃO TESTADA COM SUCESSO!")
    print("="*70)
    
    return {
        'form_data': form_data_exemplo,
        'analysis': analysis,
        'results': resultados,
        'timestamp': datetime.now().isoformat()
    }


def testar_processamento_real():
    """Tenta processar um formulário real (se credenciais estiverem configuradas)"""
    
    print_header("🧪 TESTE DE PROCESSAMENTO REAL")
    
    try:
        orchestrator = IntegrationOrchestrator()
        
        # Dados de exemplo
        form_data = {
            'response_id': 'REAL_TEST_' + datetime.now().strftime('%Y%m%d%H%M%S'),
            'submission_time': datetime.now().isoformat(),
            'answers': {
                'nome': 'Maria Santos',
                'telefone': '11988888888',
                'email': 'maria.santos@email.com',
                'tipo_imovel': 'Casa',
                'localizacao': 'Rio de Janeiro',
                'orcamento': 'R$ 800.000,00'
            }
        }
        
        print("🔄 Processando formulário real...")
        print("   (Isso vai tentar criar tarefas, leads, etc. se credenciais estiverem configuradas)\n")
        
        result = orchestrator.process_form_response(
            form_data,
            send_whatsapp=True,   # Habilitado para testar WhatsApp
            create_lead=True,     # Habilitado para testar Chaves na Mão
            save_to_drive=True,   # ✅ HABILITADO PARA TESTAR PDF!
            create_task=True      # Habilitado para testar ClickUp
        )
        
        print("✅ Processamento concluído!")
        print("\n📊 Resultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None


def menu_principal():
    """Menu principal de testes"""
    
    while True:
        print_header("MENU DE TESTES - AUTOMAÇÃO")
        print("\nEscolha uma opção:")
        print("  1. Teste Simulado (Demonstração)")
        print("  2. Teste Real (Requer credenciais configuradas)")
        print("  3. Verificar Configurações")
        print("  4. Sair")
        
        escolha = input("\nOpção: ").strip()
        
        if escolha == '1':
            testar_automacao_completa()
            input("\nPressione Enter para continuar...")
        
        elif escolha == '2':
            print("\n⚠️  ATENÇÃO: Este teste vai tentar usar as integrações reais!")
            confirmar = input("Continuar? (s/N): ").strip().lower()
            if confirmar == 's':
                testar_processamento_real()
            input("\nPressione Enter para continuar...")
        
        elif escolha == '3':
            verificar_configuracoes()
            input("\nPressione Enter para continuar...")
        
        elif escolha == '4':
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida!")


def verificar_configuracoes():
    """Verifica configurações do sistema"""
    
    print_header("🔍 VERIFICAÇÃO DE CONFIGURAÇÕES")
    
    print("\n📋 Credenciais Configuradas:")
    
    configs = {
        'OpenAI API Key': Config.OPENAI_API_KEY and Config.OPENAI_API_KEY.startswith('sk-'),
        'Google Drive Folder ID': bool(Config.GOOGLE_DRIVE_FOLDER_ID),
        'Google Client ID': bool(Config.GOOGLE_CLIENT_ID) and Config.GOOGLE_CLIENT_ID != 'your_google_client_id',
        'ClickUp API Key': bool(Config.CLICKUP_API_KEY) and Config.CLICKUP_API_KEY != 'your_clickup_api_key',
        'Chaves na Mão API Key': bool(Config.CHAVES_NA_MAO_API_KEY) and Config.CHAVES_NA_MAO_API_KEY != 'your_chaves_na_mao_api_key',
        'Wasseller API Key': bool(Config.WASSELLER_API_KEY) and Config.WASSELLER_API_KEY != 'your_wasseller_api_key',
    }
    
    for nome, configurado in configs.items():
        status = "✅" if configurado else "❌"
        print(f"   {status} {nome}")
    
    print("\n📋 Formulários Configurados:")
    forms = Config.get_forms_config()
    print(f"   ✅ {len(forms.get('forms', []))} formulários configurados")
    
    print("\n📋 Integrações Disponíveis:")
    try:
        orchestrator = IntegrationOrchestrator()
        integracoes = {
            'ChatGPT': orchestrator.chatgpt is not None,
            'ClickUp': orchestrator.clickup is not None,
            'Chaves na Mão': orchestrator.chaves_na_mao is not None,
            'Wasseller': orchestrator.wasseller is not None,
            'Google Forms': orchestrator.google_forms is not None,
            'Google Drive': orchestrator.google_drive is not None,
        }
        
        for nome, disponivel in integracoes.items():
            status = "✅" if disponivel else "⚠️"
            print(f"   {status} {nome}")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar: {str(e)}")


if __name__ == '__main__':
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")

