@echo off
chcp 65001 >nul
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"
echo ========================================
echo   TESTE DE INTEGRAÇÕES - IMOBILIÁRIA
echo ========================================
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

REM Executa o teste
echo ========================================
echo   Executando testes de integrações...
echo ========================================
echo.
python testar_integracoes_individualmente.py

echo.
echo ========================================
echo   Teste concluído!
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul

