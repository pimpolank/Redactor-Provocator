@echo off
chcp 65001
title Запуск Clipmaster в Docker

echo ===============================================
echo [1/3] Сборка Docker-образа Clipmaster...
echo ===============================================
docker build -t clipmaster .

if %ERRORLEVEL% neq 0 (
    echo Ошибка при сборке образа! Проверьте Dockerfile.
    pause
    exit /b
)

echo.
echo ===============================================
echo [2/3] Убедитесь, что X-сервер (VcXsrv) запущен!
echo Нажмите любую клавишу, чтобы продолжить...
echo ===============================================
pause >nul

echo.
echo ===============================================
echo [3/3] Запуск контейнера Clipmaster...
echo ===============================================
docker run -it --rm ^
    -e DISPLAY=host.docker.internal:0.0 ^
    --name clipmaster_container ^
    clipmaster python3 clipmaster/app.py

echo.
echo ===============================================
echo Работа приложения завершена.
pause
