"""
Gerenciador de Fila e Retry para Wasseller
Gerencia conflitos quando Wasseller está em uso manual
"""
import time
import requests
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from integrations.message_queue import MessageQueue
from integrations.wasseller import WassellerIntegration


class WassellerQueueManager:
    """Gerencia fila e retry para evitar conflitos com uso manual do Wasseller"""
    
    def __init__(self, wasseller: WassellerIntegration, check_interval: int = 5, max_retries: int = 3):
        """
        Inicializa o gerenciador de fila
        
        Args:
            wasseller: Instância do WassellerIntegration
            check_interval: Intervalo em segundos para verificar disponibilidade
            max_retries: Número máximo de tentativas
        """
        self.wasseller = wasseller
        self.queue = MessageQueue()
        self.check_interval = check_interval
        self.max_retries = max_retries
        self.is_processing = False
    
    def check_availability(self) -> Dict:
        """
        Verifica se o Wasseller está disponível (não está em uso manual)
        
        Returns:
            Dict com status de disponibilidade
        """
        try:
            # Tenta fazer uma requisição simples para verificar se API está disponível
            # Se retornar erro 501, significa que WhatsApp está desconectado
            # Se retornar erro 429, pode estar em uso
            
            # Faz requisição de teste (sem enviar mensagem real)
            # Nota: A API do Wasseller pode não ter endpoint de status
            # Então tentamos e se falhar, assumimos disponível
            try:
                response = requests.get(
                    f"{self.wasseller.api_url}/api/status/{self.wasseller.token}",
                    headers=self.wasseller.headers,
                    timeout=3
                )
                
                if response.status_code == 200:
                    return {
                        'available': True,
                        'message': 'Wasseller disponível'
                    }
                elif response.status_code == 501:
                    return {
                        'available': False,
                        'message': 'WhatsApp desconectado',
                        'reason': 'disconnected'
                    }
                elif response.status_code == 429:
                    return {
                        'available': False,
                        'message': 'Wasseller em uso (rate limit)',
                        'reason': 'in_use'
                    }
                else:
                    # Se não conseguir verificar, assume disponível (tentará enviar)
                    return {
                        'available': True,
                        'message': 'Status desconhecido, tentando enviar',
                        'warning': True
                    }
            except requests.exceptions.RequestException:
                # Se endpoint não existe, assume disponível (tentará enviar)
                return {
                    'available': True,
                    'message': 'Não foi possível verificar status, tentando enviar',
                    'warning': True
                }
        except requests.exceptions.Timeout:
            return {
                'available': False,
                'message': 'Timeout ao verificar disponibilidade',
                'reason': 'timeout'
            }
        except Exception as e:
            # Se não conseguir verificar, assume disponível
            return {
                'available': True,
                'message': f'Erro ao verificar: {str(e)}, tentando enviar',
                'warning': True
            }
    
    def send_with_retry(
        self,
        phone_number: str,
        message: str,
        priority: int = 5,
        use_queue: bool = True,
        max_wait_time: int = 60
    ) -> Dict:
        """
        Envia mensagem com retry e fila
        
        Args:
            phone_number: Número de telefone
            message: Mensagem
            priority: Prioridade (1-10, menor = maior prioridade)
            use_queue: Se True, usa fila se não conseguir enviar
            max_wait_time: Tempo máximo em segundos para aguardar antes de enfileirar
            
        Returns:
            Resultado do envio
        """
        # Verifica disponibilidade
        availability = self.check_availability()
        
        if not availability.get('available', True):
            if use_queue:
                # Adiciona à fila
                message_id = self.queue.add_message(
                    phone_number=phone_number,
                    message=message,
                    priority=priority
                )
                return {
                    'success': False,
                    'queued': True,
                    'message_id': message_id,
                    'message': f"Mensagem enfileirada. Wasseller: {availability.get('message')}",
                    'availability': availability
                }
            else:
                return {
                    'success': False,
                    'queued': False,
                    'message': f"Não foi possível enviar. Wasseller: {availability.get('message')}",
                    'availability': availability
                }
        
        # Tenta enviar
        attempts = 0
        last_error = None
        
        while attempts < self.max_retries:
            try:
                result = self.wasseller.send_message(phone_number, message)
                
                if result.get('success', False):
                    return {
                        'success': True,
                        'queued': False,
                        'result': result,
                        'attempts': attempts + 1
                    }
                else:
                    last_error = result.get('message', 'Erro desconhecido')
                    attempts += 1
                    
                    # Se erro indica que está em uso, aguarda
                    if 'em uso' in last_error.lower() or 'ocupado' in last_error.lower():
                        if attempts < self.max_retries:
                            time.sleep(self.check_interval)
                            continue
                    
            except ValueError as e:
                error_msg = str(e)
                last_error = error_msg
                
                # Se erro 501 (desconectado), não adiciona à fila
                if 'desconectado' in error_msg.lower() or '501' in error_msg:
                    return {
                        'success': False,
                        'queued': False,
                        'error': error_msg,
                        'message': 'WhatsApp desconectado. Verifique o painel Wasseller.'
                    }
                
                # Se erro indica uso, aguarda e tenta novamente
                if 'em uso' in error_msg.lower() or 'ocupado' in error_msg.lower():
                    attempts += 1
                    if attempts < self.max_retries:
                        time.sleep(self.check_interval)
                        continue
                
                attempts += 1
                
            except Exception as e:
                last_error = str(e)
                attempts += 1
                if attempts < self.max_retries:
                    time.sleep(self.check_interval)
        
        # Se falhou todas as tentativas, adiciona à fila
        if use_queue:
            message_id = self.queue.add_message(
                phone_number=phone_number,
                message=message,
                priority=priority,
                metadata={'last_error': last_error}
            )
            return {
                'success': False,
                'queued': True,
                'message_id': message_id,
                'error': last_error,
                'message': f'Mensagem enfileirada após {attempts} tentativas falhadas'
            }
        else:
            return {
                'success': False,
                'queued': False,
                'error': last_error,
                'message': f'Falha após {attempts} tentativas'
            }
    
    def process_queue(self, max_messages: int = 10) -> Dict:
        """
        Processa mensagens da fila
        
        Args:
            max_messages: Número máximo de mensagens para processar por vez
            
        Returns:
            Resultado do processamento
        """
        if self.is_processing:
            return {
                'success': False,
                'message': 'Já está processando fila'
            }
        
        self.is_processing = True
        results = {
            'processed': 0,
            'sent': 0,
            'failed': 0,
            'still_pending': 0
        }
        
        try:
            for _ in range(max_messages):
                message = self.queue.get_next_message(max_attempts=self.max_retries)
                
                if not message:
                    break
                
                results['processed'] += 1
                
                # Verifica disponibilidade antes de tentar
                availability = self.check_availability()
                
                if not availability.get('available', True):
                    results['still_pending'] += 1
                    continue
                
                # Tenta enviar
                try:
                    result = self.wasseller.send_message(
                        message['phone_number'],
                        message['message']
                    )
                    
                    if result.get('success', False):
                        self.queue.mark_sent(message['id'])
                        results['sent'] += 1
                    else:
                        self.queue.mark_failed(
                            message['id'],
                            result.get('message', 'Erro desconhecido')
                        )
                        results['failed'] += 1
                        
                except Exception as e:
                    self.queue.mark_failed(message['id'], str(e))
                    results['failed'] += 1
                
                # Aguarda um pouco entre mensagens
                time.sleep(1)
        
        finally:
            self.is_processing = False
        
        return results
    
    def schedule_message(
        self,
        phone_number: str,
        message: str,
        scheduled_time: datetime,
        priority: int = 5
    ) -> int:
        """
        Agenda mensagem para envio futuro
        
        Args:
            phone_number: Número de telefone
            message: Mensagem
            scheduled_time: Data/hora agendada
            priority: Prioridade
            
        Returns:
            ID da mensagem na fila
        """
        return self.queue.add_message(
            phone_number=phone_number,
            message=message,
            priority=priority,
            scheduled_for=scheduled_time
        )
    
    def get_queue_status(self) -> Dict:
        """Retorna status da fila"""
        stats = self.queue.get_queue_stats()
        return {
            'queue_stats': stats,
            'is_processing': self.is_processing,
            'availability': self.check_availability()
        }

