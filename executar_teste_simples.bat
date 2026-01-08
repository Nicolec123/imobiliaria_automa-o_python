@echo off
chcp 65001 >nul
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"
python testar_integracoes_individualmente.py
pause

