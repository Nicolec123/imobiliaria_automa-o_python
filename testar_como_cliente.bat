@echo off
chcp 65001 >nul
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"
echo ========================================
echo   TESTE COMPLETO - SIMULANDO CLIENTE
echo ========================================
echo.
echo Este teste simula um cliente preenchendo o formulário
echo e verifica todo o fluxo automatizado.
echo.
echo Diretório: %CD%
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado!
    echo Por favor, instale Python 3.8 ou superior.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Verifica se as dependências estão instaladas
echo Verificando dependências...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Dependências não encontradas. Instalando...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependências!
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependências instaladas!
    echo.
) else (
    echo [OK] Dependências já instaladas
    echo.
)

REM Executa o teste completo
echo ========================================
echo   Executando teste completo...
echo ========================================
echo.
echo Este teste vai:
echo   - Simular cliente preenchendo formulário
echo   - Processar com ChatGPT
echo   - Criar tarefa no ClickUp
echo   - Gerar PDF
echo   - Salvar no Google Drive
echo   - Gerar XML do Chaves na Mão
echo   - Tentar enviar WhatsApp (se conectado)
echo.
echo Aguarde...
echo.

python testar_automacao.py

echo.
echo ========================================
echo   Teste concluído!
echo ========================================
echo.
echo Verifique:
echo   - PDFs na pasta 'pdfs/'
echo   - XMLs na pasta 'imoveis/'
echo   - Tarefas no ClickUp
echo   - Documentos no Google Drive
echo.
echo Pressione qualquer tecla para fechar...
pause >nul

