@echo off
chcp 65001 >nul
echo ========================================
echo   CRIAR TAREFA AGENDADA
echo ========================================
echo.
echo Este script criará uma tarefa no Task Scheduler do Windows
echo para executar a sincronização automaticamente.
echo.
echo Opções de agendamento:
echo   1. A cada hora
echo   2. A cada 2 horas
echo   3. A cada 4 horas
echo   4. 3 vezes por dia (8h, 14h, 20h)
echo   5. Uma vez por dia (9h)
echo.
set /p opcao="Escolha uma opção (1-5): "

set "script_path=%~dp0sincronizar_automatico.bat"
set "task_name=Imobiliaria_Sincronizacao_Automatica"

if "%opcao%"=="1" (
    schtasks /create /tn "%task_name%" /tr "\"%script_path%\"" /sc hourly /f
    echo.
    echo ✅ Tarefa criada: Executa a cada hora
)

if "%opcao%"=="2" (
    schtasks /create /tn "%task_name%" /tr "\"%script_path%\"" /sc hourly /mo 2 /f
    echo.
    echo ✅ Tarefa criada: Executa a cada 2 horas
)

if "%opcao%"=="3" (
    schtasks /create /tn "%task_name%" /tr "\"%script_path%\"" /sc hourly /mo 4 /f
    echo.
    echo ✅ Tarefa criada: Executa a cada 4 horas
)

if "%opcao%"=="4" (
    schtasks /create /tn "%task_name%_Manha" /tr "\"%script_path%\"" /sc daily /st 08:00 /f
    schtasks /create /tn "%task_name%_Tarde" /tr "\"%script_path%\"" /sc daily /st 14:00 /f
    schtasks /create /tn "%task_name%_Noite" /tr "\"%script_path%\"" /sc daily /st 20:00 /f
    echo.
    echo ✅ Tarefas criadas: 8h, 14h e 20h
)

if "%opcao%"=="5" (
    schtasks /create /tn "%task_name%" /tr "\"%script_path%\"" /sc daily /st 09:00 /f
    echo.
    echo ✅ Tarefa criada: Executa diariamente às 9h
)

echo.
echo ========================================
echo   TAREFA CRIADA COM SUCESSO!
echo ========================================
echo.
echo Para gerenciar a tarefa:
echo   - Abra o "Agendador de Tarefas" do Windows
echo   - Procure por: %task_name%
echo.
echo Para remover a tarefa:
echo   schtasks /delete /tn "%task_name%" /f
echo.
pause

