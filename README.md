# Sistema de Integração para Imobiliária

Sistema completo de integração e automação de ferramentas essenciais para otimização das operações imobiliárias.

## 🎯 Funcionalidades

Este sistema integra as seguintes ferramentas:

1. **Google Forms + ChatGPT**: Processamento inteligente de formulários com análise de dados
2. **ClickUp**: Criação automática de tarefas e projetos
3. **Google Drive**: Sincronização e armazenamento de documentos
4. **Chaves na Mão**: Gestão de leads e imóveis
5. **Wasseller**: Automação de comunicações via WhatsApp
6. **Website Hub**: API REST para integração com website da imobiliária

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Contas e credenciais de API para:
  - Google Cloud Platform (Forms, Drive)
  - OpenAI (ChatGPT)
  - ClickUp
  - Chaves na Mão
  - Wasseller

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd "Imobiliáriantegração de Ferramentas Essenciais para Imobiliária"
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais reais.

## ⚙️ Configuração

### Google APIs

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative as APIs:
   - Google Forms API
   - Google Drive API
4. Crie credenciais OAuth 2.0
5. Configure o redirect URI: `http://localhost:8080/callback`
6. Adicione as credenciais no arquivo `.env`

### OpenAI/ChatGPT

1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Crie uma conta e obtenha sua API Key
3. Adicione no `.env`: `OPENAI_API_KEY=sk-...`

### ClickUp

1. Acesse [ClickUp Settings](https://app.clickup.com/settings/apps)
2. Gere um API Token
3. Adicione no `.env`: `CLICKUP_API_KEY=...`
4. Obtenha os IDs necessários (Team, Space, List)

### Chaves na Mão

1. Entre em contato com o suporte da Chaves na Mão
2. Obtenha sua API Key
3. Adicione no `.env`

### Wasseller

1. Acesse sua conta Wasseller
2. Obtenha API Key e Instance ID
3. Adicione no `.env`

## 🏃 Uso

### Setup Inicial (Primeira Vez)

1. **Criar arquivo .env:**
```bash
python create_env.py
```

2. **Executar setup e validação:**
```bash
python setup_and_test.py
```

3. **Configurar autenticação Google (se necessário):**
```bash
python setup_google_auth.py
```

### Executar Testes de Automação

```bash
# Executar todos os testes
python test_automation.py

# Ou usar o script de automação
python run_automation.py --test
```

### Executar Automações

```bash
# Sincronizar todos os formulários
python run_automation.py --sync

# Processar XML do Chaves na Mão
python run_automation.py --xml caminho/para/arquivo.xml

# Executar tudo
python run_automation.py --all
```

### Executar o servidor Flask

```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

### Endpoints da API

#### Health Check
```
GET /api/health
```

#### Processar Formulário
```
POST /api/process-form
Body: {
    "form_data": {...},
    "options": {
        "send_whatsapp": true,
        "create_lead": true,
        "save_to_drive": true,
        "create_task": true
    }
}
```

#### Sincronizar Google Forms
```
POST /api/sync-forms
Body: {
    "form_id": "optional",
    "last_sync": "2024-01-01T00:00:00"
}
```

#### Webhook Google Forms
```
POST /api/webhook/google-forms
Body: {
    "form_response": {...}
}
```

#### Processamento em Lote
```
POST /api/batch-process
Body: {
    "responses": [...]
}
```

## 📁 Estrutura do Projeto

```
.
├── integrations/          # Módulos de integração
│   ├── __init__.py
│   ├── google_forms.py   # Integração Google Forms
│   ├── chatgpt.py        # Integração ChatGPT
│   ├── clickup.py         # Integração ClickUp
│   ├── google_drive.py   # Integração Google Drive
│   ├── chaves_na_mao.py  # Integração Chaves na Mão
│   └── wasseller.py      # Integração Wasseller
├── orchestrator.py        # Orquestrador principal
├── app.py                 # Aplicação Flask
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── .env.example          # Exemplo de variáveis de ambiente
└── README.md             # Este arquivo
```

## 🔄 Fluxo de Trabalho

1. **Formulário Preenchido**: Cliente preenche Google Forms
2. **Análise ChatGPT**: Sistema analisa dados com IA
3. **ClickUp**: Cria tarefa automaticamente
4. **Chaves na Mão**: Cria lead no CRM
5. **Google Drive**: Salva documento com dados
6. **WhatsApp**: Envia mensagem de confirmação ao cliente

## 🛠️ Desenvolvimento

### Adicionar nova integração

1. Crie um novo arquivo em `integrations/`
2. Implemente a classe de integração
3. Adicione ao `orchestrator.py`
4. Atualize `config.py` se necessário

### Testar integrações

```python
from integrations.chatgpt import ChatGPTIntegration

chatgpt = ChatGPTIntegration()
analysis = chatgpt.analyze_form_data({"nome": "João", "telefone": "11999999999"})
print(analysis)
```

## ⚠️ PENDÊNCIAS E CONFIGURAÇÕES NECESSÁRIAS

**📋 IMPORTANTE:** Antes de usar o sistema, consulte o documento completo:
**[PENDENCIAS_E_CONFIGURACAO.md](PENDENCIAS_E_CONFIGURACAO.md)**

### Resumo das Pendências:

1. **Configuração de Credenciais:**
   - ⚠️ Obter todas as API Keys (Google, OpenAI, ClickUp, Chaves na Mão, Wasseller)
   - ⚠️ Configurar arquivo `.env` com credenciais reais
   - ⚠️ Configurar autenticação OAuth2 do Google

2. **APIs Não Verificadas:**
   - ⚠️ **Chaves na Mão:** Verificar se API existe e obter documentação
   - ⚠️ **Wasseller:** Verificar endpoints reais da API

3. **Testes:**
   - ⚠️ Testar cada integração individualmente
   - ⚠️ Testar fluxo completo end-to-end

4. **Automação:**
   - ⚠️ Implementar webhook ou polling para Google Forms
   - ⚠️ Configurar scheduler para processamento automático

**Consulte `PENDENCIAS_E_CONFIGURACAO.md` para detalhes completos!**

## 📝 Notas Importantes

- **Segurança**: Nunca commite o arquivo `.env` com credenciais reais
- **Rate Limits**: Respeite os limites de API de cada serviço
- **Erros**: O sistema continua funcionando mesmo se uma integração falhar
- **Logs**: Monitore os logs para identificar problemas

## 🐛 Troubleshooting

### Erro de autenticação Google
- Verifique se as credenciais OAuth2 estão corretas
- Confirme que o redirect URI está configurado

### Erro ChatGPT
- Verifique se a API Key está válida
- Confirme se há créditos disponíveis na conta OpenAI

### Erro ClickUp
- Verifique se os IDs (Team, Space, List) estão corretos
- Confirme permissões da API Key

## 📄 Licença

Este projeto é proprietário e destinado ao uso interno da imobiliária.

## 👥 Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.

