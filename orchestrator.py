"""
Sistema de orquestração principal para integração de ferramentas imobiliárias
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from integrations.google_forms import GoogleFormsIntegration
from integrations.chatgpt import ChatGPTIntegration
from integrations.clickup import ClickUpIntegration
from integrations.google_drive import GoogleDriveIntegration
from integrations.chaves_na_mao import ChavesNaMaoIntegration
from integrations.wasseller import WassellerIntegration
from integrations.wasseller_queue_manager import WassellerQueueManager
from integrations.email_fallback import EmailFallback
from config import Config


class IntegrationOrchestrator:
    """Orquestrador principal que coordena todas as integrações"""
    
    def __init__(self):
        """Inicializa o orquestrador com todas as integrações"""
        # Inicializa integrações uma a uma, sem derrubar tudo se alguma falhar
        # Isso evita que problemas na OpenAI/ChatGPT impeçam o resto do fluxo
        
        # ChatGPT
        try:
            self.chatgpt = ChatGPTIntegration()
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao inicializar ChatGPTIntegration: {e}")
            self.chatgpt = None
        
        # ClickUp (obrigatório para criação de tarefas)
        try:
            self.clickup = ClickUpIntegration()
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao inicializar ClickUpIntegration: {e}")
            self.clickup = None
        
        # Chaves na Mão - tenta inicializar, mas não é obrigatório (usa XML)
        try:
            self.chaves_na_mao = ChavesNaMaoIntegration()
        except Exception:
            self.chaves_na_mao = None  # Não precisa de API Key, usa XML
        
        # Wasseller (WhatsApp) - importante para notificações
        try:
            self.wasseller = WassellerIntegration()
            # Inicializa gerenciador de fila para evitar conflitos com uso manual
            self.wasseller_queue = WassellerQueueManager(self.wasseller)
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao inicializar WassellerIntegration: {e}")
            self.wasseller = None
            self.wasseller_queue = None
        
        # Sistema de fallback por email
        try:
            self.email_fallback = EmailFallback()
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao inicializar EmailFallback: {e}")
            self.email_fallback = None
        
        # Google Forms e Drive precisam de credenciais OAuth2
        # Tenta carregar automaticamente se arquivo existir
        self.google_forms = None
        self.google_drive = None
        
        # Tenta carregar credenciais automaticamente
        try:
            if os.path.exists('google_credentials.json'):
                from google.oauth2.credentials import Credentials
                creds = Credentials.from_authorized_user_file('google_credentials.json')
                self.set_google_credentials(creds)
                print("✅ Credenciais Google carregadas automaticamente")
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível carregar credenciais Google automaticamente: {e}")
    
    def set_google_credentials(self, credentials):
        """
        Define as credenciais do Google para Forms e Drive
        
        Args:
            credentials: Credenciais OAuth2 do Google
        """
        self.google_forms = GoogleFormsIntegration(credentials)
        self.google_drive = GoogleDriveIntegration(credentials)
    
    def process_form_response(
        self,
        form_response: Dict,
        send_whatsapp: bool = True,
        create_lead: bool = True,
        save_to_drive: bool = True,
        create_task: bool = True
    ) -> Dict:
        """
        Processa uma resposta de formulário completa
        
        Args:
            form_response: Dados da resposta do formulário
            send_whatsapp: Se deve enviar mensagem WhatsApp
            create_lead: Se deve criar lead no Chaves na Mão
            save_to_drive: Se deve salvar no Google Drive
            create_task: Se deve criar tarefa no ClickUp
            
        Returns:
            Resultado do processamento completo
        """
        result = {
            'response_id': form_response.get('response_id'),
            'timestamp': datetime.now().isoformat(),
            'steps': {},
            'success': True,
            'errors': []
        }
        
        try:
            # Passo 1: Analisar com ChatGPT (ou usar dados simulados se não disponível)
            if self.chatgpt:
                print(f"Analisando resposta {result['response_id']} com ChatGPT...")
                analysis = self.chatgpt.analyze_form_data(form_response)
                task_description = self.chatgpt.generate_task_description(analysis)
                result['steps']['chatgpt_analysis'] = {
                    'success': True,
                    'analysis': analysis
                }
            else:
                print(f"⚠️  ChatGPT não disponível, usando análise simulada...")
                # Cria análise simulada baseada nos dados do formulário
                answers = form_response.get('answers', {})
                analysis = {
                    'tipo_lead': answers.get('tipo_imovel', 'Lead Qualificado'),
                    'prioridade': 'alta' if answers.get('orcamento') else 'média',
                    'categoria': answers.get('tipo_imovel', 'Imóvel'),
                    'resumo': f"Novo lead recebido: {answers.get('nome', 'Cliente')}",
                    'informacoes_extraidas': {
                        'nome': answers.get('nome', 'Não informado'),
                        'telefone': answers.get('telefone', ''),
                        'email': answers.get('email', 'Não informado'),
                        'tipo_imovel': answers.get('tipo_imovel', 'Não especificado'),
                        'localizacao': answers.get('localizacao', 'Não especificada'),
                        'orcamento': answers.get('orcamento', 'Não informado'),
                        'observacoes': answers.get('observacoes', 'Nenhuma observação')
                    },
                    'acoes_sugeridas': [
                        'Entrar em contato com o cliente',
                        'Verificar disponibilidade de imóveis',
                        'Agendar visita'
                    ]
                }
                task_description = f"""
