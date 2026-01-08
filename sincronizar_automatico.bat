@echo off
chcp 65001 >nul
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"
echo ========================================
echo   SINCRONIZAÇÃO AUTOMÁTICA
echo ========================================
echo.
echo Data/Hora: %DATE% %TIME%
echo.

REM Executa sincronização de formulários
python -c "from orchestrator import IntegrationOrchestrator; from setup_google_auth import load_google_credentials; o = IntegrationOrchestrator(); creds = load_google_credentials(); o.set_google_credentials(creds) if creds else None; from integrations.google_forms import GoogleFormsIntegration; gf = GoogleFormsIntegration(creds) if creds else None; print('Sincronizando formulários...') if gf else print('Credenciais não encontradas'); results = gf.sync_all_forms() if gf else {}; print(f'Processados: {len(results.get(\"processed\", []))}') if results else None"

REM Alternativa: usar script Python dedicado se existir
if exist "sincronizar_forms.py" (
    python sincronizar_forms.py
) else (
    echo Executando sincronização via API...
    python -c "import requests; r = requests.post('http://localhost:5000/api/sync-all-forms'); print(r.json())" 2>nul || echo Servidor não está rodando. Execute app.py primeiro.
)

echo.
echo Sincronização concluída!
echo.

