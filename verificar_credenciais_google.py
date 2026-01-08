"""
Script para verificar se as credenciais do Google Cloud estão corretas
"""
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*60)
print("🔍 VERIFICAÇÃO DE CREDENCIAIS GOOGLE CLOUD")
print("="*60 + "\n")

client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print("📋 Credenciais no arquivo .env:")
print(f"   Client ID: {client_id if client_id else '❌ NÃO ENCONTRADO'}")
print(f"   Client Secret: {client_secret[:20] + '...' if client_secret else '❌ NÃO ENCONTRADO'}")
print()

# Verificar formato
if client_id:
    if client_id.endswith('.apps.googleusercontent.com'):
        print("✅ Formato do Client ID está correto")
    else:
        print("❌ Formato do Client ID está incorreto")
        print("   Deve terminar com: .apps.googleusercontent.com")
else:
    print("❌ Client ID não encontrado no .env")

if client_secret:
    if client_secret.startswith('GOCSPX-'):
        print("✅ Formato do Client Secret está correto")
    else:
        print("❌ Formato do Client Secret está incorreto")
        print("   Deve começar com: GOCSPX-")
else:
    print("❌ Client Secret não encontrado no .env")

print("\n" + "="*60)
print("🔍 PRÓXIMOS PASSOS PARA RESOLVER O ERRO:")
print("="*60)
print("""
1. Acesse: https://console.cloud.google.com/apis/credentials
2. Faça login com: diretoria@pebimob.com.br
3. Verifique:
   - O projeto correto está selecionado?
   - O Client ID existe na lista?
   - O Client ID deve estar configurado no .env
   
4. Se NÃO encontrar o Client ID:
   - As credenciais podem estar em outro projeto
   - Ou foram deletadas
   - Você precisa recriar as credenciais

5. Se encontrar o Client ID:
   - Clique nele para editar
   - Verifique se tem a URI: http://localhost:8080/callback
   - Se não tiver, adicione e salve
""")

print("\n" + "="*60)
print("✅ Verificação concluída!")
print("="*60 + "\n")
