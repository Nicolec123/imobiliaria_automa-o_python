@echo off
chcp 65001 >nul
echo ========================================
echo   CRIAR EXECUTÁVEL (.EXE)
echo ========================================
echo.
echo Este script criará um arquivo .exe standalone
echo que não precisa de Python instalado.
echo.

REM Verifica se PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if %errorLevel% neq 0 (
    echo PyInstaller não encontrado. Instalando...
    pip install pyinstaller
    if %errorLevel% neq 0 (
        echo ❌ Erro ao instalar PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Criando executável...
echo.

REM Cria o executável
pyinstaller --onefile ^
    --name "ImobiliariaIntegracao" ^
    --icon=NONE ^
    --add-data "forms_config.json;." ^
    --add-data "wasseller_config.json;." ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=google ^
    --hidden-import=openai ^
    --hidden-import=requests ^
    testar_integracoes_individualmente.py

if %errorLevel% equ 0 (
    echo.
    echo ✅ EXECUTÁVEL CRIADO COM SUCESSO!
    echo.
    echo Localização: dist\ImobiliariaIntegracao.exe
    echo.
    echo Você pode distribuir este arquivo .exe para outros computadores
    echo sem precisar instalar Python!
    echo.
) else (
    echo.
    echo ❌ Erro ao criar executável
    echo.
)

pause