Novo Lead Recebido

Nome: {analysis['informacoes_extraidas']['nome']}
Telefone: {analysis['informacoes_extraidas']['telefone']}
Email: {analysis['informacoes_extraidas']['email']}
Tipo de Imóvel: {analysis['informacoes_extraidas']['tipo_imovel']}
Localização: {analysis['informacoes_extraidas']['localizacao']}
Orçamento: {analysis['informacoes_extraidas']['orcamento']}

Observações: {analysis['informacoes_extraidas']['observacoes']}
"""
                result['steps']['chatgpt_analysis'] = {
                    'success': True,
                    'analysis': analysis,
                    'note': 'Análise simulada (ChatGPT não disponível)'
                }
            
            # Passo 2: Criar tarefa no ClickUp
            if create_task:
                try:
                    print(f"Criando tarefa no ClickUp...")
                    task = self.clickup.create_task_from_analysis(
                        analysis=analysis,
                        task_description=task_description,
                        response_id=result['response_id']
                    )
                    result['steps']['clickup_task'] = {
                        'success': True,
                        'task_id': task.get('id'),
                        'task_url': task.get('url')
                    }
                except Exception as e:
                    result['steps']['clickup_task'] = {
                        'success': False,
                        'error': str(e)
                    }
                    result['errors'].append(f"ClickUp: {str(e)}")
            
            # Passo 3: Gerar XML do Chaves na Mão
            if create_lead:
                try:
                    print(f"Gerando XML do Chaves na Mão...")
                    from integrations.chaves_na_mao_xml_generator import ChavesNaMaoXMLGenerator
                    import os
                    
                    generator = ChavesNaMaoXMLGenerator()
                    xml_content = generator.generate_xml_from_form_data(form_response, analysis)
                    
                    # Salva XML individual
                    os.makedirs('imoveis', exist_ok=True)
                    xml_file = f"imoveis/{result['response_id']}.xml"
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(xml_content)
                    
                    # Prepara dados do imóvel para o feed
                    info = analysis.get('informacoes_extraidas', {})
                    answers = form_response.get('answers', {})
                    
                    property_data = {
                        'codigo': result['response_id'],
                        'referencia': result['response_id'],
                        'titulo': answers.get('titulo', info.get('tipo_imovel', 'Imóvel')),
                        'tipo': answers.get('tipo', info.get('tipo_imovel', 'Apartamento')),
                        'transacao': answers.get('transacao', 'V'),
                        'finalidade': answers.get('finalidade', 'RE'),
                        'valor': answers.get('valor', info.get('orcamento', '0')),
                        'cidade': answers.get('cidade', info.get('localizacao', '').split('-')[0].strip() if info.get('localizacao') else ''),
                        'bairro': answers.get('bairro', ''),
                        'estado': answers.get('estado', ''),
                        'endereco': answers.get('endereco', ''),
                        'quartos': answers.get('quartos', ''),
                        'banheiro': answers.get('banheiro', ''),
                        'garagem': answers.get('garagem', ''),
                        'area_total': answers.get('area_total', ''),
                        'descritivo': answers.get('observacoes', info.get('observacoes', '')),
                        'fotos': answers.get('fotos', []) if isinstance(answers.get('fotos'), list) else [],
                    }
                    
                    # Atualiza feed principal
                    feed_file = 'chaves_na_mao_feed.xml'
                    existing_properties = []
                    
                    # Carrega feed existente
                    if os.path.exists(feed_file):
                        try:
                            tree = ET.parse(feed_file)
                            root = tree.getroot()
                            for imovel_elem in root.findall('.//imovel'):
                                prop_data = {}
                                for child in imovel_elem:
                                    if child.text:
                                        prop_data[child.tag] = child.text
                                if prop_data:
                                    existing_properties.append(prop_data)
                        except:
                            existing_properties = []
                    
                    # Adiciona novo imóvel (evita duplicatas)
                    if not any(p.get('codigo', p.get('referencia')) == property_data['codigo'] for p in existing_properties):
                        existing_properties.append(property_data)
                    
                    # Gera novo feed
                    feed_xml = generator.generate_feed_xml(existing_properties)
                    with open(feed_file, 'w', encoding='utf-8') as f:
                        f.write(feed_xml)
                    
                    result['steps']['chaves_na_mao_xml'] = {
                        'success': True,
                        'xml_file': xml_file,
                        'feed_url': '/api/chaves-na-mao/feed.xml',
                        'message': 'XML gerado com sucesso. Feed disponível em /api/chaves-na-mao/feed.xml'
                    }
                except Exception as e:
                    result['steps']['chaves_na_mao_xml'] = {
                        'success': False,
                        'error': str(e)
                    }
                    result['errors'].append(f"Chaves na Mão XML: {str(e)}")
            
            # Passo 4: Gerar PDF e Salvar no Google Drive
            pdf_path = None
            is_property = True  # Detecta se é imóvel ou demanda
            
            # Gera PDF sempre que save_to_drive=True (independente do Drive estar configurado)
            if save_to_drive:
                try:
                    # Detecta se é imóvel ou demanda baseado nos dados
                    answers = form_response.get('answers', {})
                    tipo_form = form_response.get('form_title', '').lower()
                    
                    # Se tem campos específicos de imóvel (valor, quartos, etc) ou título indica imóvel
                    if 'imovel' in tipo_form or 'imóvel' in tipo_form or answers.get('valor') or answers.get('quartos'):
                        is_property = True
                    else:
                        is_property = False
                    
                    # Gera PDF
                    print(f"Gerando PDF...")
                    from integrations.pdf_generator import PDFGenerator
                    pdf_generator = PDFGenerator()
                    
                    if is_property:
                        pdf_path = pdf_generator.generate_property_pdf(
                            form_data=form_response,
                            analysis=analysis,
                            response_id=result['response_id']
                        )
                    else:
                        pdf_path = pdf_generator.generate_demand_pdf(
                            form_data=form_response,
                            analysis=analysis,
                            response_id=result['response_id']
                        )
                    
                    print(f"PDF gerado: {pdf_path}")
                    result['steps']['pdf_generation'] = {
                        'success': True,
                        'pdf_path': pdf_path
                    }
                    
                    # Tenta salvar PDF no Google Drive (se configurado)
                    if self.google_drive:
                        try:
                            print(f"Salvando PDF no Google Drive...")
                            document = self.google_drive.save_form_response_document(
                                form_data=form_response,
                                analysis=analysis,
                                response_id=result['response_id'],
                                pdf_path=pdf_path,
                                is_property=is_property
                            )
                            result['steps']['google_drive'] = {
                                'success': True,
                                'document_id': document.get('id'),
                                'document_url': document.get('webViewLink'),
                                'pdf_path': pdf_path,
                                'folder_created': is_property  # Indica se pasta foi criada
                            }
                        except Exception as e:
                            result['steps']['google_drive'] = {
                                'success': False,
                                'error': str(e),
                                'note': 'PDF gerado localmente, mas upload para Drive falhou'
                            }
                            result['errors'].append(f"Google Drive: {str(e)}")
                    else:
                        result['steps']['google_drive'] = {
                            'success': False,
                            'note': 'PDF gerado localmente, mas Google Drive não está configurado',
                            'pdf_path': pdf_path
                        }
                    
                    # Limpa PDF local após upload (opcional)
                    # os.remove(pdf_path)  # Descomente se quiser remover após upload
                    
                except Exception as e:
                    result['steps']['pdf_generation'] = {
                        'success': False,
                        'error': str(e)
                    }
                    result['errors'].append(f"Geração de PDF: {str(e)}")
                    
                    # Se PDF falhar e Drive estiver configurado, tenta salvar como texto (fallback)
                    if self.google_drive:
                        try:
                            print(f"⚠️  Tentando salvar como texto (fallback)...")
                            document = self.google_drive.save_form_response_document(
                                form_data=form_response,
                                analysis=analysis,
                                response_id=result['response_id']
                            )
                            result['steps']['google_drive'] = {
                                'success': True,
                                'document_id': document.get('id'),
                                'document_url': document.get('webViewLink'),
                                'note': 'Salvo como texto (PDF falhou)'
                            }
                        except Exception as e2:
                            result['errors'].append(f"Google Drive (fallback): {str(e2)}")
            
            # Passo 5: Enviar mensagem WhatsApp (com fila e retry)
            if send_whatsapp:
                try:
                    info = analysis.get('informacoes_extraidas', {})
                    telefone = info.get('telefone')
                    
                    if telefone:
                        print(f"Enviando mensagem WhatsApp...")
                        
                        # Prepara mensagem de boas-vindas
                        nome = info.get('nome', 'Cliente')
                        welcome_message = f"""
