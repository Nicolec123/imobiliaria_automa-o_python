"""
Script para testar cada integração individualmente e diagnosticar problemas
"""
import sys
import traceback
from datetime import datetime

def testar_chatgpt():
    """Testa integração ChatGPT"""
    print("\n" + "="*70)
    print("1️⃣  TESTANDO CHATGPT")
    print("="*70)
    
    try:
        from integrations.chatgpt import ChatGPTIntegration
        
        print("   🔄 Inicializando...")
        chatgpt = ChatGPTIntegration()
        print("   ✅ Inicializado com sucesso!")
        
        print("   🔄 Testando análise...")
        test_data = {
            'nome': 'Teste',
            'telefone': '11999999999',
            'tipo_imovel': 'Apartamento'
        }
        analysis = chatgpt.analyze_form_data(test_data)
        print("   ✅ Análise realizada com sucesso!")
        print(f"   📊 Tipo de lead: {analysis.get('tipo_lead', 'N/A')}")
        
        return True, "Funcionando"
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERRO: {error_msg}")
        
        if 'proxies' in error_msg:
            print("\n   💡 DIAGNÓSTICO: Erro de compatibilidade de bibliotecas")
            print("   🔧 SOLUÇÃO:")
            print("      python -m pip install --upgrade 'openai>=1.12.0' 'httpx>=0.27.0'")
            print("      Depois reinicie o terminal")
        elif 'API' in error_msg or 'key' in error_msg.lower():
            print("\n   💡 DIAGNÓSTICO: Problema com API Key")
            print("   🔧 SOLUÇÃO: Verifique OPENAI_API_KEY no .env")
        else:
            print(f"\n   💡 Erro desconhecido: {error_msg}")
            traceback.print_exc()
        
        return False, error_msg


