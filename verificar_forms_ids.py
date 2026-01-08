"""
Script para verificar se os IDs dos Forms estão corretos
"""
from config import Config
from setup_google_auth import load_google_credentials
from integrations.google_forms import GoogleFormsIntegration

def verificar_forms_ids():
    """Verifica se os IDs dos Forms estão corretos"""
    
    print("="*70)
    print("🔍 VERIFICAÇÃO DE IDs DOS FORMS")
    print("="*70)
    
    # Carrega credenciais
    creds = load_google_credentials()
    if not creds:
        print("\n❌ Credenciais Google não encontradas!")
        print("   Execute: python setup_google_auth_simples.py")
        return
    
    print("\n✅ Credenciais Google carregadas")
    
    # Inicializa Google Forms
    try:
        google_forms = GoogleFormsIntegration(credentials=creds)
    except Exception as e:
        print(f"\n❌ Erro ao inicializar: {e}")
        return
    
    # Lista Forms configurados
    forms_config = Config.get_forms_config()
    forms = forms_config.get('forms', [])
    
    print(f"\n📋 Testando {len(forms)} formulários...\n")
    
    for form in forms:
        form_id = form.get('id')
        form_name = form.get('name')
        
        print(f"🔍 Testando: {form_name}")
        print(f"   ID: {form_id}")
        
        try:
            # Tenta acessar o form
            form_data = google_forms.service.forms().get(formId=form_id).execute()
            
            print(f"   ✅ Form encontrado!")
            print(f"   📝 Título: {form_data.get('info', {}).get('title', 'N/A')}")
            
            # Tenta obter respostas
            try:
                responses = google_forms.service.forms().responses().list(formId=form_id).execute()
                total_responses = len(responses.get('responses', []))
                print(f"   📊 Respostas: {total_responses}")
            except Exception as e:
                print(f"   ⚠️  Erro ao obter respostas: {e}")
            
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'not found' in error_msg.lower():
                print(f"   ❌ Form NÃO encontrado (404)")
                print(f"   💡 Possíveis causas:")
                print(f"      - ID incorreto")
                print(f"      - Form foi deletado")
                print(f"      - Form está em outra conta Google")
                print(f"      - Você não tem acesso a este Form")
            else:
                print(f"   ❌ Erro: {error_msg}")
        
        print()

if __name__ == '__main__':
    verificar_forms_ids()

