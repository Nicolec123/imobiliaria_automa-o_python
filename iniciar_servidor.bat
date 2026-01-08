@echo off
chcp 65001 >nul
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"
echo ========================================
echo   SERVIDOR API - SISTEMA DE INTEGRAÇÃO
echo ========================================
echo.
echo Iniciando servidor na porta 5000...
echo Acesse: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python app.py

pause

