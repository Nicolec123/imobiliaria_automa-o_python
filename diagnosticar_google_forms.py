"""
Script de diagnóstico para Google Forms
Testa diferentes formas de acesso para identificar o problema
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os


def diagnosticar_google_forms():
    """Diagnostica problemas com acesso ao Google Forms"""
    
    print("="*70)
    print("  DIAGNÓSTICO: GOOGLE FORMS")
    print("="*70)
    
    # 1. Verificar credenciais
    print("\n1️⃣ Verificando credenciais...")
    if not os.path.exists('google_credentials.json'):
        print("❌ google_credentials.json não encontrado")
        return
    
    try:
        creds = Credentials.from_authorized_user_file('google_credentials.json')
        print("✅ Credenciais carregadas")
        print(f"   Escopos: {creds.scopes}")
    except Exception as e:
        print(f"❌ Erro ao carregar credenciais: {e}")
        return
    
    # 2. Verificar se token está válido
    print("\n2️⃣ Verificando token...")
    if creds.expired:
        print("⚠️  Token expirado! Precisa renovar.")
        print("   Execute: python setup_google_auth.py")
    else:
        print("✅ Token válido")
    
    # 3. Testar acesso à API
    print("\n3️⃣ Testando acesso à API...")
    try:
        service = build('forms', 'v1', credentials=creds)
        print("✅ Serviço Google Forms inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar serviço: {e}")
        return
    
    # 4. Carregar formulários configurados
    print("\n4️⃣ Carregando formulários configurados...")
    try:
        with open('forms_config.json', 'r', encoding='utf-8') as f:
            forms_config = json.load(f)
        forms = forms_config.get('forms', [])
        print(f"✅ {len(forms)} formulários encontrados")
    except Exception as e:
        print(f"❌ Erro ao carregar forms_config.json: {e}")
        return
    
    # 5. Testar cada formulário com diferentes métodos
    print("\n5️⃣ Testando acesso aos formulários...")
    
    for form in forms:
        form_id = form['id']
        form_name = form['name']
        
        print(f"\n📋 Testando: {form_name}")
        print(f"   ID: {form_id}")
        
        # Método 1: Tentar obter informações do formulário
        try:
            print("   🔄 Método 1: Obtendo informações do formulário...")
            form_info = service.forms().get(formId=form_id).execute()
            print(f"   ✅ Formulário encontrado!")
            print(f"      Título: {form_info.get('info', {}).get('title', 'N/A')}")
        except HttpError as e:
            error_code = e.resp.status
            error_details = json.loads(e.content.decode('utf-8'))
            
            print(f"   ❌ Erro {error_code}: {error_details.get('error', {}).get('message', 'Erro desconhecido')}")
            
            if error_code == 404:
                print("   💡 Diagnóstico: Formulário não encontrado")
                print("      Possíveis causas:")
                print("      - ID do formulário está incorreto")
                print("      - Formulário foi deletado")
                print("      - Conta autorizada não tem acesso (mesmo sendo proprietário)")
            elif error_code == 403:
                print("   💡 Diagnóstico: Sem permissão")
                print("      - Verifique se a conta autorizada tem acesso")
            elif error_code == 401:
                print("   💡 Diagnóstico: Token inválido ou expirado")
                print("      - Renove o token: python setup_google_auth.py")
            else:
                print(f"   💡 Erro desconhecido: {error_code}")
        
        # Método 2: Tentar listar respostas (mesmo que vazio)
        try:
            print("   🔄 Método 2: Tentando listar respostas...")
            responses = service.forms().responses().list(formId=form_id).execute()
            print(f"   ✅ Respostas acessíveis! Total: {len(responses.get('responses', []))}")
        except HttpError as e:
            error_code = e.resp.status
            if error_code == 404:
                print("   ❌ Erro 404 ao listar respostas")
            else:
                print(f"   ❌ Erro {error_code} ao listar respostas")
    
    # 6. Verificar escopos necessários
    print("\n6️⃣ Verificando escopos...")
    print("   Escopos atuais:")
    for scope in creds.scopes:
        print(f"      - {scope}")
    
    print("\n   Escopos recomendados para Google Forms:")
    print("      - https://www.googleapis.com/auth/forms.responses.readonly")
    print("      - https://www.googleapis.com/auth/forms (opcional, para edição)")
    
    # 7. Sugestões
    print("\n" + "="*70)
    print("  SUGESTÕES")
    print("="*70)
    
    print("\n💡 Se todos os formulários deram erro 404:")
    print("   1. Verifique se os IDs estão corretos")
    print("   2. Verifique se a conta autorizada é a mesma que criou os forms")
    print("   3. Tente renovar o token: python setup_google_auth.py")
    print("   4. Verifique se Google Forms API está realmente ativada")
    
    print("\n💡 Se alguns funcionaram e outros não:")
    print("   - Os que não funcionaram podem ter IDs incorretos")
    print("   - Ou podem estar em outra conta")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    diagnosticar_google_forms()

