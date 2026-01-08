"""
Script para processar fila de mensagens do Wasseller
Pode ser executado manualmente ou agendado
"""
import time
from orchestrator import IntegrationOrchestrator


def processar_fila():
    """Processa mensagens pendentes na fila do Wasseller"""
    print("="*70)
    print("  PROCESSADOR DE FILA - WASSELLER")
    print("="*70)
    
    try:
        orchestrator = IntegrationOrchestrator()
        
        if not orchestrator.wasseller_queue:
            print("❌ Queue manager não disponível")
            return
        
        # Obtém status da fila
        status = orchestrator.wasseller_queue.get_queue_status()
        stats = status['queue_stats']
        
        print(f"\n📊 Status da Fila:")
        print(f"   - Pendentes: {stats['pending']}")
        print(f"   - Enviadas: {stats['sent']}")
        print(f"   - Falhas: {stats['failed']}")
        print(f"   - Total: {stats['total']}")
        
        if stats['pending'] == 0:
            print("\n✅ Nenhuma mensagem pendente na fila!")
            return
        
        print(f"\n🔄 Processando {stats['pending']} mensagens...")
        
        # Processa fila
        result = orchestrator.wasseller_queue.process_queue(max_messages=50)
        
        print(f"\n✅ Processamento concluído:")
        print(f"   - Processadas: {result['processed']}")
        print(f"   - Enviadas: {result['sent']}")
        print(f"   - Falhas: {result['failed']}")
        print(f"   - Ainda pendentes: {result['still_pending']}")
        
    except Exception as e:
        print(f"\n❌ Erro ao processar fila: {e}")


if __name__ == '__main__':
    processar_fila()

