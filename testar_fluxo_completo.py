"""
Script para testar o fluxo completo conforme a proposta
Verifica cada integração e mostra status detalhado
"""
from orchestrator import IntegrationOrchestrator
from config import Config
from datetime import datetime
import json

def testar_fluxo_completo():
    """Testa o fluxo completo conforme proposta"""
    
    print("="*70)
    print("🧪 TESTE COMPLETO DO FLUXO - VERIFICAÇÃO DA PROPOSTA")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Dados de teste simulando formulário real
    form_data = {
        'response_id': 'TEST_FLUXO_' + datetime.now().strftime('%Y%m%d%H%M%S'),
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
    
    print("📋 DADOS DO TESTE (Simulando Google Forms)")
    print(json.dumps(form_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("1️⃣  VERIFICANDO INTEGRAÇÕES")
    print("="*70)
    
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
            status = "✅ Disponível" if disponivel else "⚠️  Não disponível"
            print(f"   {status}: {nome}")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    print("\n" + "="*70)
    print("2️⃣  PROCESSANDO FLUXO COMPLETO")
    print("="*70)
    
    try:
        resultado = orchestrator.process_form_response(
            form_data,
            send_whatsapp=True,
            create_lead=True,
            save_to_drive=True,
            create_task=True
        )
        
        print("\n" + "="*70)
        print("3️⃣  RESULTADO DO PROCESSAMENTO")
        print("="*70)
        
        print(f"\n✅ Status Geral: {'SUCESSO' if resultado['success'] else 'COM ERROS'}")
        print(f"📊 ID do Processamento: {resultado['response_id']}")
        
        print("\n📋 Detalhes por Etapa:")
        
        # ChatGPT
        if 'chatgpt_analysis' in resultado['steps']:
            chatgpt_step = resultado['steps']['chatgpt_analysis']
            status_icon = "✅" if chatgpt_step.get('success') else "❌"
            print(f"\n   {status_icon} ChatGPT/Análise:")
            print(f"      Status: {'Sucesso' if chatgpt_step.get('success') else 'Falhou'}")
            if chatgpt_step.get('note'):
                print(f"      Observação: {chatgpt_step['note']}")
        
        # ClickUp
        if 'clickup_task' in resultado['steps']:
            clickup_step = resultado['steps']['clickup_task']
            status_icon = "✅" if clickup_step.get('success') else "❌"
            print(f"\n   {status_icon} ClickUp:")
            print(f"      Status: {'Sucesso' if clickup_step.get('success') else 'Falhou'}")
            if clickup_step.get('task_id'):
                print(f"      Tarefa ID: {clickup_step['task_id']}")
        
        # Chaves na Mão
        if 'chaves_na_mao_xml' in resultado['steps']:
            xml_step = resultado['steps']['chaves_na_mao_xml']
            status_icon = "✅" if xml_step.get('success') else "❌"
            print(f"\n   {status_icon} Chaves na Mão:")
            print(f"      Status: {'Sucesso' if xml_step.get('success') else 'Falhou'}")
            if xml_step.get('xml_file'):
                print(f"      Arquivo XML: {xml_step['xml_file']}")
        
        # Google Drive
        if 'google_drive' in resultado['steps']:
            drive_step = resultado['steps']['google_drive']
            status_icon = "✅" if drive_step.get('success') else "⚠️"
            print(f"\n   {status_icon} Google Drive:")
            print(f"      Status: {'Sucesso' if drive_step.get('success') else 'Não disponível (OAuth2 não configurado)'}")
            if drive_step.get('document_id'):
                print(f"      Documento ID: {drive_step['document_id']}")
        
        # WhatsApp Cliente
        if 'whatsapp' in resultado['steps']:
            whatsapp_step = resultado['steps']['whatsapp']
            status_icon = "✅" if whatsapp_step.get('success') else "❌"
            print(f"\n   {status_icon} WhatsApp (Cliente):")
            print(f"      Status: {'Sucesso' if whatsapp_step.get('success') else 'Falhou'}")
        
        # Notificações Equipe/Grupos
        if 'notificacoes_equipe' in resultado['steps']:
            notif_step = resultado['steps']['notificacoes_equipe']
            status_icon = "✅" if notif_step.get('success') else "❌"
            print(f"\n   {status_icon} Notificações (Grupos + Equipe):")
            print(f"      Status: {'Sucesso' if notif_step.get('success') else 'Falhou'}")
            if notif_step.get('success'):
                print(f"      Grupos: {notif_step.get('grupos_enviados', 0)} enviados")
                print(f"      Equipe: {notif_step.get('equipe_enviados', 0)} enviados")
        
        # Erros
        if resultado.get('errors'):
            print(f"\n⚠️  Erros encontrados: {len(resultado['errors'])}")
            for erro in resultado['errors']:
                print(f"      - {erro}")
        
        print("\n" + "="*70)
        print("4️⃣  RESUMO FINAL")
        print("="*70)
        
        print(f"\n✅ Integrações Funcionando:")
        funcionando = []
        if resultado['steps'].get('chatgpt_analysis', {}).get('success'):
            funcionando.append("ChatGPT/Análise")
        if resultado['steps'].get('clickup_task', {}).get('success'):
            funcionando.append("ClickUp")
        if resultado['steps'].get('chaves_na_mao_xml', {}).get('success'):
            funcionando.append("Chaves na Mão")
        if resultado['steps'].get('whatsapp', {}).get('success'):
            funcionando.append("WhatsApp Cliente")
        if resultado['steps'].get('notificacoes_equipe', {}).get('success'):
            funcionando.append("Notificações Grupos/Equipe")
        
        for item in funcionando:
            print(f"   ✅ {item}")
        
        print(f"\n📊 Taxa de Sucesso: {len(funcionando)}/5 integrações principais")
        
        if resultado['success']:
            print("\n🎉 FLUXO COMPLETO FUNCIONANDO!")
        else:
            print("\n⚠️  Fluxo funcionando com algumas limitações (ver erros acima)")
        
    except Exception as e:
        print(f"\n❌ Erro ao processar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        testar_fluxo_completo()
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

