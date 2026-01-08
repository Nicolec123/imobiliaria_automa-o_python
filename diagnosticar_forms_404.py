"""
Script para diagnosticar por que os Forms pararam de funcionar
"""
from setup_google_auth import load_google_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
from datetime import datetime

def diagnosticar_forms():
    """Diagnostica por que os Forms pararam de funcionar"""
    
    print("="*70)
    print("🔍 DIAGNÓSTICO: Por Que Forms Pararam de Funcionar")
    print("="*70)
    
    # 1. Verifica credenciais
    print("\n1️⃣  VERIFICANDO CREDENCIAIS OAUTH2")
    print("-" * 70)
    
    creds = load_google_credentials()
    if not creds:
        print("❌ Credenciais não encontradas!")
        print("   Isso explica por que não funciona!")
        return
    
    print("✅ Credenciais encontradas")
    
    # Verifica informações da conta autorizada
    try:
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        
        print(f"   📧 Email autorizado: {user_info.get('email', 'N/A')}")
        print(f"   👤 Nome: {user_info.get('name', 'N/A')}")
        print(f"   🆔 ID: {user_info.get('id', 'N/A')}")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao obter info do usuário: {e}")
    
    # 2. Verifica quando credenciais foram criadas
    print("\n2️⃣  VERIFICANDO DATA DAS CREDENCIAIS")
    print("-" * 70)
    
    if os.path.exists('google_credentials.json'):
        stat = os.stat('google_credentials.json')
        created = datetime.fromtimestamp(stat.st_ctime)
        modified = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"   📅 Criado em: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📅 Modificado em: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verifica se token expirou
        with open('google_credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        if 'token' in creds_data:
            print(f"   ✅ Token presente")
        else:
            print(f"   ❌ Token ausente!")
    
    # 3. Testa acesso aos Forms
    print("\n3️⃣  TESTANDO ACESSO AOS FORMS")
    print("-" * 70)
    
    from config import Config
    forms_config = Config.get_forms_config()
    forms = forms_config.get('forms', [])
    
    forms_service = build('forms', 'v1', credentials=creds)
    
    resultados = {
        'funcionando': [],
        '404': [],
        '403': [],
        'outros_erros': []
    }
    
    for form in forms[:3]:  # Testa só os 3 primeiros para não demorar
        form_id = form.get('id')
        form_name = form.get('name')
        
        try:
            form_data = forms_service.forms().get(formId=form_id).execute()
            resultados['funcionando'].append(form_name)
            print(f"   ✅ {form_name}: FUNCIONANDO")
            
        except HttpError as e:
            if e.resp.status == 404:
                resultados['404'].append(form_name)
                print(f"   ❌ {form_name}: 404 - Não encontrado")
            elif e.resp.status == 403:
                resultados['403'].append(form_name)
                print(f"   ❌ {form_name}: 403 - Sem permissão")
            else:
                resultados['outros_erros'].append((form_name, str(e)))
                print(f"   ❌ {form_name}: Erro {e.resp.status}")
        except Exception as e:
            resultados['outros_erros'].append((form_name, str(e)))
            print(f"   ❌ {form_name}: Erro desconhecido - {e}")
    
    # 4. Testa se token ainda é válido
    print("\n4️⃣  VERIFICANDO SE TOKEN AINDA É VÁLIDO")
    print("-" * 70)
    
    try:
        # Tenta usar o token para acessar algo simples
        drive_service = build('drive', 'v3', credentials=creds)
        results = drive_service.files().list(pageSize=1).execute()
        print("   ✅ Token ainda é válido (conseguiu acessar Drive)")
    except HttpError as e:
        if e.resp.status == 401:
            print("   ❌ Token EXPIRADO ou INVÁLIDO!")
            print("   💡 Solução: Reautorize com: python setup_google_auth_simples.py")
        else:
            print(f"   ⚠️  Erro ao testar token: {e}")
    except Exception as e:
        print(f"   ⚠️  Erro: {e}")
    
    # 5. Resumo e diagnóstico
    print("\n" + "="*70)
    print("📊 DIAGNÓSTICO FINAL")
    print("="*70)
    
    if resultados['funcionando']:
        print(f"\n✅ {len(resultados['funcionando'])} Forms funcionando")
    
    if resultados['404']:
        print(f"\n❌ {len(resultados['404'])} Forms com 404")
        print("   💡 Possíveis causas:")
        print("      1. Forms foram deletados")
        print("      2. Forms foram movidos para outra conta")
        print("      3. IDs dos Forms estão incorretos")
        print("      4. Você está usando conta Google diferente da que tem os Forms")
    
    if resultados['403']:
        print(f"\n❌ {len(resultados['403'])} Forms com 403 (sem permissão)")
        print("   💡 Solução: Reautorize com a conta que tem acesso aos Forms")
    
    if resultados['outros_erros']:
        print(f"\n⚠️  {len(resultados['outros_erros'])} Forms com outros erros")
        for form_name, erro in resultados['outros_erros']:
            print(f"      - {form_name}: {erro}")
    
    # Recomendações
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÕES")
    print("="*70)
    
    if resultados['404'] and not resultados['funcionando']:
        print("\n🔴 TODOS OS FORMS DÃO 404")
        print("\n   Ações sugeridas:")
        print("   1. Verifique se está usando a CONTA GOOGLE CORRETA")
        print("      - Abra um Form no navegador")
        print("      - Veja qual conta está logada")
        print("      - Compare com o email autorizado acima")
        print("\n   2. Se a conta estiver errada:")
        print("      - Delete: google_credentials.json")
        print("      - Execute: python setup_google_auth_simples.py")
        print("      - Use a CONTA QUE TEM OS FORMS")
        print("\n   3. Verifique se os IDs dos Forms estão corretos")
        print("      - Abra cada Form no navegador")
        print("      - Copie o ID da URL")
        print("      - Compare com forms_config.json")

if __name__ == '__main__':
    diagnosticar_forms()

