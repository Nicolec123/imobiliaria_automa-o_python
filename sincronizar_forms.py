"""
Script para sincronizar todos os formulários automaticamente
"""
import sys
from datetime import datetime
from orchestrator import IntegrationOrchestrator
from setup_google_auth import load_google_credentials
from config import Config

def sincronizar_todos_forms():
    """Sincroniza todos os formulários configurados"""
    print("="*70)
    print("🔄 SINCRONIZAÇÃO AUTOMÁTICA DE FORMULÁRIOS")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Carrega credenciais do Google
        creds = load_google_credentials()
        if not creds:
            print("❌ ERRO: Credenciais do Google não encontradas")
            print("💡 Execute: python setup_google_auth_simples.py")
            return False
        
        # Inicializa orquestrador
        orchestrator = IntegrationOrchestrator()
        orchestrator.set_google_credentials(creds)
        
        if not orchestrator.google_forms:
            print("❌ ERRO: Não foi possível inicializar Google Forms")
            return False
        
        # Obtém lista de formulários
        forms_config = Config.get_forms_config()
        forms = forms_config.get('forms', [])
        
        if not forms:
            print("⚠️  Nenhum formulário configurado")
            return False
        
        print(f"📋 Formulários encontrados: {len(forms)}")
        print()
        
        total_processados = 0
        total_erros = 0
        
        # Processa cada formulário
        for form in forms:
            form_id = form.get('id')
            form_name = form.get('name', 'Sem nome')
            
            print(f"🔄 Processando: {form_name}")
            
            try:
                # Busca novas respostas
                responses = orchestrator.google_forms.get_new_responses(form_id)
                
                if responses:
                    print(f"   ✅ {len(responses)} nova(s) resposta(s) encontrada(s)")
                    
                    # Processa cada resposta
                    for response in responses:
                        try:
                            result = orchestrator.process_form_response(
                                response,
                                send_whatsapp=True,
                                create_lead=True,
                                save_to_drive=True,
                                create_task=True
                            )
                            
                            if result.get('success'):
                                total_processados += 1
                                print(f"   ✅ Processado: {result.get('response_id', 'N/A')}")
                            else:
                                total_erros += 1
                                print(f"   ❌ Erro ao processar: {result.get('errors', [])}")
                        except Exception as e:
                            total_erros += 1
                            print(f"   ❌ Erro: {str(e)}")
                else:
                    print(f"   ℹ️  Nenhuma nova resposta")
                    
            except Exception as e:
                total_erros += 1
                print(f"   ❌ Erro ao processar formulário: {str(e)}")
            
            print()
        
        # Resumo
        print("="*70)
        print("📊 RESUMO")
        print("="*70)
        print(f"✅ Processados com sucesso: {total_processados}")
        print(f"❌ Erros: {total_erros}")
        print(f"📋 Total de formulários verificados: {len(forms)}")
        print()
        
        return total_erros == 0
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    sucesso = sincronizar_todos_forms()
    sys.exit(0 if sucesso else 1)

