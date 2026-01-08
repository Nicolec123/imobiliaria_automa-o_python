"""
Script para testar descoberta automática de grupos no Waseller
"""
from integrations.wasseller import WassellerIntegration
from config import Config

def testar_descobrir_grupos():
    """Testa a descoberta automática de grupos"""
    
    print("="*70)
    print("🔍 TESTE: DESCOBERTA AUTOMÁTICA DE GRUPOS")
    print("="*70)
    
    if not Config.WASSELLER_TOKEN:
        print("\n❌ ERRO: WASSELLER_TOKEN não está configurado no .env")
        return
    
    try:
        wasseller = WassellerIntegration()
        print(f"\n✅ Integração inicializada!")
        print(f"✅ Token: {Config.WASSELLER_TOKEN[:20]}...")
        print(f"✅ URL: {Config.WASSELLER_API_URL}")
        
        print("\n" + "="*70)
        print("TENTANDO DESCOBRIR GRUPOS AUTOMATICAMENTE...")
        print("="*70)
        
        grupos = wasseller.list_groups()
        
        if grupos:
            print(f"\n✅ {len(grupos)} grupos encontrados!")
            print("\n📋 Lista de grupos:")
            for i, grupo in enumerate(grupos, 1):
                grupo_id = grupo.get('id') or grupo.get('groupId') or grupo.get('jid', 'N/A')
                grupo_nome = grupo.get('nome') or grupo.get('name') or grupo.get('subject', 'Sem nome')
                print(f"   {i}. {grupo_nome} (ID: {grupo_id})")
        else:
            print("\n⚠️  Nenhum grupo encontrado automaticamente")
            print("\n💡 Possíveis motivos:")
            print("   - A API do Waseller pode não ter endpoint para listar grupos")
            print("   - O endpoint pode ter formato diferente")
            print("   - Você pode precisar configurar grupos manualmente no wasseller_config.json")
        
        print("\n" + "="*70)
        print("TESTE DE ENVIO PARA GRUPOS DESCOBERTOS")
        print("="*70)
        
        if grupos:
            confirmar = input("\n⚠️  Enviar mensagem de teste para os grupos descobertos? (s/N): ").strip().lower()
            if confirmar == 's':
                mensagem_teste = "🧪 Mensagem de teste - Sistema de automação"
                resultado = wasseller.send_to_groups(mensagem_teste, auto_discover=True)
                
                print("\n📊 Resultado:")
                print(f"   ✅ Enviados: {len(resultado.get('enviados', []))}")
                print(f"   ❌ Falhas: {len(resultado.get('falhas', []))}")
                print(f"   🚫 Bloqueados: {len(resultado.get('bloqueados', []))}")
                
                if resultado.get('enviados'):
                    print("\n✅ Grupos que receberam mensagem:")
                    for envio in resultado['enviados']:
                        print(f"   - {envio.get('grupo', 'N/A')}")
                
                if resultado.get('falhas'):
                    print("\n❌ Grupos com falha:")
                    for falha in resultado['falhas']:
                        print(f"   - {falha.get('grupo', 'N/A')}: {falha.get('erro', 'Erro desconhecido')}")
        else:
            print("\n⚠️  Não é possível testar envio sem grupos descobertos")
            print("   Configure grupos manualmente no wasseller_config.json ou verifique a API")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print(f"\nTipo: {type(e).__name__}")

if __name__ == '__main__':
    try:
        testar_descobrir_grupos()
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

