"""
Integração com Google Drive
"""
from typing import Dict, List, Optional, BinaryIO
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
from config import Config
import io
import os


class GoogleDriveIntegration:
    """Classe para integração com Google Drive"""
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """
        Inicializa a integração com Google Drive
        
        Args:
            credentials: Credenciais OAuth2 do Google (opcional)
        """
        self.credentials = credentials
        self.service = None
        if credentials:
            self.service = build('drive', 'v3', credentials=credentials)
        self.folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
    
    def upload_file(
        self,
        file_path: Optional[str] = None,
        file_content: Optional[BinaryIO] = None,
        file_name: str = "documento",
        mime_type: str = "application/pdf",
        folder_id: Optional[str] = None
    ) -> Dict:
        """
        Faz upload de um arquivo para o Google Drive
        
        Args:
            file_path: Caminho do arquivo local
            file_content: Conteúdo do arquivo (objeto file-like)
            file_name: Nome do arquivo
            mime_type: Tipo MIME do arquivo
            folder_id: ID da pasta de destino (usa a configurada se não fornecido)
            
        Returns:
            Metadados do arquivo enviado
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Configure as credenciais primeiro.")
        
        folder_id = folder_id or self.folder_id
        
        file_metadata = {
            'name': file_name,
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        try:
            if file_path:
                media = MediaFileUpload(file_path, mimetype=mime_type)
            elif file_content:
                media = MediaIoBaseUpload(file_content, mimetype=mime_type)
            else:
                raise ValueError("Forneça file_path ou file_content")
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            return file
            
        except HttpError as error:
            print(f"Erro ao fazer upload para o Google Drive: {error}")
            raise
    
    def create_document_from_text(
        self,
        content: str,
        title: str,
        folder_id: Optional[str] = None
    ) -> Dict:
        """
        Cria um documento de texto no Google Drive
        
        Args:
            content: Conteúdo do documento
            title: Título do documento
            folder_id: ID da pasta de destino
            
        Returns:
            Metadados do documento criado
        """
        # Cria um arquivo de texto temporário em memória
        file_content = io.BytesIO(content.encode('utf-8'))
        
        return self.upload_file(
            file_content=file_content,
            file_name=title,
            mime_type='text/plain',
            folder_id=folder_id
        )
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Dict:
        """
        Cria uma pasta no Google Drive
        
        Args:
            folder_name: Nome da pasta
            parent_folder_id: ID da pasta pai (opcional)
            
        Returns:
            Metadados da pasta criada
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Configure as credenciais primeiro.")
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            return folder
            
        except HttpError as error:
            print(f"Erro ao criar pasta no Google Drive: {error}")
            raise
    
    def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        """
        Lista arquivos no Google Drive
        
        Args:
            folder_id: ID da pasta (opcional)
            query: Query de busca (opcional)
            
        Returns:
            Lista de arquivos
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Configure as credenciais primeiro.")
        
        folder_id = folder_id or self.folder_id
        
        query_parts = []
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        if query:
            query_parts.append(query)
        
        q = ' and '.join(query_parts) if query_parts else None
        
        try:
            results = self.service.files().list(
                q=q,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, webViewLink, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except HttpError as error:
            print(f"Erro ao listar arquivos do Google Drive: {error}")
            return []
    
    def save_form_response_document(
        self,
        form_data: Dict,
        analysis: Dict,
        response_id: str,
        pdf_path: Optional[str] = None,
        is_property: bool = True
    ) -> Dict:
        """
        Salva um documento com dados do formulário e análise
        
        Args:
            form_data: Dados do formulário
            analysis: Análise do ChatGPT
            response_id: ID da resposta
            pdf_path: Caminho do PDF gerado (se fornecido, faz upload do PDF)
            is_property: Se True, é imóvel; se False, é demanda
            
        Returns:
            Metadados do documento criado
        """
        from datetime import datetime
        
        # Se PDF foi fornecido, faz upload do PDF
        if pdf_path and os.path.exists(pdf_path):
            # Cria pasta específica para o imóvel/demanda se for imóvel
            folder_id = None
            if is_property:
                folder_name = f"Imovel_{response_id}_{datetime.now().strftime('%Y%m%d')}"
                try:
                    folder = self.create_folder(folder_name, parent_folder_id=self.folder_id)
                    folder_id = folder.get('id')
                except Exception as e:
                    print(f"⚠️  Erro ao criar pasta: {e}. Salvando na pasta principal.")
                    folder_id = self.folder_id
            
            # Nome do arquivo
            file_name = f"{'Imovel' if is_property else 'Demanda'}_{response_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Faz upload do PDF
            return self.upload_file(
                file_path=pdf_path,
                file_name=file_name,
                mime_type="application/pdf",
                folder_id=folder_id or self.folder_id
            )
        else:
            # Fallback: salva como texto (compatibilidade)
            import json
            content = f"""
RESPOSTA DE FORMULÁRIO - {response_id}
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== DADOS DO FORMULÁRIO ===
{json.dumps(form_data, indent=2, ensure_ascii=False)}

=== ANÁLISE DO CHATGPT ===
{json.dumps(analysis, indent=2, ensure_ascii=False)}
"""
            
            title = f"Resposta_{response_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            return self.create_document_from_text(content, title)


