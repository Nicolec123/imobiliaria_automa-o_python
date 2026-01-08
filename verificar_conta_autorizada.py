"""
Script para verificar qual conta Google está autorizada e comparar com Forms
"""
from setup_google_auth import load_google_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os

def verificar_conta_autorizada():
    """Verifica qual conta está autorizada e compara com Forms"""
    
    print("="*70)
    print("🔍 VERIFICAÇÃO DE CONTA AUTORIZADA")
    print("="*70)
    
    # 1. Carrega credenciais
    creds = load_google_credentials()
    if not creds:
        print("\n❌ Credenciais não encontradas!")
        print("   Execute: python setup_google_auth_simples.py")
        return
    
    print("\n✅ Credenciais encontradas")
    
    # 2. Tenta obter informações da conta
    print("\n" + "="*70)
    print("1️⃣  CONTA GOOGLE AUTORIZADA")
    print("="*70)
    
    email_autorizado = None
    nome_autorizado = None
    
    try:
        # Tenta obter via OAuth2 API
        oauth_service = build('oauth2', 'v2', credentials=creds)
        user_info = oauth_service.userinfo().get().execute()
        email_autorizado = user_info.get('email')
        nome_autorizado = user_info.get('name')
        
        print(f"\n📧 Email: {email_autorizado}")
        print(f"👤 Nome: {nome_autorizado}")
        
    except HttpError as e:
        if e.resp.status == 401:
            print("\n⚠️  Não conseguiu obter email (token pode ter expirado)")
            print("   Mas vou tentar outras formas...")
        else:
            print(f"\n⚠️  Erro ao obter info: {e}")
    
    # Se não conseguiu, tenta via Drive
    if not email_autorizado:
        try:
            drive_service = build('drive', 'v3', credentials=creds)
            about = drive_service.about().get(fields='user').execute()
            user = about.get('user', {})
            email_autorizado = user.get('emailAddress')
            nome_autorizado = user.get('displayName')
            
            if email_autorizado:
                print(f"\n📧 Email (via Drive): {email_autorizado}")
                print(f"👤 Nome: {nome_autorizado}")
        except Exception as e:
            print(f"\n⚠️  Erro ao obter via Drive: {e}")
    
    # Se ainda não conseguiu, mostra do arquivo
    if not email_autorizado:
        try:
            with open('google_credentials.json', 'r') as f:
                creds_data = json.load(f)
                client_id = creds_data.get('client_id', '')
                print(f"\n📋 Client ID usado: {client_id[:50]}...")
                print("   (Não consegui obter email diretamente)")
        except:
            pass
    
    # 3. Testa acesso aos Forms
    print("\n" + "="*70)
    print("2️⃣  TESTANDO ACESSO AOS FORMS")
    print("="*70)
    
    from config import Config
    forms_config = Config.get_forms_config()
    forms = forms_config.get('forms', [])
    
    forms_service = build('forms', 'v1', credentials=creds)
    
    forms_funcionando = []
    forms_404 = []
    
    print(f"\n📋 Testando {len(forms)} formulários...\n")
    
    for i, form in enumerate(forms, 1):
        form_id = form.get('id')
        form_name = form.get('name')
        
        print(f"{i}. {form_name}")
        print(f"   ID: {form_id}")
        
        try:
            form_data = forms_service.forms().get(formId=form_id).execute()
            title = form_data.get('info', {}).get('title', 'N/A')
            forms_funcionando.append((form_name, form_id))
            print(f"   ✅ FUNCIONANDO - Título: {title}")
            
        except HttpError as e:
            if e.resp.status == 404:
                forms_404.append((form_name, form_id))
                print(f"   ❌ 404 - Não encontrado")
            elif e.resp.status == 403:
                print(f"   ❌ 403 - Sem permissão")
            else:
                print(f"   ❌ Erro {e.resp.status}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
    
    # 4. Resumo e recomendações
    print("="*70)
    print("📊 RESUMO")
    print("="*70)
    
    if email_autorizado:
        print(f"\n📧 Conta autorizada: {email_autorizado}")
    else:
        print(f"\n⚠️  Não foi possível identificar a conta autorizada")
    
    print(f"\n✅ Forms funcionando: {len(forms_funcionando)}")
    print(f"❌ Forms com 404: {len(forms_404)}")
    
    # 5. Diagnóstico e solução
    print("\n" + "="*70)
    print("💡 DIAGNÓSTICO E SOLUÇÃO")
    print("="*70)
    
    if len(forms_404) == len(forms):
        print("\n🔴 PROBLEMA: TODOS OS FORMS DÃO 404")
        print("\n   Isso significa que:")
        print("   - A conta autorizada NÃO tem acesso aos Forms")
        print("   - OU os Forms foram deletados/movidos")
        print("   - OU os IDs estão incorretos")
        
        print("\n   📋 AÇÕES NECESSÁRIAS:")
        print("\n   1. Verifique qual conta tem os Forms:")
        print("      - Abra um Form no navegador")
        print("      - Veja qual conta Google está logada (canto superior direito)")
        print("      - Anote o email dessa conta")
        
        if email_autorizado:
            print(f"\n   2. Compare com a conta autorizada:")
            print(f"      - Conta autorizada: {email_autorizado}")
            print(f"      - Conta que tem Forms: [VERIFIQUE NO NAVEGADOR]")
            print(f"      - Se forem diferentes, você precisa reautorizar!")
        
        print("\n   3. Se a conta estiver errada, reautorize:")
        print("      - Delete: google_credentials.json")
        print("      - Execute: python setup_google_auth_simples.py")
        print("      - Use a CONTA QUE TEM OS FORMS (não outra conta!)")
        
        print("\n   4. Verifique os IDs dos Forms:")
        print("      - Abra cada Form no navegador")
        print("      - A URL tem o formato:")
        print("        https://docs.google.com/forms/d/e/FORM_ID_AQUI/viewform")
        print("      - Copie o FORM_ID e compare com forms_config.json")
        
    elif len(forms_funcionando) > 0:
        print("\n✅ ALGUNS FORMS FUNCIONAM")
        print("\n   Forms funcionando:")
        for form_name, form_id in forms_funcionando:
            print(f"      ✅ {form_name}")
        
        if forms_404:
            print("\n   Forms com problema:")
            for form_name, form_id in forms_404:
                print(f"      ❌ {form_name}")
            print("\n   💡 Verifique os IDs dos Forms que não funcionam")
    
    else:
        print("\n✅ TODOS OS FORMS FUNCIONAM!")
        print("   Não há problema!")
    
    # 6. Instruções específicas
    print("\n" + "="*70)
    print("🔧 COMO REAUTORIZAR (SE NECESSÁRIO)")
    print("="*70)
    
    print("""
    Passo 1: Delete as credenciais antigas
    ----------------------------------------
    del google_credentials.json
    
    Passo 2: Reautorize com a conta CORRETA
    ----------------------------------------
    python setup_google_auth_simples.py
    
    ⚠️  IMPORTANTE:
    - Use a CONTA GOOGLE QUE TEM OS FORMS
    - Não use sua conta pessoal
    - Não use outra conta de trabalho
    - Use EXATAMENTE a conta que criou/possui os Forms
    
    Passo 3: Teste novamente
    ----------------------------------------
    python verificar_conta_autorizada.py
    """)

if __name__ == '__main__':
    verificar_conta_autorizada()

