"""
Script principal para executar automações do sistema
"""
import os
import sys
import time
from datetime import datetime
from config import Config
from orchestrator import IntegrationOrchestrator
from setup_google_auth import load_google_credentials


def check_environment():
    """Verifica se o ambiente está configurado"""
    print("="*60)
    print("VERIFICAÇÃO DO AMBIENTE")
    print("="*60)
    
    issues = []
    
    # Verifica OpenAI
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key':
        issues.append("⚠️  OpenAI API Key não configurada")
    else:
        print("✅ OpenAI API Key configurada")
    
    # Verifica Google Drive
    if not Config.GOOGLE_DRIVE_FOLDER_ID or Config.GOOGLE_DRIVE_FOLDER_ID == 'your_drive_folder_id':
        issues.append("⚠️  Google Drive Folder ID não configurado")
    else:
        print(f"✅ Google Drive Folder ID configurado: {Config.GOOGLE_DRIVE_FOLDER_ID[:30]}...")
    
    # Verifica formulários
    forms = Config.get_forms_config()
    if len(forms.get('forms', [])) > 0:
        print(f"✅ {len(forms['forms'])} formulários configurados")
    else:
        issues.append("⚠️  Nenhum formulário configurado")
    
    # Verifica outras credenciais (warnings)
    if not Config.GOOGLE_CLIENT_ID or Config.GOOGLE_CLIENT_ID == 'your_google_client_id':
        issues.append("⚠️  Google Client ID não configurado (necessário para Forms/Drive)")
    
    if not Config.CLICKUP_API_KEY or Config.CLICKUP_API_KEY == 'your_clickup_api_key':
        issues.append("⚠️  ClickUp API Key não configurada")
    
    if not Config.CHAVES_NA_MAO_API_KEY or Config.CHAVES_NA_MAO_API_KEY == 'your_chaves_na_mao_api_key':
        issues.append("⚠️  Chaves na Mão API Key não configurada")
    
    if not Config.WASSELLER_API_KEY or Config.WASSELLER_API_KEY == 'your_wasseller_api_key':
        issues.append("⚠️  Wasseller API Key não configurada")
    
    if issues:
        print("\n⚠️  AVISOS:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Ambiente totalmente configurado!")
    
    return len(issues) == 0


def sync_all_forms_automation():
    """Automação para sincronizar todos os formulários"""
    print("\n" + "="*60)
    print("AUTOMAÇÃO: Sincronização de Formulários")
    print("="*60)
    
    try:
        orchestrator = IntegrationOrchestrator()
        
        # Carrega credenciais Google se disponíveis
        google_creds = load_google_credentials()
        if google_creds:
            orchestrator.set_google_credentials(google_creds)
            print("✅ Credenciais Google carregadas")
        else:
            print("⚠️  Credenciais Google não encontradas. Execute: python setup_google_auth.py")
            return
        
        # Obtém todos os formulários
        form_ids = Config.get_form_ids()
        forms_config = Config.get_forms_config()
        
        if not form_ids:
            print("❌ Nenhum formulário configurado")
            return
        
        print(f"\n📋 Sincronizando {len(form_ids)} formulários...\n")
        
        total_responses = 0
        for form_id in form_ids:
            form_info = Config.get_form_by_id(form_id)
            form_name = form_info['name'] if form_info else form_id
            
            print(f"🔄 Processando: {form_name}")
            print(f"   ID: {form_id}")
            
            try:
                result = orchestrator.sync_google_forms(form_id)
                responses = result.get('responses_processed', 0)
                total_responses += responses
                
                if responses > 0:
                    print(f"   ✅ {responses} resposta(s) processada(s)")
                else:
                    print(f"   ℹ️  Nenhuma nova resposta")
                
                if result.get('errors'):
                    print(f"   ⚠️  {len(result['errors'])} erro(s)")
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
            
            print()
        
        print(f"✅ Sincronização concluída: {total_responses} resposta(s) processada(s) no total")
        
    except Exception as e:
        print(f"❌ Erro na automação: {str(e)}")


