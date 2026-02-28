@echo off
chcp 65001 >nul
title CS2 PRO ASSISTANT — EXE Builder
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║     CS2 PRO ASSISTANT — Otomatik EXE Oluşturucu     ║
echo  ║             by Burak (r001B) Aydogdu                 ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

REM ── 1. Python kontrolü
echo [1/5] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [HATA] Python bulunamadi!
    echo  Lutfen https://python.org adresinden Python 3.10+ indirin.
    echo  ONEMLI: "Add Python to PATH" kutusunu isaretleyin!
    pause
    exit /b 1
)
python --version
echo  Python OK.
echo.

REM ── 2. pip güncelle
echo [2/5] pip guncelleniyor...
python -m pip install --upgrade pip --quiet
echo  pip OK.
echo.

REM ── 3. Gerekli paketleri kur
echo [3/5] Gerekli paketler kuruluyor...
echo  ^> pyinstaller...
pip install pyinstaller --quiet
echo  ^> Pillow...
pip install Pillow --quiet
echo  Paketler OK.
echo.

REM ── 4. EXE derle
echo [4/5] EXE derleniyor... (1-3 dakika surebilir)
echo.

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "CS2_PRO_ASSISTANT" ^
  --icon "icon.ico" ^
  --add-data "data;data" ^
  --add-data "maps;maps" ^
  --hidden-import "PIL" ^
  --hidden-import "PIL._tkinter_finder" ^
  --hidden-import "tkinter" ^
  --hidden-import "tkinter.ttk" ^
  --hidden-import "tkinter.scrolledtext" ^
  --clean ^
  main.py

REM icon yoksa tekrar dene
if errorlevel 1 (
    echo  [BILGI] icon.ico bulunamadi, ikonsuz derleniyor...
    pyinstaller ^
      --onefile ^
      --windowed ^
      --name "CS2_PRO_ASSISTANT" ^
      --add-data "data;data" ^
      --add-data "maps;maps" ^
      --hidden-import "PIL" ^
      --hidden-import "PIL._tkinter_finder" ^
      --hidden-import "tkinter" ^
      --hidden-import "tkinter.ttk" ^
      --hidden-import "tkinter.scrolledtext" ^
      --clean ^
      main.py
)

echo.
echo [5/5] Kontrol ediliyor...
if exist "dist\CS2_PRO_ASSISTANT.exe" (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║              ✅  EXE BASARIYLA OLUSTURULDU!          ║
    echo  ║                                                      ║
    echo  ║   Konum: dist\CS2_PRO_ASSISTANT.exe                 ║
    echo  ║                                                      ║
    echo  ║   ONEMLI: EXE ile ayni klasorde su klasorler olmali: ║
    echo  ║     - data\   (otomatik olusur)                     ║
    echo  ║     - maps\   (harita resimlerini buraya koy)        ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    REM data ve maps klasörlerini dist'e kopyala
    if not exist "dist\data" mkdir "dist\data"
    if not exist "dist\maps" mkdir "dist\maps"
    if exist "data" xcopy /E /I /Q "data" "dist\data" >nul 2>&1
    if exist "maps" xcopy /E /I /Q "maps" "dist\maps" >nul 2>&1
    echo  dist\data ve dist\maps klasorleri hazir.
    echo.
    set /p OPEN="EXE'yi simdi acmak ister misiniz? (E/H): "
    if /i "%OPEN%"=="E" start "" "dist\CS2_PRO_ASSISTANT.exe"
) else (
    echo.
    echo  [HATA] EXE olusturulamadi!
    echo  Lutfen BUILD_LOG.txt dosyasini kontrol edin.
    echo  Hata cozumu: python main.py komutuyla once test edin.
)

echo.
pause