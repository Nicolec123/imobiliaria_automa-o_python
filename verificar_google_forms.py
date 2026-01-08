"""
Script para verificar se Google Forms está configurado e funcionando
"""
import os
from config import Config
from setup_google_auth import load_google_credentials

def verificar_google_forms():
    """Verifica status da configuração Google Forms"""
    
    print("="*70)
    print("🔍 VERIFICAÇÃO GOOGLE FORMS")
    print("="*70)
    
    # 1. Verifica credenciais OAuth2 no .env
    print("\n1️⃣  Credenciais OAuth2 no .env:")
    if Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_ID != 'your_google_client_id':
        print(f"   ✅ GOOGLE_CLIENT_ID: {Config.GOOGLE_CLIENT_ID[:30]}...")
    else:
        print("   ❌ GOOGLE_CLIENT_ID não configurado")
        return False
    
    if Config.GOOGLE_CLIENT_SECRET and Config.GOOGLE_CLIENT_SECRET != 'your_google_client_secret':
        print(f"   ✅ GOOGLE_CLIENT_SECRET: Configurado")
    else:
        print("   ❌ GOOGLE_CLIENT_SECRET não configurado")
        return False
    
    # 2. Verifica se google_credentials.json existe (autorização feita)
    print("\n2️⃣  Autorização OAuth2:")
    creds = load_google_credentials()
    if creds:
        print("   ✅ google_credentials.json encontrado")
        print("   ✅ Sistema autorizado para acessar Google Forms/Drive")
    else:
        print("   ⚠️  google_credentials.json NÃO encontrado")
        print("   ⚠️  Você precisa autorizar o sistema uma vez")
        print("\n   💡 Execute: python setup_google_auth.py")
        return False
    
    # 3. Verifica Google Drive Folder ID
    print("\n3️⃣  Google Drive:")
    if Config.GOOGLE_DRIVE_FOLDER_ID and Config.GOOGLE_DRIVE_FOLDER_ID != 'your_drive_folder_id':
        print(f"   ✅ GOOGLE_DRIVE_FOLDER_ID: {Config.GOOGLE_DRIVE_FOLDER_ID[:30]}...")
    else:
        print("   ⚠️  GOOGLE_DRIVE_FOLDER_ID não configurado")
    
    # 4. Verifica Forms configurados
    print("\n4️⃣  Formulários Configurados:")
    try:
        forms_config = Config.get_forms_config()
        forms = forms_config.get('forms', [])
        if forms:
            print(f"   ✅ {len(forms)} formulários configurados:")
            for form in forms:
                print(f"      - {form.get('name')}: {form.get('id')}")
        else:
            print("   ⚠️  Nenhum formulário configurado em forms_config.json")
    except Exception as e:
        print(f"   ⚠️  Erro ao carregar forms_config.json: {e}")
    
    # 5. Testa inicialização do GoogleFormsIntegration
    print("\n5️⃣  Teste de Inicialização:")
    try:
        from integrations.google_forms import GoogleFormsIntegration
        
        if creds:
            google_forms = GoogleFormsIntegration(credentials=creds)
            print("   ✅ GoogleFormsIntegration inicializado com sucesso")
            print("   ✅ Pronto para ler respostas dos Forms!")
        else:
            print("   ⚠️  Não foi possível inicializar (credenciais não encontradas)")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar: {e}")
    
    print("\n" + "="*70)
    print("📊 RESUMO")
    print("="*70)
    
    if creds:
        print("\n✅ Google Forms está CONFIGURADO e PRONTO!")
        print("   Você pode executar: python run_automation.py --sync")
    else:
        print("\n⚠️  Falta autorizar o sistema uma vez")
        print("   Execute: python setup_google_auth.py")
    
    return creds is not None

if __name__ == '__main__':
    verificar_google_forms()

