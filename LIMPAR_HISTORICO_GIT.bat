@echo off
chcp 65001 >nul
echo ========================================
echo   LIMPAR HISTÓRICO DO GIT
echo ========================================
echo.
echo Este script vai remover arquivos com segredos do histórico do Git.
echo.
echo ⚠️  ATENÇÃO: Isso vai reescrever o histórico do Git!
echo.
pause

echo.
echo Removendo arquivos do histórico...
echo.

REM Remover arquivos específicos do histórico
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch google_credentials.json.backup teste.txt" --prune-empty --tag-name-filter cat -- --all

if %errorLevel% equ 0 (
    echo.
    echo ✅ Histórico limpo!
    echo.
    echo Agora você pode fazer push:
    echo   git push --force
    echo.
    echo ⚠️  ATENÇÃO: Use --force apenas se ninguém mais está usando este repositório!
) else (
    echo.
    echo ❌ Erro ao limpar histórico
    echo.
    echo Tente usar git filter-repo (mais moderno):
    echo   pip install git-filter-repo
    echo   git filter-repo --path google_credentials.json.backup --invert-paths
    echo   git filter-repo --path teste.txt --invert-paths
)

echo.
pause
