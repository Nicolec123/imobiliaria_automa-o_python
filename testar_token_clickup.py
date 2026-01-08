"""
Script para testar qual token do ClickUp está funcionando
"""
import requests
from config import Config

def testar_token_clickup():
    """Testa o token do ClickUp"""
    
    print("="*70)
    print("🧪 TESTE DE TOKEN CLICKUP")
    print("="*70)
    
    token_atual = Config.CLICKUP_API_KEY
    team_id = Config.CLICKUP_TEAM_ID
    list_id = Config.CLICKUP_LIST_ID
    
    print(f"\n📋 Configuração Atual:")
    print(f"   Token: {token_atual[:20]}...{token_atual[-10:] if token_atual else 'NÃO CONFIGURADO'}")
    print(f"   Team ID: {team_id}")
    print(f"   List ID: {list_id}")
    
    if not token_atual or token_atual == 'your_clickup_api_key':
        print("\n❌ Token não configurado ou ainda está com valor padrão!")
        return
    
    # Testa o token atual - primeiro verifica o usuário
    print("\n" + "="*70)
    print("TESTANDO TOKEN ATUAL")
    print("="*70)
    
    headers = {
        "Authorization": token_atual,
        "Content-Type": "application/json"
    }
    
    # Passo 1: Testa se o token é válido verificando o usuário
    print("\n1️⃣  Verificando token (GET /user)...")
    try:
        user_url = "https://api.clickup.com/api/v2/user"
        user_response = requests.get(user_url, headers=headers)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   ✅ Token válido!")
            print(f"   👤 Usuário: {user_data.get('user', {}).get('username', 'N/A')}")
            print(f"   📧 Email: {user_data.get('user', {}).get('email', 'N/A')}")
        elif user_response.status_code == 401:
            print(f"   ❌ Token inválido!")
            print(f"   Erro: {user_response.json()}")
            print("\n💡 Gere um novo token:")
            print("   - Acesse: https://app.clickup.com/settings/apps")
            print("   - Clique em 'Generate' para criar novo token")
            return False
        else:
            print(f"   ⚠️  Status: {user_response.status_code}")
            print(f"   Resposta: {user_response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # Passo 2: Testa acesso à lista
    print("\n2️⃣  Verificando List ID...")
    try:
        list_url = f"https://api.clickup.com/api/v2/list/{list_id}"
        list_response = requests.get(list_url, headers=headers)
        
        if list_response.status_code == 200:
            print(f"   ✅ List ID válido!")
            list_data = list_response.json()
            print(f"   📋 Lista: {list_data.get('name', 'N/A')}")
            print(f"   📁 Space: {list_data.get('space', {}).get('name', 'N/A')}")
            print(f"   📂 Folder: {list_data.get('folder', {}).get('name', 'N/A')}")
            return True
        elif list_response.status_code == 400:
            error_data = list_response.json()
            print(f"   ❌ List ID inválido!")
            print(f"   Erro: {error_data}")
            print("\n💡 Possíveis causas:")
            print("   1. O List ID está incorreto")
            print("   2. O List ID não existe mais")
            print("   3. Você não tem acesso a essa lista")
            print("\n💡 Como encontrar o List ID correto:")
            print("   1. Abra a lista no ClickUp")
            print("   2. A URL será: https://app.clickup.com/.../v/l/LIST_ID_AQUI/...")
            print("   3. O List ID está na URL após '/v/l/'")
            return False
        elif list_response.status_code == 404:
            print(f"   ❌ Lista não encontrada!")
            print(f"   Verifique se o List ID está correto")
            return False
        else:
            print(f"   ⚠️  Status: {list_response.status_code}")
            print(f"   Resposta: {list_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

if __name__ == '__main__':
    testar_token_clickup()

