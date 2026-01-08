"""
Sistema de Fallback por Email quando Wasseller está indisponível
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
from config import Config
import os


class EmailFallback:
    """Envia notificações por email quando Wasseller está indisponível"""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        email_from: Optional[str] = None,
        email_password: Optional[str] = None,
        email_to: Optional[List[str]] = None
    ):
        """
        Inicializa o sistema de fallback por email
        
        Args:
            smtp_server: Servidor SMTP (ex: smtp.gmail.com)
            smtp_port: Porta SMTP (ex: 587)
            email_from: Email remetente
            email_password: Senha do email
            email_to: Lista de emails destinatários
        """
        self.smtp_server = smtp_server or Config.EMAIL_SMTP_SERVER or "smtp.gmail.com"
        self.smtp_port = smtp_port or Config.EMAIL_SMTP_PORT or 587
        self.email_from = email_from or Config.EMAIL_FROM
        self.email_password = email_password or Config.EMAIL_PASSWORD
        self.email_to = email_to or (Config.EMAIL_TO.split(',') if hasattr(Config, 'EMAIL_TO') and Config.EMAIL_TO else [])
        
        if not self.email_from:
            self.email_from = os.getenv('EMAIL_FROM', '')
        if not self.email_password:
            self.email_password = os.getenv('EMAIL_PASSWORD', '')
        if not self.email_to:
            email_to_env = os.getenv('EMAIL_TO', '')
            self.email_to = [e.strip() for e in email_to_env.split(',') if e.strip()]
    
    def send_notification(
        self,
        subject: str,
        message: str,
        recipients: Optional[List[str]] = None,
        is_html: bool = False
    ) -> Dict:
        """
        Envia notificação por email
        
        Args:
            subject: Assunto do email
            message: Mensagem (texto ou HTML)
            recipients: Lista de destinatários (usa configurado se None)
            is_html: Se True, mensagem é HTML
            
        Returns:
            Resultado do envio
        """
        if not self.email_from or not self.email_password:
            return {
                'success': False,
                'error': 'Email não configurado. Configure EMAIL_FROM e EMAIL_PASSWORD no .env'
            }
        
        recipients = recipients or self.email_to
        if not recipients:
            return {
                'success': False,
                'error': 'Nenhum destinatário configurado'
            }
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return {
                'success': True,
                'message': f'Email enviado para {len(recipients)} destinatário(s)',
                'recipients': recipients
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_whatsapp_fallback(
        self,
        phone_number: str,
        message: str,
        reason: str = "Wasseller indisponível"
    ) -> Dict:
        """
        Envia notificação de fallback quando WhatsApp não está disponível
        
        Args:
            phone_number: Número que deveria receber WhatsApp
            message: Mensagem que deveria ser enviada
            reason: Motivo do fallback
            
        Returns:
            Resultado do envio
        """
        subject = f"⚠️ WhatsApp Indisponível - Mensagem para {phone_number}"
        
        email_message = f"""
Mensagem WhatsApp não pôde ser enviada

Motivo: {reason}

Destinatário: {phone_number}
Mensagem que deveria ser enviada:

{message}

---
Esta é uma notificação automática do sistema de integração.
A mensagem foi enfileirada e será enviada quando o Wasseller estiver disponível.
"""
        
        return self.send_notification(subject, email_message)

