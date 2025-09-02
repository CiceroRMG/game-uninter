@echo off
setlocal ENABLEDELAYEDEXPANSION

echo === BrainRotGame Build ===

REM
if exist dist  rd /s /q dist
if exist build rd /s /q build

REM
for /f "delims=" %%P in ('python -c "import sys;print(sys.version.split()[0])" 2^>NUL') do set PYVER=%%P
if not defined PYVER (
  echo Python nao encontrado no PATH.
  pause
  exit /b 1
)
echo Python detectado: %PYVER%

REM 3. Criar venv se nao existir
if not exist .venv (
  echo Criando ambiente virtual...
  python -m venv .venv
)

call .venv\Scripts\activate

REM
echo Atualizando pip...
python -m pip install --upgrade pip >nul
echo Instalando dependencias...
pip install pygame Pillow pyinstaller >nul
if errorlevel 1 (
  echo Falha instalando dependencias.
  pause
  exit /b 1
)

REM
if not exist assets\fonts  mkdir assets\fonts
if not exist assets\sounds mkdir assets\sounds

REM
echo Gerando executavel...
pyinstaller --clean --noconfirm --name BrainRotGame --noconsole ^
  --add-data ".\assets\images;assets/images" ^
  --add-data ".\assets\fonts;assets/fonts" ^
  --add-data ".\assets\sounds;assets/sounds" ^
  .\src\main.py
if errorlevel 1 (
  echo Erro no PyInstaller.
  pause
  exit /b 1
)

REM
if not exist dist\BrainRotGame\BrainRotGame.exe (
  echo Nao foi gerado o EXE. Ver log acima.
  pause
  exit /b 1
)

REM
echo Compactando ZIP...
powershell -command "Compress-Archive -Path 'dist\\BrainRotGame\\*' -DestinationPath 'BrainRotGame_windows.zip' -Force"

echo.
echo === Concluido ===
echo Executavel: dist\BrainRotGame\BrainRotGame.exe
echo ZIP: BrainRotGame_windows.zip
echo Pressione uma tecla para sair.
pause
endlocal