Olá {nome}! 👋

Obrigado por entrar em contato conosco!

Recebemos sua solicitação e nossa equipe já está analisando suas necessidades.

Em breve entraremos em contato para dar continuidade ao seu atendimento.

Atenciosamente,
Equipe Imobiliária
""".strip()
                        
                        # Usa queue manager se disponível (com retry e fila)
                        if self.wasseller_queue:
                            whatsapp_result = self.wasseller_queue.send_with_retry(
                                phone_number=telefone,
                                message=welcome_message,
                                priority=3,  # Prioridade alta para mensagens de boas-vindas
                                use_queue=True
                            )
                            
                            if whatsapp_result.get('queued', False):
                                # Se foi enfileirado, envia notificação por email
                                if self.email_fallback:
                                    email_result = self.email_fallback.send_whatsapp_fallback(
                                        phone_number=telefone,
                                        message=welcome_message,
                                        reason=whatsapp_result.get('message', 'Wasseller em uso')
                                    )
                                    result['steps']['whatsapp_fallback_email'] = email_result
                            
                            result['steps']['whatsapp'] = whatsapp_result
                        else:
                            # Fallback: usa método direto (sem fila)
                            whatsapp_result = self.wasseller.send_welcome_message(
                                analysis=analysis,
                                form_data=form_response
                            )
                            result['steps']['whatsapp'] = {
                                'success': True,
                                'message_id': whatsapp_result.get('id'),
                                'note': 'Enviado sem fila (queue manager não disponível)'
                            }
                    else:
                        result['steps']['whatsapp'] = {
                            'success': False,
                            'error': 'Telefone não encontrado'
                        }
                except Exception as e:
                    result['steps']['whatsapp'] = {
                        'success': False,
                        'error': str(e)
                    }
                    result['errors'].append(f"WhatsApp: {str(e)}")
                    
                    # Tenta fallback por email se WhatsApp falhar completamente
                    if self.email_fallback and telefone:
                        try:
                            email_result = self.email_fallback.send_whatsapp_fallback(
                                phone_number=telefone,
                                message=welcome_message if 'welcome_message' in locals() else "Mensagem de boas-vindas",
                                reason=f"Erro ao enviar: {str(e)}"
                            )
                            result['steps']['whatsapp_fallback_email'] = email_result
                        except:
                            pass
            
            # Passo 6: Enviar notificações para grupos e equipe (com fila e retry)
            try:
                print(f"Enviando notificações para grupos e equipe...")
                # Pega telefone do cliente para excluir se necessário (do analysis)
                info_analysis = analysis.get('informacoes_extraidas', {})
                cliente_telefone = info_analysis.get('telefone', '')
                
                # Monta mensagem de notificação
                template = self.wasseller.config.get('mensagens', {}).get('template_novo_lead', 
                    "🔔 NOVO LEAD RECEBIDO\n\nID: {response_id}\nNome: {nome}\nTelefone: {telefone}\nTipo: {tipo_lead}\nPrioridade: {prioridade}\n\nAção: Verificar no ClickUp")
                
                notification_message = template.format(
                    response_id=result['response_id'],
                    nome=info_analysis.get('nome', 'Não informado'),
                    telefone=info_analysis.get('telefone', 'Não informado'),
                    tipo_lead=analysis.get('tipo_lead', 'Lead'),
                    prioridade=analysis.get('prioridade', 'Média')
                )
                
                # Se tem queue manager, usa para enviar notificações com retry
                if self.wasseller_queue:
                    # Envia para grupos (com fila)
                    grupos_result = self.wasseller.send_to_groups(
                        message=notification_message,
                        auto_discover=True
                    )
                    
                    # Envia para equipe (com fila)
                    equipe_result = self.wasseller.send_to_team(
                        message=notification_message,
                        exclude_owner=True,
                        owner_phone=cliente_telefone
                    )
                    
                    # Tenta processar fila se houver mensagens enfileiradas
                    queue_status = self.wasseller_queue.get_queue_status()
                    if queue_status['queue_stats']['pending'] > 0:
                        print(f"📋 Processando {queue_status['queue_stats']['pending']} mensagens da fila...")
                        queue_result = self.wasseller_queue.process_queue(max_messages=10)
                        print(f"✅ Fila processada: {queue_result.get('sent', 0)} enviadas, {queue_result.get('failed', 0)} falhas")
                    
                    notificacoes = {
                        'grupos': grupos_result,
                        'equipe': equipe_result,
                        'queue_status': queue_status
                    }
                else:
                    # Fallback: usa método direto
                    notificacoes = self.wasseller.send_notification_to_all(
                        analysis=analysis,
                        response_id=result['response_id'],
                        exclude_owner=True,
                        owner_phone=cliente_telefone
                    )
                
                result['steps']['notificacoes_equipe'] = {
                    'success': True,
                    'grupos_enviados': len(notificacoes.get('grupos', {}).get('enviados', [])),
                    'equipe_enviados': len(notificacoes.get('equipe', {}).get('enviados', [])),
                    'detalhes': notificacoes
                }
            except Exception as e:
                result['steps']['notificacoes_equipe'] = {
                    'success': False,
                    'error': str(e)
                }
                # Não adiciona aos erros críticos, pois é opcional
                print(f"Aviso: Erro ao enviar notificações para equipe: {e}")
            
            # Verifica se houve erros críticos
            if result['errors']:
                result['success'] = False
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Erro geral: {str(e)}")
            print(f"Erro ao processar resposta: {e}")
        
        return result
    
    def sync_google_forms(
        self,
        form_id: Optional[str] = None,
        last_sync: Optional[str] = None
    ) -> Dict:
        """
        Sincroniza respostas do Google Forms e processa automaticamente
        
        Args:
            form_id: ID do formulário
            last_sync: Timestamp da última sincronização
            
        Returns:
            Resultado da sincronização
        """
        if not self.google_forms:
            raise ValueError("Google Forms não inicializado. Configure as credenciais primeiro.")
        
        sync_result = {
            'timestamp': datetime.now().isoformat(),
            'form_id': form_id or Config.GOOGLE_FORMS_FORM_ID,
            'responses_processed': 0,
            'results': [],
            'errors': []
        }
        
        try:
            # Obtém novas respostas
            responses = self.google_forms.get_new_responses(form_id, last_sync)
            
            # Formata respostas
            formatted_responses = [
                self.google_forms.format_response_data(resp)
                for resp in responses
            ]
            
            # Processa cada resposta
            for response in formatted_responses:
                try:
                    result = self.process_form_response(response)
                    sync_result['results'].append(result)
                    sync_result['responses_processed'] += 1
                except Exception as e:
                    sync_result['errors'].append({
                        'response_id': response.get('response_id'),
                        'error': str(e)
                    })
            
        except Exception as e:
            sync_result['errors'].append({
                'error': f"Erro na sincronização: {str(e)}"
            })
        
        return sync_result
    
    def process_batch(self, form_responses: List[Dict]) -> Dict:
        """
        Processa múltiplas respostas em lote
        
        Args:
            form_responses: Lista de respostas do formulário
            
        Returns:
            Resultado do processamento em lote
        """
        batch_result = {
            'timestamp': datetime.now().isoformat(),
            'total': len(form_responses),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for response in form_responses:
            try:
                result = self.process_form_response(response)
                batch_result['results'].append(result)
                batch_result['processed'] += 1
                
                if result['success']:
                    batch_result['successful'] += 1
                else:
                    batch_result['failed'] += 1
                    
            except Exception as e:
                batch_result['failed'] += 1
                batch_result['results'].append({
                    'response_id': response.get('response_id'),
                    'success': False,
                    'error': str(e)
                })
        
        return batch_result

