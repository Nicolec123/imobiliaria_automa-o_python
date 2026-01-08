"""
Aplicação Flask principal - Hub central para integrações
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from orchestrator import IntegrationOrchestrator
from config import Config
from setup_google_auth import load_google_credentials
from datetime import datetime
import json
import os
import threading

app = Flask(__name__)
CORS(app)

# Inicializa o orquestrador
orchestrator = IntegrationOrchestrator()

# Carrega credenciais do Google se disponíveis
google_creds = load_google_credentials()
if google_creds:
    orchestrator.set_google_credentials(google_creds)


@app.route('/')
def index():
    """Página inicial"""
    return jsonify({
        'status': 'online',
        'message': 'Sistema de Integração Imobiliária',
        'endpoints': {
            'process_form': '/api/process-form',
            'sync_forms': '/api/sync-forms',
            'sync_all_forms': '/api/sync-all-forms',
            'webhook_forms': '/api/webhook/google-forms',
            'import_xml': '/api/chaves-na-mao/import-xml',
            'list_forms': '/api/forms',
            'health': '/api/health'
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'integrations': {
            'chatgpt': orchestrator.chatgpt is not None,
            'clickup': orchestrator.clickup is not None,
            'chaves_na_mao': True,  # Sempre disponível (gera XML, não precisa API)
            'wasseller': orchestrator.wasseller is not None,
            'google_forms': orchestrator.google_forms is not None,
            'google_drive': orchestrator.google_drive is not None
        },
        'chaves_na_mao_feed_url': '/api/chaves-na-mao/feed.xml'
    })


@app.route('/api/process-form', methods=['POST'])
def process_form():
    """
    Processa uma resposta de formulário
    
    Body:
        {
            "form_data": {...},
            "options": {
                "send_whatsapp": true,
                "create_lead": true,
                "save_to_drive": true,
                "create_task": true
            }
        }
    """
    try:
        data = request.json
        form_data = data.get('form_data', {})
        options = data.get('options', {})
        
        result = orchestrator.process_form_response(
            form_data,
            **options
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sync-forms', methods=['POST'])
def sync_forms():
    """
    Sincroniza respostas do Google Forms
    
    Body:
        {
            "form_id": "optional_form_id",
            "last_sync": "2024-01-01T00:00:00"
        }
    """
    try:
        data = request.json or {}
        form_id = data.get('form_id')
        last_sync = data.get('last_sync')
        
        result = orchestrator.sync_google_forms(form_id, last_sync)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


def process_form_background(form_response):
    """Processa formulário em background (thread separada)"""
    try:
        print(f"[Background] Processando formulário: {form_response.get('response_id', 'unknown')}")
        result = orchestrator.process_form_response(form_response)
        print(f"[Background] Formulário processado: {result.get('success', False)}")
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Background] Erro ao processar: {error_details}")
        return {
            'success': False,
            'error': str(e),
            'details': error_details
        }

@app.route('/api/webhook/google-forms', methods=['POST'])
def webhook_google_forms():
    """
    Webhook para receber notificações do Google Forms
    Responde IMEDIATAMENTE e processa em background para evitar timeout
    """
    try:
        data = request.json or {}
        
        # Aceita tanto form_response quanto form_data
        form_response = data.get('form_response') or data.get('form_data', {})
        
        if not form_response:
            return jsonify({
                'success': False,
                'error': 'form_response ou form_data não encontrado no payload'
            }), 400
        
        # Extrai informações básicas
        response_id = form_response.get('response_id', 'unknown')
        form_title = form_response.get('form_title', 'Formulário')
        
        # Responde IMEDIATAMENTE (evita timeout do Railway - máximo 30s)
        # O processamento acontece em background
        thread = threading.Thread(
            target=process_form_background,
            args=(form_response,),
            daemon=True  # Thread morre quando app morre
        )
        thread.start()
        
        # Responde imediatamente antes de processar
        return jsonify({
            'success': True,
            'message': 'Formulário recebido e será processado em background',
            'response_id': response_id,
            'form_title': form_title,
            'status': 'processing'
        }), 200
        
    except Exception as e:
        # Erro crítico - retorna 500
        import traceback
        error_details = traceback.format_exc()
        print(f"[Webhook] Erro crítico: {error_details}")
        
        # Mesmo com erro, tenta responder 200 para evitar retry do Google
        return jsonify({
            'success': False,
            'message': 'Erro ao receber requisição, mas registro criado',
            'error': str(e)
        }), 200


@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """
    Processa múltiplas respostas em lote
    
    Body:
        {
            "responses": [...]
        }
    """
    try:
        data = request.json
        responses = data.get('responses', [])
        
        result = orchestrator.process_batch(responses)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/sync-all-forms', methods=['POST'])
def sync_all_forms():
    """
    Sincroniza todos os formulários configurados
    
    Body (opcional):
        {
            "last_sync": "2024-01-01T00:00:00"
        }
    """
    try:
        data = request.json or {}
        last_sync = data.get('last_sync')
        
        form_ids = Config.get_form_ids()
        forms_config = Config.get_forms_config()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_forms': len(form_ids),
            'forms_processed': 0,
            'total_responses': 0,
            'form_results': [],
            'errors': []
        }
        
        for form_id in form_ids:
            form_info = Config.get_form_by_id(form_id)
            try:
                result = orchestrator.sync_google_forms(form_id, last_sync)
                results['form_results'].append({
                    'form_id': form_id,
                    'form_name': form_info['name'] if form_info else 'Unknown',
                    'responses_processed': result.get('responses_processed', 0),
                    'success': True
                })
                results['total_responses'] += result.get('responses_processed', 0)
                results['forms_processed'] += 1
            except Exception as e:
                results['errors'].append({
                    'form_id': form_id,
                    'form_name': form_info['name'] if form_info else 'Unknown',
                    'error': str(e)
                })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/forms', methods=['GET'])
def list_forms():
    """Lista todos os formulários configurados"""
    try:
        forms_config = Config.get_forms_config()
        return jsonify(forms_config), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/chaves-na-mao/import-xml', methods=['POST'])
def import_xml():
    """
    Importa imóveis a partir de XML do Chaves na Mão
    
    Body:
        {
            "xml_content": "<?xml version=\"1.0\"...",
            "file_path": "optional_path_to_xml_file"
        }
    """
    try:
        data = request.json
        xml_content = data.get('xml_content')
        file_path = data.get('file_path')
        
        if file_path:
            # Importa de arquivo
            results = orchestrator.chaves_na_mao.import_properties_from_xml_file(file_path)
            return jsonify({
                'success': True,
                'total': len(results),
                'successful': sum(1 for r in results if r.get('success')),
                'failed': sum(1 for r in results if not r.get('success')),
                'results': results
            }), 200
        elif xml_content:
            # Importa de string XML
            property_data = orchestrator.chaves_na_mao.parse_xml_property(xml_content)
            result = orchestrator.chaves_na_mao.import_property_from_xml(xml_content)
            return jsonify({
                'success': True,
                'property': result,
                'parsed_data': property_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'É necessário fornecer xml_content ou file_path'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chaves-na-mao/generate-xml', methods=['POST'])
def generate_xml():
    """
    Gera XML do Chaves na Mão a partir de dados do formulário
    
    Body:
        {
            "form_data": {...},
            "analysis": {...}
        }
    """
    try:
        from integrations.chaves_na_mao_xml_generator import ChavesNaMaoXMLGenerator
        
        data = request.json
        form_data = data.get('form_data', {})
        analysis = data.get('analysis', {})
        
        generator = ChavesNaMaoXMLGenerator()
        xml_content = generator.generate_xml_from_form_data(form_data, analysis)
        
        return xml_content, 200, {'Content-Type': 'application/xml; charset=utf-8'}
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chaves-na-mao/feed.xml', methods=['GET'])
def chaves_na_mao_feed():
    """
    Endpoint que serve o XML feed do Chaves na Mão
    Gera XML dinamicamente a partir dos dados processados
    """
    try:
        from integrations.chaves_na_mao_xml_generator import ChavesNaMaoXMLGenerator
        import os
        
        generator = ChavesNaMaoXMLGenerator()
        
        # Tenta carregar XML salvo, ou gera vazio
        xml_file = 'chaves_na_mao_feed.xml'
        if os.path.exists(xml_file):
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
        else:
            # Gera XML vazio
            xml_content = generator.generate_feed_xml([])
        
        return xml_content, 200, {'Content-Type': 'application/xml; charset=utf-8'}
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    Config.validate()
    # Railway define PORT automaticamente, usa 5000 como fallback
    port = int(os.environ.get('PORT', Config.FLASK_PORT))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.FLASK_DEBUG
    )

