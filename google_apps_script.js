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

// CONFIGURAÇÃO: URL da sua API
// IMPORTANTE: Use o endpoint /api/webhook/google-forms
const API_URL = 'https://8daf4fa3da63.ngrok-free.app/api/webhook/google-forms';

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
    'headers': {
      'ngrok-skip-browser-warning': 'true'  // Pula aviso do ngrok free
    }
  };
  
  try {
    const response = UrlFetchApp.fetch(API_URL, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    if (responseCode === 200) {
      return JSON.parse(responseText);
    } else {
      throw new Error('Erro na API: ' + responseCode + ' - ' + responseText);
    }
  } catch (error) {
    Logger.log('Erro ao enviar para API: ' + error.toString());
    throw error;
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

