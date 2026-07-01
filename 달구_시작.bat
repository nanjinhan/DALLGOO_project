@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 달구 게시판 서버

echo ============================================
echo   달구 게시판 시작
echo ============================================
echo.
echo [1/2] 백엔드(도커) 시작 중...
echo   ^(Docker Desktop이 켜져 있어야 합니다^)
docker compose up -d
if errorlevel 1 (
  echo.
  echo [!] 도커 실행 실패 - Docker Desktop을 먼저 켠 뒤 다시 실행하세요.
  echo.
  pause
  exit /b 1
)
echo   백엔드 준비 완료. (http://localhost:8000)
echo.
echo [2/2] 프론트엔드 시작 중...
echo   브라우저에서 http://localhost:5173 접속하세요.
echo   ^(이 창을 닫으면 프론트엔드가 꺼집니다^)
echo.
cd frontend
call npm run dev
