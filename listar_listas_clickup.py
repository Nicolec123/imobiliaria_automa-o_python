"""
Script para listar todas as listas do ClickUp e encontrar o List ID correto
"""
import requests
from config import Config

def listar_listas_clickup():
    """Lista todas as listas disponíveis no ClickUp"""
    
    print("="*70)
    print("📋 LISTAR LISTAS DO CLICKUP")
    print("="*70)
    
    token = Config.CLICKUP_API_KEY
    space_id = Config.CLICKUP_SPACE_ID
    
    if not token or token == 'your_clickup_api_key':
        print("\n❌ Token não configurado!")
        return
    
    if not space_id or space_id == 'your_clickup_space_id':
        print("\n❌ Space ID não configurado!")
        return
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print(f"\n📋 Space ID: {space_id}")
    print(f"🔍 Buscando listas...\n")
    
    # Método 1: Listar listas do Space diretamente
    print("="*70)
    print("MÉTODO 1: Listas do Space")
    print("="*70)
    
    try:
        url = f"https://api.clickup.com/api/v2/space/{space_id}/list"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            lists = response.json().get('lists', [])
            
            if lists:
                print(f"\n✅ {len(lists)} listas encontradas:\n")
                for i, lista in enumerate(lists, 1):
                    list_id = lista.get('id', 'N/A')
                    list_name = lista.get('name', 'N/A')
                    folder_name = lista.get('folder', {}).get('name', 'Sem pasta')
                    print(f"   {i}. {list_name}")
                    print(f"      📋 List ID: {list_id}")
                    print(f"      📂 Folder: {folder_name}")
                    print()
            else:
                print("⚠️  Nenhuma lista encontrada diretamente no Space")
        else:
            print(f"⚠️  Erro ao buscar listas do Space: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Método 2: Listar folders e depois listas de cada folder
    print("="*70)
    print("MÉTODO 2: Folders e suas Listas")
    print("="*70)
    
    try:
        # Lista folders do Space
        folders_url = f"https://api.clickup.com/api/v2/space/{space_id}/folder"
        folders_response = requests.get(folders_url, headers=headers)
        
        if folders_response.status_code == 200:
            folders = folders_response.json().get('folders', [])
            
            if folders:
                print(f"\n✅ {len(folders)} pastas encontradas:\n")
                
                for folder in folders:
                    folder_id = folder.get('id', 'N/A')
                    folder_name = folder.get('name', 'N/A')
                    
                    print(f"📂 {folder_name} (ID: {folder_id})")
                    
                    # Lista listas dentro da pasta
                    try:
                        folder_lists_url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
                        folder_lists_response = requests.get(folder_lists_url, headers=headers)
                        
                        if folder_lists_response.status_code == 200:
                            folder_lists = folder_lists_response.json().get('lists', [])
                            
                            if folder_lists:
                                for lista in folder_lists:
                                    list_id = lista.get('id', 'N/A')
                                    list_name = lista.get('name', 'N/A')
                                    print(f"   📋 {list_name}")
                                    print(f"      List ID: {list_id}")
                                    print()
                            else:
                                print("   ⚠️  Nenhuma lista nesta pasta")
                        else:
                            print(f"   ⚠️  Erro ao buscar listas: {folder_lists_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Erro ao buscar listas da pasta: {e}")
                    
                    print()
            else:
                print("⚠️  Nenhuma pasta encontrada")
        else:
            print(f"⚠️  Erro ao buscar pastas: {folders_response.status_code}")
            print(f"   Resposta: {folders_response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("="*70)
    print("💡 INSTRUÇÕES")
    print("="*70)
    print("\n1. Encontre a lista que você quer usar (ex: 'Imóveis')")
    print("2. Copie o 'List ID' dessa lista")
    print("3. Atualize CLICKUP_LIST_ID no arquivo .env")
    print("4. Teste novamente: python testar_token_clickup.py")

if __name__ == '__main__':
    try:
        listar_listas_clickup()
    except Exception as e:
        print(f"\n❌ Erro: {e}")

