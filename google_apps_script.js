/**
 * Google Apps Script para integração com Sistema de Automação
 * 
 * INSTRUÇÕES:
 * 1. Abra seu Google Form
 * 2. Clique nos 3 pontos (menu) > Scripts do editor
 * 3. Cole este código
 * 4. Configure a URL da API (linha 8)
 * 5. Salve e autorize o script
 * 6. Configure o trigger (Editar > Acionadores do projeto atual)
 * 7. Adicione trigger: "Ao enviar formulário" > "processarFormulario"
 */

// CONFIGURAÇÃO: URL da sua API (Railway)
// IMPORTANTE: Use o endpoint /api/webhook/google-forms
const API_URL = 'https://web-production-5ed79.up.railway.app/api/webhook/google-forms';

/**
 * Função principal que é executada quando formulário é enviado
 */
function processarFormulario(e) {
  try {
    // Obtém dados do formulário
    const formResponse = e.response;
    const form = e.source;
    
    // Extrai informações do formulário
    const formData = extrairDadosFormulario(formResponse, form);
    
    // Envia para API
    const resultado = enviarParaAPI(formData);
    
    // Log do resultado
    Logger.log('Formulário processado: ' + JSON.stringify(resultado));
    
    // Opcional: Enviar email de confirmação
    // enviarEmailConfirmacao(formData);
    
  } catch (error) {
    Logger.log('Erro ao processar formulário: ' + error.toString());
    // Opcional: Enviar email de erro
    // MailApp.sendEmail('danieleoffice24@gmail.com', 'Erro no Sistema', error.toString());
  }
}

/**
 * Extrai dados do formulário
 */
function extrairDadosFormulario(formResponse, form) {
  const itemResponses = formResponse.getItemResponses();
  const dados = {
    form_id: form.getId(),
    form_title: form.getTitle(),
    response_id: formResponse.getId(),
    timestamp: formResponse.getTimestamp().toISOString(),
    email: formResponse.getRespondentEmail() || '',
    fields: {}
  };
  
  // Extrai cada resposta
  itemResponses.forEach(function(itemResponse) {
    const item = itemResponse.getItem();
    const title = item.getTitle();
    const response = itemResponse.getResponse();
    
    dados.fields[title] = response;
  });
  
  return dados;
}

/**
 * Envia dados para API
 */
function enviarParaAPI(formData) {
  // O endpoint /api/webhook/google-forms espera form_response
  const payload = {
    form_response: formData
  };
  
  const options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true,
    'followRedirects': true,
    'validateHttpsCertificates': true,
    'headers': {
      'User-Agent': 'GoogleAppsScript'
    }
  };
  
  try {
    // Timeout de 30 segundos (Google Apps Script máximo é 30s)
    const response = UrlFetchApp.fetch(API_URL, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    Logger.log('Response Code: ' + responseCode);
    Logger.log('Response Text: ' + responseText);
    
    if (responseCode === 200) {
      try {
        const result = JSON.parse(responseText);
        Logger.log('Resposta parseada com sucesso');
        return result;
      } catch (parseError) {
        Logger.log('Erro ao parsear JSON: ' + parseError.toString());
        // Mesmo com erro de parse, se o código é 200, consideramos sucesso
        return {
          'success': true,
          'message': 'Resposta recebida (parse JSON falhou)',
          'raw_response': responseText
        };
      }
    } else if (responseCode >= 500) {
      // Erro do servidor - não tenta novamente
      Logger.log('Erro 5xx do servidor: ' + responseCode);
      throw new Error('Erro no servidor (5xx): ' + responseCode + ' - ' + responseText);
    } else {
      // Erro 4xx - erro do cliente
      Logger.log('Erro 4xx: ' + responseCode);
      throw new Error('Erro na requisição (4xx): ' + responseCode + ' - ' + responseText);
    }
  } catch (error) {
    Logger.log('Erro ao enviar para API: ' + error.toString());
    Logger.log('Tipo do erro: ' + typeof error);
    
    // Não relança o erro para não bloquear o formulário
    // Apenas registra
    return {
      'success': false,
      'error': error.toString(),
      'message': 'Erro ao enviar para API, mas formulário foi salvo no Google Forms'
    };
  }
}

/**
 * Função auxiliar para enviar email de confirmação (opcional)
 */
function enviarEmailConfirmacao(formData) {
  const assunto = 'Novo Lead Recebido: ' + formData.form_title;
  const corpo = 'Um novo formulário foi recebido e processado:\n\n' +
                'ID: ' + formData.response_id + '\n' +
                'Data: ' + formData.timestamp + '\n\n' +
                'Dados:\n' + JSON.stringify(formData.fields, null, 2);
  
  MailApp.sendEmail({
    to: 'danieleoffice24@gmail.com',
    subject: assunto,
    body: corpo
  });
}

/**
 * Função de teste (executar manualmente)
 */
function testarIntegracao() {
  // Simula evento de formulário para teste
  const form = FormApp.getActiveForm();
  const responses = form.getResponses();
  
  if (responses.length > 0) {
    const ultimaResposta = responses[responses.length - 1];
    const event = {
      response: ultimaResposta,
      source: form
    };
    
    processarFormulario(event);
    Logger.log('Teste executado com sucesso!');
  } else {
    Logger.log('Nenhuma resposta encontrada para testar');
  }
}

