@echo off
chcp 65001 >nul
echo ========================================
echo   INSTALAR SERVIÇO WINDOWS
echo ========================================
echo.
echo Este script instalará o sistema como serviço do Windows
echo para rodar automaticamente em background.
echo.
echo IMPORTANTE: Execute como Administrador!
echo.
pause

REM Verifica se está como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ❌ ERRO: Execute este script como Administrador!
    echo Clique com botão direito e escolha "Executar como administrador"
    pause
    exit /b 1
)

set "servico_nome=ImobiliariaIntegracao"
set "servico_display=Imobiliária - Sistema de Integração"
set "servico_desc=Automação de integrações para imobiliária (Google Forms, ClickUp, WhatsApp, etc)"
set "script_path=%~dp0servico_windows.py"
set "python_path=pythonw.exe"

echo.
echo Verificando Python...
where pythonw.exe >nul 2>&1
if %errorLevel% neq 0 (
    where python.exe >nul 2>&1
    if %errorLevel% neq 0 (
        echo ❌ ERRO: Python não encontrado!
        pause
        exit /b 1
    )
    set "python_path=python.exe"
)

echo ✅ Python encontrado: %python_path%
echo.

REM Cria script de serviço se não existir
if not exist "servico_windows.py" (
    echo Criando script de serviço...
    (
        echo import win32serviceutil
        echo import win32service
        echo import servicemanager
        echo import socket
        echo import sys
        echo import os
        echo from app import app
        echo.
        echo class ImobiliariaService^(win32serviceutil.ServiceFramework^):
        echo     _svc_name_ = "%servico_nome%"
        echo     _svc_display_name_ = "%servico_display%"
        echo     _svc_description_ = "%servico_desc%"
        echo.
        echo     def __init__^(self, args^):
        echo         win32serviceutil.ServiceFramework.__init__^(self, args^)
        echo         self.stop_event = win32service.CreateEvent^(None, 0, 0, None^)
        echo         socket.setdefaulttimeout^(60^)
        echo.
        echo     def SvcStop^(self^):
        echo         self.ReportServiceStatus^(win32service.SERVICE_STOP_PENDING^)
        echo         self.stop_event.set^()
        echo.
        echo     def SvcDoRun^(self^):
        echo         servicemanager.LogMsg^(
        echo             servicemanager.EVENTLOG_INFORMATION_TYPE,
        echo             servicemanager.PYS_SERVICE_STARTED,
        echo             ^(self._svc_name_, ''^)
        echo         ^)
        echo         self.main^()
        echo.
        echo     def main^(self^):
        echo         os.chdir^(os.path.dirname^(os.path.abspath^(__file__^)^)^)
        echo         app.run^(host='0.0.0.0', port=5000, debug=False^)
        echo.
        echo if __name__ == '__main__':
        echo     win32serviceutil.HandleCommandLine^(ImobiliariaService^)
    ) > servico_windows.py
    echo ✅ Script criado
)

echo.
echo Instalando serviço...
%python_path% servico_windows.py install

if %errorLevel% equ 0 (
    echo.
    echo ✅ SERVIÇO INSTALADO COM SUCESSO!
    echo.
    echo Para iniciar o serviço:
    echo   net start %servico_nome%
    echo.
    echo Para parar o serviço:
    echo   net stop %servico_nome%
    echo.
    echo Para desinstalar:
    echo   %python_path% servico_windows.py remove
    echo.
    set /p iniciar="Deseja iniciar o serviço agora? (S/N): "
    if /i "%iniciar%"=="S" (
        net start %servico_nome%
        echo.
        echo ✅ Serviço iniciado!
    )
) else (
    echo.
    echo ❌ ERRO ao instalar serviço
    echo.
    echo Possíveis causas:
    echo   - Falta instalar pywin32: pip install pywin32
    echo   - Não está executando como administrador
    echo   - Serviço já existe (desinstale primeiro)
)

echo.
pause

