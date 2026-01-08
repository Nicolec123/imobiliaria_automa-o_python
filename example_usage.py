"""
Exemplos de uso do sistema de integração
"""
from orchestrator import IntegrationOrchestrator
from setup_google_auth import load_google_credentials

# Exemplo 1: Processar uma resposta de formulário
def exemplo_processar_formulario():
    """Exemplo de processamento de formulário"""
    
    # Inicializa orquestrador
    orchestrator = IntegrationOrchestrator()
    
    # Carrega credenciais Google se disponíveis
    google_creds = load_google_credentials()
    if google_creds:
        orchestrator.set_google_credentials(google_creds)
    
    # Dados de exemplo de formulário
    form_data = {
        'response_id': '12345',
        'submission_time': '2024-01-15T10:30:00Z',
        'answers': {
            'nome': 'João Silva',
            'telefone': '11999999999',
            'email': 'joao@email.com',
            'tipo_imovel': 'Apartamento',
            'localizacao': 'São Paulo - SP',
            'orcamento': 'R$ 500.000,00',
            'observacoes': 'Procuro apartamento com 2 quartos próximo ao metrô'
        }
    }
    
    # Processa formulário
    result = orchestrator.process_form_response(
        form_data,
        send_whatsapp=True,
        create_lead=True,
        save_to_drive=True,
        create_task=True
    )
    
    print("Resultado do processamento:")
    print(result)
    return result


# Exemplo 2: Sincronizar Google Forms
def exemplo_sincronizar_forms():
    """Exemplo de sincronização com Google Forms"""
    
    orchestrator = IntegrationOrchestrator()
    google_creds = load_google_credentials()
    
    if not google_creds:
        print("Erro: Credenciais do Google não configuradas")
        return
    
    orchestrator.set_google_credentials(google_creds)
    
    # Sincroniza formulários
    result = orchestrator.sync_google_forms(
        form_id=None,  # Usa o configurado no .env
        last_sync=None  # Pega todas as respostas
    )
    
    print(f"Respostas processadas: {result['responses_processed']}")
    print(f"Resultados: {len(result['results'])}")
    return result


# Exemplo 3: Usar integrações individualmente
def exemplo_uso_individual():
    """Exemplo de uso individual das integrações"""
    
    from integrations.chatgpt import ChatGPTIntegration
    from integrations.clickup import ClickUpIntegration
    
    # ChatGPT
    chatgpt = ChatGPTIntegration()
    analysis = chatgpt.analyze_form_data({
        'nome': 'Maria Santos',
        'telefone': '11888888888',
        'tipo_imovel': 'Casa'
    })
    print("Análise ChatGPT:", analysis)
    
    # ClickUp
    clickup = ClickUpIntegration()
    task = clickup.create_task(
        name="Teste de Tarefa",
        description="Descrição da tarefa de teste",
        priority=2
    )
    print("Tarefa criada:", task.get('id'))


if __name__ == '__main__':
    print("=== Exemplo 1: Processar Formulário ===")
    exemplo_processar_formulario()
    
    print("\n=== Exemplo 2: Sincronizar Forms ===")
    # exemplo_sincronizar_forms()  # Descomente se tiver credenciais Google
    
    print("\n=== Exemplo 3: Uso Individual ===")
    exemplo_uso_individual()

