"""
Script interativo para configurar Google Cloud OAuth2
Guia passo a passo e configuração automática
"""
import os
import re
from dotenv import load_dotenv

load_dotenv()

def print_header():
    """Imprime cabeçalho do script"""
    print("\n" + "="*60)
    print("🔐 CONFIGURAÇÃO GOOGLE CLOUD - GUIA INTERATIVO")
    print("="*60 + "\n")

def print_step(step_num, title):
    """Imprime um passo do guia"""
    print(f"\n{'='*60}")
    print(f"PASSO {step_num}: {title}")
    print('='*60)

def validate_client_id(client_id):
    """Valida formato do Client ID"""
    if not client_id:
        return False, "Client ID não pode estar vazio"
    
    # Formato típico: 123456789-abc.apps.googleusercontent.com
    pattern = r'^\d+-[\w-]+\.apps\.googleusercontent\.com$'
    if not re.match(pattern, client_id):
        return False, "Formato inválido. Deve ser: 123456789-abc.apps.googleusercontent.com"
    
    return True, "OK"

def validate_client_secret(client_secret):
    """Valida formato do Client Secret"""
    if not client_secret:
        return False, "Client Secret não pode estar vazio"
    
    # Formato típico: GOCSPX-...
    if not client_secret.startswith('GOCSPX-'):
        return False, "Formato inválido. Deve começar com 'GOCSPX-'"
    
    return True, "OK"

