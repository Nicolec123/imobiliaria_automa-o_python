"""
Script auxiliar para configurar autenticação OAuth2 do Google
"""
import os
import webbrowser
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from config import Config

SCOPES = [
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/drive.file'
]


def setup_google_oauth():
    """Configura e obtém credenciais OAuth2 do Google"""
    
    print("\n" + "="*60)
    print("🔐 CONFIGURAÇÃO OAUTH2 GOOGLE")
    print("="*60 + "\n")
    
    # Verificar se credenciais já existem
    if os.path.exists('google_credentials.json'):
        print("⚠️  Arquivo 'google_credentials.json' já existe!")
        resposta = input("Deseja sobrescrever? (s/n): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("Operação cancelada.")
            return load_google_credentials()
    
    # Validar configurações
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        print("❌ Erro: Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env")
        print("\n💡 Execute primeiro: python configurar_google_cloud.py")
        return None
    
    print("✅ Credenciais OAuth encontradas no .env")
    print(f"   Client ID: {Config.GOOGLE_CLIENT_ID[:30]}...")
    print(f"   Redirect URI: {Config.GOOGLE_REDIRECT_URI}\n")
    
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": Config.GOOGLE_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )
        
        # Gera URL de autorização
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("="*60)
        print("📋 PASSO A PASSO:")
        print("="*60)
        print("\n⚠️  IMPORTANTE: Use a CONTA GOOGLE DO CLIENTE!")
        print("   (A mesma que tem os Google Forms e Google Drive)\n")
        print("1. Uma URL será aberta no seu navegador")
        print("2. Faça login com a CONTA GOOGLE DO CLIENTE")
        print("   (NÃO use sua conta pessoal de desenvolvedor!)")
        print("3. Autorize o aplicativo")
        print("4. Você será redirecionado (pode dar erro 404, é normal)")
        print("5. Copie a URL completa da barra de endereços")
        print("6. Cole aqui no terminal\n")
        
        input("Pressione ENTER para abrir o navegador...")
        
        # Abre navegador automaticamente
        print("\n🌐 Abrindo navegador...")
        webbrowser.open(auth_url)
        
        print(f"\n📎 Se o navegador não abrir, acesse manualmente:")
        print(f"   {auth_url}\n")
        print(f"📍 Após autorizar, você será redirecionado para:")
        print(f"   {Config.GOOGLE_REDIRECT_URI}")
        print(f"\n⚠️  A página pode mostrar erro 404 - isso é normal!")
        print(f"   Copie a URL completa da barra de endereços do navegador.\n")
        
        redirect_response = input("📋 Cole a URL completa aqui: ").strip()
        
        if not redirect_response:
            print("❌ URL não fornecida. Operação cancelada.")
            return None
        
        # Obtém token
        print("\n🔄 Obtendo token de acesso...")
        flow.fetch_token(authorization_response=redirect_response)
        credentials = flow.credentials
        
        # Salva credenciais
        creds_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        import json
        with open('google_credentials.json', 'w') as f:
            json.dump(creds_dict, f, indent=2)
        
        print("\n✅ Credenciais salvas em 'google_credentials.json'")
        print("⚠️  Este arquivo já está no .gitignore (seguro)")
        print("\n🎉 Autenticação OAuth2 configurada com sucesso!")
        
        return credentials
        
    except Exception as e:
        print(f"\n❌ Erro durante autenticação: {e}")
        print("\n💡 Verifique:")
        print("   - Se as credenciais no .env estão corretas")
        print("   - Se a URL de redirecionamento está configurada no Google Cloud")
        print("   - Se você copiou a URL completa do redirecionamento")
        return None


def load_google_credentials():
    """Carrega credenciais salvas"""
    import json
    
    if not os.path.exists('google_credentials.json'):
        return None
    
    with open('google_credentials.json', 'r') as f:
        creds_dict = json.load(f)
    
    return Credentials(
        token=creds_dict['token'],
        refresh_token=creds_dict.get('refresh_token'),
        token_uri=creds_dict['token_uri'],
        client_id=creds_dict['client_id'],
        client_secret=creds_dict['client_secret'],
        scopes=creds_dict['scopes']
    )


if __name__ == '__main__':
    setup_google_oauth()

