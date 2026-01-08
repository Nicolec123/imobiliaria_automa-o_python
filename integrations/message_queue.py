"""
Sistema de Fila de Mensagens para Wasseller
Gerencia fila quando o Wasseller está em uso
"""
import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime
from threading import Lock
import sqlite3


class MessageQueue:
    """Gerenciador de fila de mensagens para evitar conflitos com uso manual do Wasseller"""
    
    def __init__(self, queue_file: str = "wasseller_queue.json", db_file: str = "wasseller_queue.db"):
        """
        Inicializa o gerenciador de fila
        
        Args:
            queue_file: Arquivo JSON para backup da fila
            db_file: Arquivo SQLite para persistência
        """
        self.queue_file = queue_file
        self.db_file = db_file
        self.lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados SQLite para fila"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    attempts INTEGER DEFAULT 0,
                    last_attempt TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    scheduled_for TIMESTAMP,
                    metadata TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao inicializar banco de dados da fila: {e}")
    
    def add_message(
        self,
        phone_number: str,
        message: str,
        priority: int = 5,
        scheduled_for: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Adiciona mensagem à fila
        
        Args:
            phone_number: Número de telefone
            message: Mensagem a ser enviada
            priority: Prioridade (1-10, menor = maior prioridade)
            scheduled_for: Data/hora agendada (None = enviar imediatamente)
            metadata: Metadados adicionais
            
        Returns:
            ID da mensagem na fila
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                scheduled_str = scheduled_for.isoformat() if scheduled_for else None
                metadata_str = json.dumps(metadata) if metadata else None
                
                cursor.execute('''
                    INSERT INTO message_queue 
                    (phone_number, message, priority, scheduled_for, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (phone_number, message, priority, scheduled_str, metadata_str))
                
                message_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Backup em JSON
                self._save_json_backup()
                
                return message_id
            except Exception as e:
                print(f"❌ Erro ao adicionar mensagem à fila: {e}")
                raise
    
    def get_next_message(self, max_attempts: int = 3) -> Optional[Dict]:
        """
        Obtém próxima mensagem da fila (maior prioridade, mais antiga)
        
        Args:
            max_attempts: Número máximo de tentativas antes de marcar como falha
            
        Returns:
            Dicionário com dados da mensagem ou None se fila vazia
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                # Busca mensagem pendente, não agendada para futuro, com menos tentativas
                cursor.execute('''
                    SELECT id, phone_number, message, priority, attempts, scheduled_for, metadata
                    FROM message_queue
                    WHERE status = 'pending'
                    AND (scheduled_for IS NULL OR scheduled_for <= datetime('now'))
                    AND attempts < ?
                    ORDER BY priority ASC, created_at ASC
                    LIMIT 1
                ''', (max_attempts,))
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        'id': row[0],
                        'phone_number': row[1],
                        'message': row[2],
                        'priority': row[3],
                        'attempts': row[4],
                        'scheduled_for': row[5],
                        'metadata': json.loads(row[6]) if row[6] else None
                    }
                return None
            except Exception as e:
                print(f"❌ Erro ao obter próxima mensagem: {e}")
                return None
    
    def mark_sent(self, message_id: int):
        """Marca mensagem como enviada"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE message_queue
                    SET status = 'sent', last_attempt = datetime('now')
                    WHERE id = ?
                ''', (message_id,))
                conn.commit()
                conn.close()
                self._save_json_backup()
            except Exception as e:
                print(f"❌ Erro ao marcar mensagem como enviada: {e}")
    
    def mark_failed(self, message_id: int, error_message: str):
        """Marca mensagem como falha e incrementa tentativas"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE message_queue
                    SET attempts = attempts + 1,
                        last_attempt = datetime('now'),
                        error_message = ?,
                        status = CASE 
                            WHEN attempts + 1 >= 3 THEN 'failed'
                            ELSE 'pending'
                        END
                    WHERE id = ?
                ''', (error_message, message_id))
                conn.commit()
                conn.close()
                self._save_json_backup()
            except Exception as e:
                print(f"❌ Erro ao marcar mensagem como falha: {e}")
    
    def get_queue_stats(self) -> Dict:
        """Retorna estatísticas da fila"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM message_queue
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total': row[0] or 0,
                'pending': row[1] or 0,
                'sent': row[2] or 0,
                'failed': row[3] or 0
            }
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {'total': 0, 'pending': 0, 'sent': 0, 'failed': 0}
    
    def clear_sent_messages(self, days_old: int = 7):
        """Remove mensagens enviadas mais antigas que X dias"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM message_queue
                WHERE status = 'sent'
                AND last_attempt < datetime('now', '-' || ? || ' days')
            ''', (days_old,))
            conn.commit()
            conn.close()
            self._save_json_backup()
        except Exception as e:
            print(f"❌ Erro ao limpar mensagens antigas: {e}")
    
    def _save_json_backup(self):
        """Salva backup da fila em JSON"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, phone_number, message, priority, status, attempts, created_at
                FROM message_queue
                WHERE status IN ('pending', 'failed')
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            queue_data = [
                {
                    'id': row[0],
                    'phone_number': row[1],
                    'message': row[2],
                    'priority': row[3],
                    'status': row[4],
                    'attempts': row[5],
                    'created_at': row[6]
                }
                for row in rows
            ]
            
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao salvar backup JSON: {e}")