def update_env_file(client_id, client_secret):
    """Atualiza arquivo .env com as credenciais"""
    env_path = '.env'
    
    # Lê arquivo .env se existir
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        # Cria novo arquivo baseado no env.example
        if os.path.exists('env.example'):
            with open('env.example', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
    
    # Atualiza ou adiciona GOOGLE_CLIENT_ID
    updated = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('GOOGLE_CLIENT_ID='):
            new_lines.append(f'GOOGLE_CLIENT_ID={client_id}\n')
            updated = True
        elif line.strip().startswith('GOOGLE_CLIENT_SECRET='):
            new_lines.append(f'GOOGLE_CLIENT_SECRET={client_secret}\n')
            updated = True
        else:
            new_lines.append(line)
    
    # Se não encontrou, adiciona no final
    if not any('GOOGLE_CLIENT_ID=' in line for line in new_lines):
        # Adiciona seção Google APIs se não existir
        if not any('Google APIs' in line for line in new_lines):
            new_lines.insert(0, '# Google APIs\n')
        new_lines.append(f'GOOGLE_CLIENT_ID={client_id}\n')
    
    if not any('GOOGLE_CLIENT_SECRET=' in line for line in new_lines):
        new_lines.append(f'GOOGLE_CLIENT_SECRET={client_secret}\n')
    
    # Escreve arquivo atualizado
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True

def main():
    """Função principal"""
    print_header()
    
    print("Este script vai te guiar para configurar o Google Cloud OAuth2.")
    print("\n" + "="*60)
    print("⚠️  ATENÇÃO MUITO IMPORTANTE!")
    print("="*60)
    print("\n🔴 A configuração DEVE ser feita na CONTA GOOGLE DO CLIENTE!")
    print("   (A mesma conta que tem os Google Forms e Google Drive)")
    print("\n❌ NÃO use sua conta pessoal de desenvolvedor")
    print("❌ NÃO use conta de teste")
    print("\n✅ Use a conta Google do CLIENTE que vai usar o sistema")
    print("✅ A conta que tem acesso aos formulários e pastas do Drive")
    print("\n" + "="*60 + "\n")
    
    input("Pressione ENTER para continuar...")
    
    # Passo 1: Explicação
    print_step(1, "ENTENDENDO O PROCESSO")
    print("""
Você precisa criar credenciais OAuth2 no Google Cloud Console.
Isso é GRATUITO e leva cerca de 10 minutos.

O que você vai fazer:
1. Acessar Google Cloud Console
2. Criar um projeto
3. Ativar 2 APIs (Google Forms + Google Drive)
4. Criar credenciais OAuth 2.0
5. Copiar Client ID e Client Secret
6. Colar aqui no script

O script vai validar e salvar automaticamente no arquivo .env
    """)
    
    input("\nPressione ENTER para ver o guia passo a passo...")
    
    # Passo 2: Guia passo a passo
    print_step(2, "GUIA PASSO A PASSO")
    print("""
📍 URL PRINCIPAL: https://console.cloud.google.com/

📋 PASSO A PASSO:

1. ACESSAR GOOGLE CLOUD
   → Abra: https://console.cloud.google.com/
   → ⚠️  FAÇA LOGIN COM A CONTA GOOGLE DO CLIENTE!
   → (A mesma conta que tem os Google Forms e Google Drive)
   → NÃO use sua conta pessoal de desenvolvedor!

2. CRIAR PROJETO
   → No topo, clique em "Selecionar projeto"
   → Clique em "NOVO PROJETO"
   → Nome: "Integração Imobiliária" (ou qualquer nome)
   → Clique em "CRIAR"
   → Aguarde alguns segundos

3. ATIVAR APIs
   → Menu lateral → "APIs e Serviços" → "Biblioteca"
   → Busque: "Google Forms API" → Clique → "ATIVAR"
   → Busque: "Google Drive API" → Clique → "ATIVAR"

4. CRIAR CREDENCIAIS OAuth 2.0
   → Menu lateral → "APIs e Serviços" → "Credenciais"
   → Clique em "CRIAR CREDENCIAIS"
   → Selecione: "ID do cliente OAuth"
   
   Se aparecer tela de consentimento:
   → Nome do app: "Integração Imobiliária"
   → Email: seu email
   → Clique "SALVAR E CONTINUAR" (vá clicando até finalizar)
   
   Configurar OAuth Client:
   → Tipo: "Aplicativo da Web"
   → Nome: "Integração Imobiliária"
   → URIs de redirecionamento: http://localhost:8080/callback
   → Clique em "CRIAR"

5. COPIAR CREDENCIAIS
   → Você verá uma tela com:
     • ID do cliente: 123456789-abc.apps.googleusercontent.com
     • Chave secreta: GOCSPX-abc123xyz...
   
   ⚠️ COPIE AGORA! A chave secreta não aparece novamente!
    """)
    
    input("\n✅ Quando terminar, pressione ENTER para continuar...")
    
    # Passo 3: Coletar credenciais
    print_step(3, "INSERIR CREDENCIAIS")
    print("\nAgora cole as credenciais que você copiou:\n")
    
    # Coletar Client ID
    while True:
        client_id = input("📋 Cole o CLIENT ID aqui: ").strip()
        valid, message = validate_client_id(client_id)
        if valid:
            print(f"✅ {message}\n")
            break
        else:
            print(f"❌ {message}")
            print("   Exemplo: 123456789-abc.apps.googleusercontent.com\n")
    
    # Coletar Client Secret
    while True:
        client_secret = input("🔐 Cole o CLIENT SECRET aqui: ").strip()
        valid, message = validate_client_secret(client_secret)
        if valid:
            print(f"✅ {message}\n")
            break
        else:
            print(f"❌ {message}")
            print("   Exemplo: GOCSPX-abc123xyz...\n")
    
    # Passo 4: Confirmar
    print_step(4, "CONFIRMAÇÃO")
    print(f"""
Você inseriu:

Client ID: {client_id}
Client Secret: {client_secret[:10]}... (oculto por segurança)

Deseja salvar essas credenciais no arquivo .env?
    """)
    
    confirm = input("Digite 'sim' para confirmar: ").strip().lower()
    
    if confirm not in ['sim', 's', 'yes', 'y']:
        print("\n❌ Operação cancelada.")
        return
    
    # Salvar no .env
    print("\n💾 Salvando credenciais no arquivo .env...")
    try:
        update_env_file(client_id, client_secret)
        print("✅ Credenciais salvas com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}\n")
        return
    
    # Passo 5: Próximos passos
    print_step(5, "PRÓXIMOS PASSOS")
    print("""
✅ Credenciais configuradas!

Agora você precisa:

1. Executar o script de autenticação OAuth:
   → python setup_google_auth.py
   
   Isso vai:
   - Gerar uma URL de autorização
   - Você acessa a URL e autoriza o app
   - O script salva o token de acesso

2. Testar a integração:
   → Execute os testes do sistema
   → Verifique se Google Forms e Drive funcionam

📖 Documentação completa:
   → Veja: COMO_ACESSAR_GOOGLE_CLOUD.md

⚠️  LEMBRE-SE:
   - O arquivo .env contém informações sensíveis
   - Não compartilhe essas credenciais
   - Mantenha o .env no .gitignore (já está configurado)
    """)
    
    print("\n" + "="*60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
