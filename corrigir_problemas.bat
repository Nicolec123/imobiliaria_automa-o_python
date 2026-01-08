@echo off
chcp 65001 >nul
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"
echo ========================================
echo   CORREÇÃO AUTOMÁTICA DE PROBLEMAS
echo ========================================
echo.

echo [1/3] Corrigindo bibliotecas OpenAI/httpx...
python -m pip install --upgrade 'openai>=1.12.0' 'httpx>=0.27.0'
if %errorLevel% equ 0 (
    echo ✅ Bibliotecas atualizadas com sucesso!
) else (
    echo ❌ Erro ao atualizar bibliotecas
)
echo.

echo [2/3] Verificando outras dependências...
pip install --upgrade -r requirements.txt
if %errorLevel% equ 0 (
    echo ✅ Dependências verificadas!
) else (
    echo ⚠️  Alguns pacotes podem ter problemas
)
echo.

echo [3/3] Testando novamente...
echo.
python testar_integracoes_individualmente.py

echo.
echo ========================================
echo   CORREÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Se ainda houver erros:
echo   1. Google Forms: Verifique se o Form ID está correto
echo   2. Chaves na Mão: API Key é opcional (pode ignorar)
echo   3. Reinicie o terminal e teste novamente
echo.
pause

