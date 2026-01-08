"""
Script para testar especificamente o Google Forms
"""
import json
from datetime import datetime
from orchestrator import IntegrationOrchestrator
from integrations.google_forms import GoogleFormsIntegration
from google.oauth2.credentials import Credentials
import os


def carregar_credenciais():
    """Carrega credenciais do Google do arquivo"""
    try:
        if os.path.exists('google_credentials.json'):
            creds = Credentials.from_authorized_user_file('google_credentials.json')
            return creds
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar credenciais: {e}")
        return None


def testar_google_forms():
    """Testa captura de respostas do Google Forms"""
    
    print("="*70)
    print("  TESTE: GOOGLE FORMS")
    print("="*70)
    
    # Carrega credenciais
    print("\n1️⃣ Carregando credenciais...")
    creds = carregar_credenciais()
    
    if not creds:
        print("❌ Credenciais não encontradas ou inválidas")
        print("   Verifique se google_credentials.json existe e está válido")
        return
    
    print("✅ Credenciais carregadas!")
    
    # Inicializa Google Forms
    print("\n2️⃣ Inicializando Google Forms...")
    try:
        google_forms = GoogleFormsIntegration(credentials=creds)
        print("✅ Google Forms inicializado!")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    # Carrega configuração de formulários
    print("\n3️⃣ Carregando formulários configurados...")
    try:
        with open('forms_config.json', 'r', encoding='utf-8') as f:
            forms_config = json.load(f)
        
        forms = forms_config.get('forms', [])
        print(f"✅ {len(forms)} formulários encontrados")
        
        for form in forms:
            print(f"   - {form['name']}: {form['id']}")
    except Exception as e:
        print(f"❌ Erro ao carregar forms_config.json: {e}")
        return
    
    # Testa cada formulário
    print("\n4️⃣ Testando acesso aos formulários...")
    
    for form in forms:
        form_id = form['id']
        form_name = form['name']
        
        print(f"\n📋 Testando: {form_name}")
        print(f"   ID: {form_id}")
        
        try:
            # Tenta obter respostas
            responses = google_forms.get_form_responses(form_id=form_id)
            
            print(f"   ✅ Acesso OK!")
            print(f"   📊 Respostas encontradas: {len(responses)}")
            
            if responses:
                print(f"   📝 Última resposta:")
                last_response = responses[-1]
                print(f"      ID: {last_response.get('responseId', 'N/A')}")
                print(f"      Criada em: {last_response.get('createTime', 'N/A')}")
            
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'not found' in error_msg.lower():
                print(f"   ❌ Form não encontrado (404)")
                print(f"      Verifique se o Form ID está correto")
            elif '403' in error_msg or 'permission' in error_msg.lower():
                print(f"   ❌ Sem permissão (403)")
                print(f"      Verifique se a conta autorizada tem acesso ao Form")
            else:
                print(f"   ❌ Erro: {error_msg}")
    
    # Testa processamento completo
    print("\n5️⃣ Testando processamento completo...")
    
    try:
        orchestrator = IntegrationOrchestrator()
        
        # Tenta buscar novas respostas
        if orchestrator.google_forms:
            print("✅ Orchestrator tem Google Forms configurado!")
            
            # Testa sincronização
            print("\n6️⃣ Testando sincronização...")
            
            # Busca respostas de um formulário
            test_form = forms[0] if forms else None
            if test_form:
                print(f"   Testando com: {test_form['name']}")
                responses = orchestrator.google_forms.get_form_responses(form_id=test_form['id'])
                print(f"   ✅ {len(responses)} respostas encontradas")
                
                if responses:
                    print(f"\n   📋 Processando primeira resposta...")
                    # Simula processamento
                    form_response = {
                        'response_id': responses[0].get('responseId', 'TEST'),
                        'form_id': test_form['id'],
                        'form_title': test_form['name'],
                        'submission_time': responses[0].get('createTime', datetime.now().isoformat()),
                        'answers': {}  # Seria extraído das respostas
                    }
                    
                    print(f"   ✅ Resposta preparada para processamento")
                    print(f"   💡 Execute: orchestrator.process_form_response(form_response)")
        else:
            print("⚠️  Orchestrator não tem Google Forms configurado")
            print("   Verifique se credenciais foram carregadas no __init__")
            
    except Exception as e:
        print(f"❌ Erro ao testar processamento: {e}")
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO!")
    print("="*70)


if __name__ == '__main__':
    testar_google_forms()

