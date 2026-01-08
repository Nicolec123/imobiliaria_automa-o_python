"""
Script simples para testar o envio de mensagem via Waseller
"""
from integrations.wasseller import WassellerIntegration
from config import Config

def testar_wasseller():
    """Testa o envio de mensagem via Waseller"""
    
    print("="*70)
    print("🧪 TESTE DO WASSELLER (WhatsApp)")
    print("="*70)
    
    # Verifica se o token está configurado
    if not Config.WASSELLER_TOKEN:
        print("\n❌ ERRO: WASSELLER_TOKEN não está configurado no .env")
        print("   Configure o token antes de testar.")
        return
    
    print(f"\n✅ Token configurado: {Config.WASSELLER_TOKEN[:20]}...")
    print(f"✅ URL da API: {Config.WASSELLER_API_URL}")
    
    try:
        # Inicializa a integração
        print("\n🔄 Inicializando integração Waseller...")
        wasseller = WassellerIntegration()
        print("✅ Integração inicializada!")
        
        # Solicita dados do teste
        print("\n" + "="*70)
        print("DADOS DO TESTE")
        print("="*70)
        
        telefone = input("\n📱 Digite o número de telefone (ex: 11999999999): ").strip()
        if not telefone:
            print("❌ Telefone não informado. Cancelando teste.")
            return
        
        mensagem = input("💬 Digite a mensagem a ser enviada: ").strip()
        if not mensagem:
            print("❌ Mensagem não informada. Cancelando teste.")
            return
        
        # Confirma envio
        print("\n" + "="*70)
        print("CONFIRMAÇÃO")
        print("="*70)
        print(f"\n📱 Telefone: {telefone}")
        print(f"💬 Mensagem: {mensagem}")
        
        confirmar = input("\n⚠️  Enviar mensagem agora? (s/N): ").strip().lower()
        if confirmar != 's':
            print("\n❌ Teste cancelado pelo usuário.")
            return
        
        # Envia mensagem
        print("\n" + "="*70)
        print("ENVIANDO MENSAGEM...")
        print("="*70)
        
        resultado = wasseller.send_message(telefone, mensagem)
        
        print("\n✅ SUCESSO! Mensagem enviada!")
        print("\n📊 Resposta da API:")
        print(f"   {resultado}")
        
        print("\n" + "="*70)
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("\n💡 Verifique se a mensagem chegou no WhatsApp!")
        
    except ValueError as e:
        print(f"\n❌ ERRO: {str(e)}")
        # A mensagem de erro já vem completa do wasseller.py, não precisa repetir
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        print(f"\nTipo do erro: {type(e).__name__}")

if __name__ == '__main__':
    try:
        testar_wasseller()
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