def process_xml_automation(xml_file_path=None):
    """Automação para processar XML do Chaves na Mão"""
    print("\n" + "="*60)
    print("AUTOMAÇÃO: Processamento XML Chaves na Mão")
    print("="*60)
    
    try:
        orchestrator = IntegrationOrchestrator()
        
        if not Config.CHAVES_NA_MAO_API_KEY or Config.CHAVES_NA_MAO_API_KEY == 'your_chaves_na_mao_api_key':
            print("⚠️  Chaves na Mão API Key não configurada")
            print("   Testando apenas parse do XML (sem importação)...")
            
            # Testa parse sem API
            from integrations.chaves_na_mao import ChavesNaMaoIntegration
            chaves = ChavesNaMaoIntegration()
            chaves.api_key = "test_key"  # Temporário para teste
            
            # XML de exemplo
            xml_example = """<?xml version="1.0" encoding="UTF-8"?>
<Document>
    <imoveis>
        <imovel>
            <referencia>AP01</referencia>
            <titulo>Apartamento Exemplo 01</titulo>
            <valor>210000</valor>
            <cidade>Curitiba</cidade>
            <estado>PR</estado>
        </imovel>
    </imoveis>
</Document>"""
            
            try:
                property_data = chaves.parse_xml_property(xml_example)
                print("✅ Parse XML funcionando corretamente")
                print(f"   Referência: {property_data.get('referencia')}")
                print(f"   Título: {property_data.get('titulo')}")
                print(f"   Valor: {property_data.get('valor')}")
            except Exception as e:
                print(f"❌ Erro no parse: {str(e)}")
            
            return
        
        if xml_file_path and os.path.exists(xml_file_path):
            print(f"📄 Processando arquivo: {xml_file_path}")
            results = orchestrator.chaves_na_mao.import_properties_from_xml_file(xml_file_path)
            
            successful = sum(1 for r in results if r.get('success'))
            failed = sum(1 for r in results if not r.get('success'))
            
            print(f"✅ Importação concluída:")
            print(f"   Sucesso: {successful}")
            print(f"   Falhas: {failed}")
            print(f"   Total: {len(results)}")
        else:
            print("⚠️  Arquivo XML não fornecido ou não encontrado")
            print("   Use: python run_automation.py --xml caminho/para/arquivo.xml")
    
    except Exception as e:
        print(f"❌ Erro na automação: {str(e)}")


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("SISTEMA DE AUTOMAÇÃO - INTEGRAÇÃO IMOBILIÁRIA")
    print("="*60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verifica ambiente
    env_ok = check_environment()
    
    # Menu de opções
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--test':
            # Executa testes
            from test_automation import TestAutomation
            tester = TestAutomation()
            tester.run_all_tests()
        
        elif command == '--sync':
            # Sincroniza formulários
            sync_all_forms_automation()
        
        elif command == '--xml':
            # Processa XML
            xml_path = sys.argv[2] if len(sys.argv) > 2 else None
            process_xml_automation(xml_path)
        
        elif command == '--all':
            # Executa tudo
            from test_automation import TestAutomation
            tester = TestAutomation()
            tester.run_all_tests()
            print("\n")
            sync_all_forms_automation()
        
        else:
            print(f"Comando desconhecido: {command}")
            print_help()
    else:
        print_help()


def print_help():
    """Exibe ajuda"""
    print("\n" + "="*60)
    print("OPÇÕES DISPONÍVEIS")
    print("="*60)
    print("  python run_automation.py --test    # Executa testes automatizados")
    print("  python run_automation.py --sync    # Sincroniza todos os formulários")
    print("  python run_automation.py --xml [arquivo]  # Processa XML do Chaves na Mão")
    print("  python run_automation.py --all     # Executa tudo")
    print("\nExemplos:")
    print("  python run_automation.py --test")
    print("  python run_automation.py --sync")
    print("  python run_automation.py --xml imoveis.xml")
    print()


if __name__ == '__main__':
    main()

