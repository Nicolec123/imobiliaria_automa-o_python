"""
Script completo de setup e validação do sistema
"""
import os
import sys
from datetime import datetime


def print_banner():
    """Imprime banner do sistema"""
    print("\n" + "="*70)
    print(" " * 15 + "SISTEMA DE INTEGRAÇÃO IMOBILIÁRIA")
    print(" " * 20 + "Setup e Validação Completa")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def check_env_file():
    """Verifica se arquivo .env existe"""
    print("1️⃣  Verificando arquivo .env...")
    
    if os.path.exists('.env'):
        print("   ✅ Arquivo .env encontrado")
        return True
    else:
        print("   ❌ Arquivo .env não encontrado")
        print("   📝 Criando arquivo .env a partir do env.example...")
        
        if os.path.exists('env.example'):
            import shutil
            shutil.copy('env.example', '.env')
            print("   ✅ Arquivo .env criado")
            print("   ⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais!")
            return True
        else:
            print("   ❌ Arquivo env.example não encontrado")
            return False


def validate_config():
    """Valida configurações básicas"""
    print("\n2️⃣  Validando configurações...")
    
    try:
        from config import Config
        
        configs_ok = []
        configs_missing = []
        
        # Verifica OpenAI
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY.startswith('sk-'):
            configs_ok.append("OpenAI API Key")
        else:
            configs_missing.append("OpenAI API Key")
        
        # Verifica Google Drive
        if Config.GOOGLE_DRIVE_FOLDER_ID and len(Config.GOOGLE_DRIVE_FOLDER_ID) > 10:
            configs_ok.append("Google Drive Folder ID")
        else:
            configs_missing.append("Google Drive Folder ID")
        
        # Verifica formulários
        forms = Config.get_forms_config()
        if len(forms.get('forms', [])) > 0:
            configs_ok.append(f"Formulários ({len(forms['forms'])} configurados)")
        else:
            configs_missing.append("Formulários")
        
        # Lista configs opcionais
        optional_configs = []
        if not Config.GOOGLE_CLIENT_ID or Config.GOOGLE_CLIENT_ID == 'your_google_client_id':
            optional_configs.append("Google Client ID/Secret")
        if not Config.CLICKUP_API_KEY or Config.CLICKUP_API_KEY == 'your_clickup_api_key':
            optional_configs.append("ClickUp API Key")
        if not Config.CHAVES_NA_MAO_API_KEY or Config.CHAVES_NA_MAO_API_KEY == 'your_chaves_na_mao_api_key':
            optional_configs.append("Chaves na Mão API Key")
        if not Config.WASSELLER_API_KEY or Config.WASSELLER_API_KEY == 'your_wasseller_api_key':
            optional_configs.append("Wasseller API Key")
        
        print(f"   ✅ Configurado: {len(configs_ok)}")
        for config in configs_ok:
            print(f"      - {config}")
        
        if configs_missing:
            print(f"   ❌ Faltando: {len(configs_missing)}")
            for config in configs_missing:
                print(f"      - {config}")
        
        if optional_configs:
            print(f"   ⚠️  Opcional (não configurado): {len(optional_configs)}")
            for config in optional_configs:
                print(f"      - {config}")
        
        return len(configs_missing) == 0
        
    except Exception as e:
        print(f"   ❌ Erro ao validar: {str(e)}")
        return False


def run_tests():
    """Executa testes automatizados"""
    print("\n3️⃣  Executando testes automatizados...")
    
    try:
        from test_automation import TestAutomation
        
        tester = TestAutomation()
        results = tester.run_all_tests()
        
        print(f"\n   📊 Resultado: {results['passed']}/{results['total']} testes aprovados")
        
        return results['failed'] == 0
        
    except Exception as e:
        print(f"   ❌ Erro ao executar testes: {str(e)}")
        return False


def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "="*70)
    print("PRÓXIMOS PASSOS")
    print("="*70)
    
    steps = [
        "1. Configure as credenciais faltantes no arquivo .env",
        "2. Execute 'python setup_google_auth.py' para autenticação Google",
        "3. Execute 'python run_automation.py --test' para validar tudo",
        "4. Execute 'python run_automation.py --sync' para sincronizar formulários",
        "5. Execute 'python app.py' para iniciar o servidor Flask",
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n" + "="*70)


def main():
    """Função principal"""
    print_banner()
    
    # Passo 1: Verifica .env
    env_ok = check_env_file()
    
    if not env_ok:
        print("\n❌ Não foi possível continuar sem o arquivo .env")
        return
    
    # Passo 2: Valida configurações
    config_ok = validate_config()
    
    # Passo 3: Executa testes
    if config_ok:
        tests_ok = run_tests()
    else:
        print("\n⚠️  Algumas configurações estão faltando. Testes podem falhar.")
        tests_ok = False
    
    # Resumo final
    print("\n" + "="*70)
    print("RESUMO DO SETUP")
    print("="*70)
    
    status_icon = "✅" if (env_ok and config_ok and tests_ok) else "⚠️"
    print(f"{status_icon} Status: ", end="")
    
    if env_ok and config_ok and tests_ok:
        print("Sistema pronto para uso!")
    elif env_ok and config_ok:
        print("Sistema configurado, mas alguns testes falharam")
    elif env_ok:
        print("Arquivo .env criado, mas configurações estão incompletas")
    else:
        print("Setup incompleto")
    
    show_next_steps()


if __name__ == '__main__':
    main()

