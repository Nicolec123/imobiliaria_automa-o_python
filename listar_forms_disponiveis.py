"""
Script para listar TODOS os Forms que a conta Google tem acesso
"""
from setup_google_auth import load_google_credentials
from integrations.google_forms import GoogleFormsIntegration
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def listar_forms_disponiveis():
    """Lista todos os Forms que a conta tem acesso"""
    
    print("="*70)
    print("🔍 LISTANDO TODOS OS FORMS DISPONÍVEIS")
    print("="*70)
    
    # Carrega credenciais
    creds = load_google_credentials()
    if not creds:
        print("\n❌ Credenciais Google não encontradas!")
        print("   Execute: python setup_google_auth_simples.py")
        return
    
    print("\n✅ Credenciais Google carregadas")
    
    try:
        # Cria serviço do Google Forms
        service = build('forms', 'v1', credentials=creds)
        
        print("\n📋 Buscando Forms...")
        print("   (A API do Google Forms não tem endpoint para listar todos)")
        print("   Vamos testar os IDs que você tem configurados...\n")
        
        # Testa cada Form do forms_config.json
        from config import Config
        forms_config = Config.get_forms_config()
        forms = forms_config.get('forms', [])
        
        forms_encontrados = []
        forms_nao_encontrados = []
        
        for form in forms:
            form_id = form.get('id')
            form_name = form.get('name')
            
            print(f"🔍 Testando: {form_name}")
            print(f"   ID: {form_id}")
            
            try:
                # Tenta acessar o form
                form_data = service.forms().get(formId=form_id).execute()
                
                print(f"   ✅ ENCONTRADO!")
                print(f"   📝 Título: {form_data.get('info', {}).get('title', 'N/A')}")
                
                # Tenta obter respostas
                try:
                    responses = service.forms().responses().list(formId=form_id).execute()
                    total_responses = len(responses.get('responses', []))
                    print(f"   📊 Total de respostas: {total_responses}")
                except HttpError as e:
                    if e.resp.status == 403:
                        print(f"   ⚠️  Sem permissão para ler respostas")
                    else:
                        print(f"   ⚠️  Erro ao obter respostas: {e}")
                
                forms_encontrados.append({
                    'id': form_id,
                    'name': form_name,
                    'title': form_data.get('info', {}).get('title', 'N/A')
                })
                
            except HttpError as e:
                if e.resp.status == 404:
                    print(f"   ❌ NÃO ENCONTRADO (404)")
                    forms_nao_encontrados.append({
                        'id': form_id,
                        'name': form_name,
                        'erro': '404 - Não encontrado'
                    })
                elif e.resp.status == 403:
                    print(f"   ❌ SEM PERMISSÃO (403)")
                    forms_nao_encontrados.append({
                        'id': form_id,
                        'name': form_name,
                        'erro': '403 - Sem permissão'
                    })
                else:
                    print(f"   ❌ Erro: {e}")
                    forms_nao_encontrados.append({
                        'id': form_id,
                        'name': form_name,
                        'erro': str(e)
                    })
            
            print()
        
        # Resumo
        print("="*70)
        print("📊 RESUMO")
        print("="*70)
        print(f"\n✅ Forms encontrados: {len(forms_encontrados)}")
        print(f"❌ Forms não encontrados: {len(forms_nao_encontrados)}")
        
        if forms_encontrados:
            print("\n✅ FORMS QUE FUNCIONAM:")
            for form in forms_encontrados:
                print(f"   - {form['name']}: {form['id']}")
        
        if forms_nao_encontrados:
            print("\n❌ FORMS COM PROBLEMA:")
            for form in forms_nao_encontrados:
                print(f"   - {form['name']}: {form['erro']}")
            print("\n💡 POSSÍVEIS CAUSAS:")
            print("   1. IDs incorretos")
            print("   2. Forms foram deletados")
            print("   3. Forms estão em outra conta Google")
            print("   4. Você não tem acesso a esses Forms")
            print("   5. Forms foram movidos ou renomeados")
            print("\n💡 SOLUÇÃO:")
            print("   - Verifique os IDs diretamente nas URLs dos Forms")
            print("   - Confirme com o cliente se os Forms ainda existem")
            print("   - Verifique se está usando a conta Google correta")
        
        # Testa acesso ao Drive também
        print("\n" + "="*70)
        print("🔍 TESTANDO ACESSO AO GOOGLE DRIVE")
        print("="*70)
        
        try:
            drive_service = build('drive', 'v3', credentials=creds)
            # Tenta listar arquivos
            results = drive_service.files().list(pageSize=5, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if files:
                print(f"\n✅ Acesso ao Google Drive OK!")
                print(f"   Encontrados {len(files)} arquivos (mostrando 5 primeiros):")
                for file in files:
                    print(f"   - {file.get('name')}: {file.get('id')}")
            else:
                print("\n⚠️  Nenhum arquivo encontrado no Drive")
                
        except Exception as e:
            print(f"\n❌ Erro ao acessar Google Drive: {e}")
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    listar_forms_disponiveis()

