"""
Script para instalar todas as dependências do projeto
"""
import subprocess
import sys
import os


def install_requirements():
    """Instala dependências do requirements.txt"""
    print("="*60)
    print("INSTALANDO DEPENDÊNCIAS")
    print("="*60)
    
    if not os.path.exists('requirements.txt'):
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    
    try:
        print("\n📦 Instalando pacotes do requirements.txt...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Dependências instaladas com sucesso!")
        print("\n📋 Pacotes instalados:")
        
        # Lista pacotes principais
        packages = [
            'python-dotenv',
            'requests',
            'flask',
            'flask-cors',
            'google-api-python-client',
            'google-auth-oauthlib',
            'openai',
        ]
        
        for package in packages:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    version = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
                    if version:
                        print(f"   ✅ {package} - {version[0].replace('Version: ', '')}")
            except:
                pass
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False


def verify_installation():
    """Verifica se as dependências principais estão instaladas"""
    print("\n" + "="*60)
    print("VERIFICANDO INSTALAÇÃO")
    print("="*60)
    
    required_modules = [
        ('dotenv', 'python-dotenv'),
        ('requests', 'requests'),
        ('flask', 'flask'),
        ('flask_cors', 'flask-cors'),
        ('google.oauth2', 'google-api-python-client'),
        ('google_auth_oauthlib', 'google-auth-oauthlib'),
        ('openai', 'openai'),
    ]
    
    all_ok = True
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - NÃO INSTALADO")
            all_ok = False
    
    return all_ok


if __name__ == '__main__':
    print("\n" + "="*60)
    print("INSTALADOR DE DEPENDÊNCIAS")
    print("="*60)
    print("Este script instalará todas as dependências necessárias\n")
    
    # Instala dependências
    success = install_requirements()
    
    if success:
        # Verifica instalação
        verified = verify_installation()
        
        if verified:
            print("\n" + "="*60)
            print("✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print("\nPróximos passos:")
            print("  1. Execute: python setup_and_test.py")
            print("  2. Execute: python test_automation.py")
            print("  3. Execute: python app.py")
        else:
            print("\n" + "="*60)
            print("⚠️  INSTALAÇÃO PARCIAL")
            print("="*60)
            print("Algumas dependências podem não ter sido instaladas corretamente.")
            print("Tente executar manualmente: pip install -r requirements.txt")
    else:
        print("\n" + "="*60)
        print("❌ FALHA NA INSTALAÇÃO")
        print("="*60)
        print("Tente executar manualmente: pip install -r requirements.txt")

