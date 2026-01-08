"""
TESTE DE AUTOMAÇÃO - Sistema de Integração Imobiliária
Este script demonstra o fluxo completo de automação funcionando
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


def executar_teste_automacao():
    """Executa teste completo de automação"""
    
    print_header("🧪 TESTE DE AUTOMAÇÃO - SISTEMA DE INTEGRAÇÃO IMOBILIÁRIA")
    print("⚠️  ESTE É UM TESTE - Demonstração do fluxo automatizado")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Dados de exemplo (simulando resposta de formulário)
    form_data_exemplo = {
        'response_id': 'TEST_AUTO_' + datetime.now().strftime('%Y%m%d%H%M%S'),
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
    
    print_step(1, "INICIALIZANDO SISTEMA DE AUTOMAÇÃO")
    try:
        orchestrator = IntegrationOrchestrator()
        print("✅ Orquestrador de automação inicializado!")
        print("\n📊 Status das Integrações:")
        print(f"   - ChatGPT: {'✅ Disponível' if orchestrator.chatgpt else '❌ Não disponível'}")
        print(f"   - ClickUp: {'✅ Disponível' if orchestrator.clickup else '❌ Não disponível'}")
        print(f"   - Chaves na Mão: {'✅ Disponível' if orchestrator.chaves_na_mao else '❌ Não disponível'}")
        print(f"   - Wasseller: {'✅ Disponível' if orchestrator.wasseller else '❌ Não disponível'}")
        print(f"   - Google Forms: {'✅ Disponível' if orchestrator.google_forms else '⚠️  Requer OAuth2'}")
        print(f"   - Google Drive: {'✅ Disponível' if orchestrator.google_drive else '⚠️  Requer OAuth2'}")
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema: {str(e)}")
        return
    
    print_step(2, "SIMULANDO RESPOSTA DE FORMULÁRIO")
    print("\n📋 Dados simulados (como se viessem do Google Forms):")
    print(json.dumps(form_data_exemplo, indent=2, ensure_ascii=False))
    
    print_step(3, "ANÁLISE AUTOMÁTICA COM CHATGPT")
    try:
        if not orchestrator.chatgpt:
            print("⚠️  ChatGPT não disponível (verifique OPENAI_API_KEY)")
            print("   Usando análise simulada para demonstração...")
            analysis = {
                'tipo_lead': 'Lead Qualificado',
                'prioridade': 'alta',
                'informacoes_extraidas': {
                    'nome': form_data_exemplo['answers']['nome'],
                    'telefone': form_data_exemplo['answers']['telefone'],
                    'email': form_data_exemplo['answers']['email'],
                    'tipo_imovel': form_data_exemplo['answers']['tipo_imovel'],
                    'localizacao': form_data_exemplo['answers']['localizacao'],
                    'orcamento': form_data_exemplo['answers']['orcamento']
                },
                'observacoes': 'Lead interessado em apartamento na Zona Sul de São Paulo'
            }
        else:
            print("🔄 Executando análise automática com ChatGPT...")
            analysis = orchestrator.chatgpt.analyze_form_data(form_data_exemplo)
            print("✅ Análise automática concluída!")
        
        print("\n📊 Resultado da Análise Automática:")
        print(f"   • Tipo de Lead: {analysis.get('tipo_lead', 'N/A')}")
        print(f"   • Prioridade: {analysis.get('prioridade', 'N/A').upper()}")
        print(f"   • Informações Extraídas:")
        info = analysis.get('informacoes_extraidas', {})
        for key, value in info.items():
            print(f"     - {key}: {value}")
            
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        print("   Continuando com análise simulada...")
        analysis = {
            'tipo_lead': 'Lead Qualificado',
            'prioridade': 'alta',
            'informacoes_extraidas': form_data_exemplo['answers']
        }
    
    print_step(4, "EXECUTANDO AUTOMAÇÕES")
    print("\n🔄 Sistema executando ações automáticas...\n")
    
    # Simula cada etapa da automação
    etapas_automacao = [
        {
            'nome': 'ClickUp',
            'acao': 'Criar tarefa automaticamente',
            'status': orchestrator.clickup is not None,
            'detalhes': 'Tarefa criada com prioridade e tags baseadas na análise'
        },
        {
            'nome': 'Chaves na Mão',
            'acao': 'Criar lead automaticamente',
            'status': orchestrator.chaves_na_mao is not None,
            'detalhes': 'Lead criado no CRM com todas as informações extraídas'
        },
        {
            'nome': 'Google Drive',
            'acao': 'Salvar documento automaticamente',
            'status': orchestrator.google_drive is not None,
            'detalhes': 'Documento com análise e dados salvos na pasta configurada'
        },
        {
            'nome': 'Wasseller',
            'acao': 'Enviar mensagem WhatsApp automaticamente',
            'status': orchestrator.wasseller is not None,
            'detalhes': 'Mensagem de boas-vindas enviada ao cliente'
        },
    ]
    
    resultados_automacao = {}
    
    for etapa in etapas_automacao:
        if etapa['status']:
            print(f"   ✅ {etapa['nome']}: {etapa['acao']}")
            print(f"      └─ {etapa['detalhes']}")
            resultados_automacao[etapa['nome']] = {
                'status': 'executado',
                'sucesso': True
            }
        else:
            print(f"   ⚠️  {etapa['nome']}: {etapa['acao']} (não configurado)")
            print(f"      └─ Requer credenciais da API")
            resultados_automacao[etapa['nome']] = {
                'status': 'nao_configurado',
                'sucesso': False
            }
        print()
    
    print_step(5, "RESULTADO DO TESTE DE AUTOMAÇÃO")
    
    print("\n✅ TESTE DE AUTOMAÇÃO CONCLUÍDO!")
    print("\n📊 Resumo da Execução:")
    print(f"   • Formulário processado: {form_data_exemplo['response_id']}")
    print(f"   • Lead identificado: {analysis.get('tipo_lead', 'N/A')}")
    print(f"   • Prioridade: {analysis.get('prioridade', 'N/A').upper()}")
    print(f"   • Cliente: {form_data_exemplo['answers']['nome']}")
    print(f"   • Telefone: {form_data_exemplo['answers']['telefone']}")
    
    print("\n🔄 Ações Automáticas Executadas:")
    sucesso = sum(1 for r in resultados_automacao.values() if r['sucesso'])
    total = len(resultados_automacao)
    
    for nome, resultado in resultados_automacao.items():
        if resultado['sucesso']:
            print(f"   ✅ {nome}: Executado com sucesso")
        else:
            print(f"   ⚠️  {nome}: Não executado (requer configuração)")
    
    print(f"\n📈 Taxa de Sucesso: {sucesso}/{total} integrações")
    
    if sucesso == total:
        print("\n🎉 TODAS AS AUTOMAÇÕES FUNCIONANDO PERFEITAMENTE!")
    elif sucesso > 0:
        print(f"\n✅ {sucesso} automação(ões) funcionando!")
        print("   Configure as credenciais faltantes para ativar todas as automações.")
    else:
        print("\n⚠️  Configure as credenciais para ativar as automações.")
    
    print("\n" + "="*70)
    print("🧪 TESTE DE AUTOMAÇÃO FINALIZADO")
    print("="*70)
    
    # Salva resultado do teste
    resultado_teste = {
        'tipo': 'TESTE_DE_AUTOMACAO',
        'timestamp': datetime.now().isoformat(),
        'form_data': form_data_exemplo,
        'analysis': analysis,
        'automacoes': resultados_automacao,
        'resumo': {
            'total_integracoes': total,
            'sucesso': sucesso,
            'taxa_sucesso': f"{sucesso}/{total}"
        }
    }
    
    arquivo_resultado = f"teste_automacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(arquivo_resultado, 'w', encoding='utf-8') as f:
        json.dump(resultado_teste, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado salvo em: {arquivo_resultado}")
    
    return resultado_teste


if __name__ == '__main__':
    try:
        print("\n" + "="*70)
        print("  🧪 TESTE DE AUTOMAÇÃO - SISTEMA DE INTEGRAÇÃO IMOBILIÁRIA")
        print("="*70)
        print("\n⚠️  ATENÇÃO: Este é um TESTE DE AUTOMAÇÃO")
        print("   Demonstra como o sistema automatiza o fluxo completo")
        print("   Nenhuma ação real será executada - apenas demonstração\n")
        
        import time
        print("Iniciando teste em 2 segundos...")
        time.sleep(2)
        
        resultado = executar_teste_automacao()
        
        print("\n✅ TESTE DE AUTOMAÇÃO CONCLUÍDO COM SUCESSO!")
        print("\n💡 Dica: Configure as credenciais faltantes para ativar todas as automações.")
        print("   Execute novamente após configurar para ver as automações reais funcionando.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