def testar_clickup():
    """Testa integração ClickUp"""
    print("\n" + "="*70)
    print("2️⃣  TESTANDO CLICKUP")
    print("="*70)
    
    try:
        from integrations.clickup import ClickUpIntegration
        
        print("   🔄 Inicializando...")
        clickup = ClickUpIntegration()
        print("   ✅ Inicializado com sucesso!")
        
        print("   🔄 Testando acesso à lista...")
        # Tenta acessar a lista configurada
        from config import Config
        list_id = Config.CLICKUP_LIST_ID
        
        import requests
        url = f"https://api.clickup.com/api/v2/list/{list_id}"
        headers = {
            "Authorization": Config.CLICKUP_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("   ✅ Acesso à lista OK!")
            data = response.json()
            print(f"   📋 Lista: {data.get('name', 'N/A')}")
            return True, "Funcionando"
        elif response.status_code == 401:
            print("   ❌ ERRO: Token inválido (401)")
            print("\n   💡 DIAGNÓSTICO: Token do ClickUp expirou ou está incorreto")
            print("   🔧 SOLUÇÃO:")
            print("      1. Gere um novo token em: https://app.clickup.com/settings/apps")
            print("      2. Atualize CLICKUP_API_KEY no .env")
            return False, "Token inválido"
        elif response.status_code == 404:
            print("   ❌ ERRO: List ID inválido (404)")
            print("\n   💡 DIAGNÓSTICO: List ID está incorreto")
            print("   🔧 SOLUÇÃO:")
            print("      1. Execute: python listar_listas_clickup.py")
            print("      2. Encontre o List ID correto")
            print("      3. Atualize CLICKUP_LIST_ID no .env")
            return False, "List ID inválido"
        else:
            print(f"   ❌ ERRO: Status {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False, f"Erro {response.status_code}"
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERRO: {error_msg}")
        traceback.print_exc()
        return False, error_msg


def testar_wasseller():
    """Testa integração Wasseller"""
    print("\n" + "="*70)
    print("3️⃣  TESTANDO WASSELLER")
    print("="*70)
    
    try:
        from integrations.wasseller import WassellerIntegration
        
        print("   🔄 Inicializando...")
        wasseller = WassellerIntegration()
        print("   ✅ Inicializado com sucesso!")
        
        print("   🔄 Testando envio de mensagem...")
        # Testa com um número de teste (não envia de verdade, só valida)
        from config import Config
        token = Config.WASSELLER_TOKEN
        api_url = Config.WASSELLER_API_URL
        
        if not token:
            print("   ❌ ERRO: WASSELLER_TOKEN não configurado")
            return False, "Token não configurado"
        
        print(f"   ✅ Token configurado: {token[:20]}...")
        print(f"   ✅ API URL: {api_url}")
        
        # Testa apenas a estrutura, não envia mensagem real
        print("   ✅ Configuração OK!")
        return True, "Funcionando"
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERRO: {error_msg}")
        
        if 'token' in error_msg.lower() or 'WASSELLER' in error_msg:
            print("\n   💡 DIAGNÓSTICO: Token ou configuração do Wasseller")
            print("   🔧 SOLUÇÃO: Verifique WASSELLER_TOKEN e WASSELLER_API_URL no .env")
        else:
            traceback.print_exc()
        
        return False, error_msg


def testar_google_forms():
    """Testa integração Google Forms"""
    print("\n" + "="*70)
    print("4️⃣  TESTANDO GOOGLE FORMS")
    print("="*70)
    
    try:
        from setup_google_auth import load_google_credentials
        
        print("   🔄 Verificando credenciais...")
        creds = load_google_credentials()
        
        if not creds:
            print("   ❌ ERRO: Credenciais não encontradas")
            print("\n   💡 DIAGNÓSTICO: OAuth2 não foi autorizado")
            print("   🔧 SOLUÇÃO:")
            print("      python setup_google_auth_simples.py")
            return False, "Credenciais não encontradas"
        
        print("   ✅ Credenciais encontradas")
        
        from integrations.google_forms import GoogleFormsIntegration
        print("   🔄 Inicializando...")
        google_forms = GoogleFormsIntegration(credentials=creds)
        print("   ✅ Inicializado com sucesso!")
        
        # Testa acesso a um form
        from config import Config
        forms_config = Config.get_forms_config()
        if forms_config.get('forms'):
            first_form = forms_config['forms'][0]
            form_id = first_form.get('id')
            form_name = first_form.get('name')
            
            print(f"   🔄 Testando acesso ao form: {form_name}")
            
            try:
                form_data = google_forms.service.forms().get(formId=form_id).execute()
                print(f"   ✅ Form acessado com sucesso!")
                print(f"   📋 Título: {form_data.get('info', {}).get('title', 'N/A')}")
                return True, "Funcionando"
            except Exception as e:
                if '404' in str(e):
                    print(f"   ❌ ERRO: Form não encontrado (404)")
                    print("\n   💡 DIAGNÓSTICO: Form não existe ou conta não tem acesso")
                    print("   🔧 SOLUÇÃO:")
                    print("      1. Execute: python verificar_conta_autorizada.py")
                    print("      2. Verifique se a conta autorizada tem acesso aos Forms")
                    return False, "Form não encontrado"
                else:
                    raise
        
        return True, "Funcionando"
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERRO: {error_msg}")
        traceback.print_exc()
        return False, error_msg


def testar_google_drive():
    """Testa integração Google Drive"""
    print("\n" + "="*70)
    print("5️⃣  TESTANDO GOOGLE DRIVE")
    print("="*70)
    
    try:
        from setup_google_auth import load_google_credentials
        
        print("   🔄 Verificando credenciais...")
        creds = load_google_credentials()
        
        if not creds:
            print("   ❌ ERRO: Credenciais não encontradas")
            print("\n   💡 DIAGNÓSTICO: OAuth2 não foi autorizado")
            print("   🔧 SOLUÇÃO:")
            print("      python setup_google_auth_simples.py")
            return False, "Credenciais não encontradas"
        
        print("   ✅ Credenciais encontradas")
        
        from integrations.google_drive import GoogleDriveIntegration
        print("   🔄 Inicializando...")
        google_drive = GoogleDriveIntegration(credentials=creds)
        print("   ✅ Inicializado com sucesso!")
        
        from config import Config
        folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        
        if folder_id:
            print(f"   ✅ Folder ID configurado: {folder_id[:30]}...")
        else:
            print("   ⚠️  Folder ID não configurado")
        
        return True, "Funcionando"
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERRO: {error_msg}")
        traceback.print_exc()
        return False, error_msg


def testar_chaves_na_mao():
    """Testa integração Chaves na Mão"""
    print("\n" + "="*70)
    print("6️⃣  TESTANDO CHAVES NA MÃO")
    print("="*70)
    
    try:
        from integrations.chaves_na_mao import ChavesNaMaoIntegration
        
        print("   🔄 Inicializando...")
        # Chaves na Mão não precisa de API Key para gerar XML
        chaves = ChavesNaMaoIntegration()
        print("   ✅ Inicializado com sucesso!")
        
        # Testa geração de XML
        print("   🔄 Testando geração de XML...")
        from integrations.chaves_na_mao_xml_generator import ChavesNaMaoXMLGenerator
        
        generator = ChavesNaMaoXMLGenerator()
        test_data = {
            'codigo': 'TEST001',
            'titulo': 'Teste',
            'tipo': 'Apartamento',
            'valor': '200000'
        }
        
        xml = generator.generate_property_xml(test_data)
        print("   ✅ XML gerado com sucesso!")
        print(f"   📄 Tamanho: {len(xml)} caracteres")
        
        return True, "Funcionando"
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERRO: {error_msg}")
        
        if 'API' in error_msg or 'key' in error_msg.lower():
            print("\n   💡 DIAGNÓSTICO: API Key não configurada (mas não é obrigatória)")
            print("   ℹ️  Chaves na Mão funciona sem API Key (gera XML)")
        else:
            traceback.print_exc()
        
        return False, error_msg


def main():
    """Executa todos os testes"""
    print("="*70)
    print("🧪 TESTE INDIVIDUAL DE INTEGRAÇÕES")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {}
    
    # Testa cada integração
    resultados['ChatGPT'] = testar_chatgpt()
    resultados['ClickUp'] = testar_clickup()
    resultados['Wasseller'] = testar_wasseller()
    resultados['Google Forms'] = testar_google_forms()
    resultados['Google Drive'] = testar_google_drive()
    resultados['Chaves na Mão'] = testar_chaves_na_mao()
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    funcionando = []
    com_erro = []
    
    for nome, (status, msg) in resultados.items():
        if status:
            funcionando.append(nome)
            print(f"   ✅ {nome}: {msg}")
        else:
            com_erro.append((nome, msg))
            print(f"   ❌ {nome}: {msg}")
    
    print(f"\n✅ Funcionando: {len(funcionando)}/{len(resultados)}")
    print(f"❌ Com erro: {len(com_erro)}/{len(resultados)}")
    
    if com_erro:
        print("\n" + "="*70)
        print("💡 O QUE PODE TER CAUSADO OS ERROS")
        print("="*70)
        
        print("\n🔍 Possíveis causas:")
        print("   1. Tokens/credenciais expiraram")
        print("   2. Bibliotecas foram atualizadas/desatualizadas")
        print("   3. Configurações no .env foram alteradas")
        print("   4. Serviços externos estão temporariamente fora do ar")
        print("   5. Conta Google foi alterada ou perdeu acesso")
        
        print("\n🔧 Ações recomendadas:")
        print("   1. Verifique o arquivo .env (não foi alterado?)")
        print("   2. Verifique se os tokens ainda são válidos")
        print("   3. Execute os comandos de correção sugeridos acima")
        print("   4. Reinicie o terminal após instalar bibliotecas")
    
    return resultados


if __name__ == '__main__':
    main()


