"""
Script para corrigir o modelo ChatGPT no arquivo .env
"""
import os
import re


def corrigir_modelo_env():
    """Corrige o modelo ChatGPT no arquivo .env"""
    
    print("="*70)
    print("  🔧 CORREÇÃO DO MODELO CHATGPT")
    print("="*70)
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print(f"❌ Arquivo {env_file} não encontrado!")
        print("   Execute primeiro: python create_env.py")
        return False
    
    try:
        # Lê o arquivo
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se precisa corrigir
        if 'gpt-4-turbo-preview' in content:
            print("⚠️  Modelo antigo encontrado: gpt-4-turbo-preview")
            print("🔄 Atualizando para: gpt-4o-mini")
            
            # Substitui o modelo
            content = content.replace(
                'CHATGPT_MODEL=gpt-4-turbo-preview',
                'CHATGPT_MODEL=gpt-4o-mini'
            )
            
            # Salva o arquivo
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Modelo atualizado com sucesso!")
            print("\n💡 Execute novamente o teste de automação para verificar.")
            return True
        else:
            print("✅ Modelo já está correto!")
            if 'gpt-4o-mini' in content or 'gpt-4o' in content:
                print("   Modelo atual: gpt-4o-mini (ou similar)")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir: {str(e)}")
        return False


if __name__ == '__main__':
    corrigir_modelo_env()

