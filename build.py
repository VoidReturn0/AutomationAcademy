#!/usr/bin/env python3
"""
Build script for creating executable with PyInstaller
"""

import PyInstaller.__main__
import os
import shutil
import subprocess
from pathlib import Path

def build_executable():
    """Build the training application executable"""
    
    print("Starting build process...")
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Create version info file
    create_version_info()
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=BroetjeTrainingSystem',
        '--windowed',  # No console window
        '--onefile',   # Single executable file
        '--icon=resources/icons/broetje_icon.ico',
        '--add-data=resources;resources',
        '--add-data=modules;modules',
        '--add-data=config;config',
        '--hidden-import=PySide6.QtSvg',
        '--hidden-import=PySide6.QtPrintSupport',
        '--hidden-import=sqlite3',
        '--collect-all=qrcode',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        '--clean',
        '--version-file=version_info.txt'
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Copy additional files
    copy_deployment_files()
    
    # Create installer
    create_installer_package()
    
    print("Build complete! Installer created in dist/ directory")

def create_version_info():
    """Create version info file for Windows executable"""
    version_info = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Broetje Automation USA'),
           StringStruct(u'FileDescription', u'Broetje Training System'),
           StringStruct(u'FileVersion', u'1.0.0.0'),
           StringStruct(u'InternalName', u'BroetjeTrainingSystem'),
           StringStruct(u'LegalCopyright', u'© 2025 Broetje Automation USA'),
           StringStruct(u'OriginalFilename', u'BroetjeTrainingSystem.exe'),
           StringStruct(u'ProductName', u'Broetje Training System'),
           StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    with open("version_info.txt", "w") as f:
        f.write(version_info)

def copy_deployment_files():
    """Copy additional files needed for deployment"""
    dist_path = Path("dist")
    
    # Create data directory
    data_dir = dist_path / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Copy config files
    config_src = Path("config")
    if config_src.exists():
        config_dst = dist_path / "config"
        shutil.copytree(config_src, config_dst, dirs_exist_ok=True)
    
    # Copy documentation
    docs_src = Path("docs")
    if docs_src.exists():
        docs_dst = dist_path / "docs"
        shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
    
    # Create installation scripts
    create_install_scripts()

def create_install_scripts():
    """Create installation and uninstallation scripts"""
    dist_path = Path("dist")
    
    # Install script (Windows)
    install_script = """@echo off
echo Installing Broetje Training System...

REM Create program directory
mkdir "%ProgramFiles%\\Broetje Training System" 2>NUL

REM Copy executable
copy "BroetjeTrainingSystem.exe" "%ProgramFiles%\\Broetje Training System\\"

REM Copy data files
if exist "data" xcopy "data" "%ProgramFiles%\\Broetje Training System\\data\\" /E /I /Y
if exist "config" xcopy "config" "%ProgramFiles%\\Broetje Training System\\config\\" /E /I /Y
if exist "docs" xcopy "docs" "%ProgramFiles%\\Broetje Training System\\docs\\" /E /I /Y

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Broetje Training System.lnk'); $Shortcut.TargetPath = '%ProgramFiles%\\Broetje Training System\\BroetjeTrainingSystem.exe'; $Shortcut.Save()"

REM Create start menu entry
mkdir "%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Broetje Training System" 2>NUL
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Broetje Training System\\Broetje Training System.lnk'); $Shortcut.TargetPath = '%ProgramFiles%\\Broetje Training System\\BroetjeTrainingSystem.exe'; $Shortcut.Save()"

echo Installation complete!
pause
"""
    
    # Uninstall script
    uninstall_script = """@echo off
echo Uninstalling Broetje Training System...

REM Remove program files
rd /s /q "%ProgramFiles%\\Broetje Training System" 2>NUL

REM Remove desktop shortcut
del "%USERPROFILE%\\Desktop\\Broetje Training System.lnk" 2>NUL

REM Remove start menu entry
rd /s /q "%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Broetje Training System" 2>NUL

echo Uninstallation complete!
pause
"""
    
    with open(dist_path / "install.bat", "w") as f:
        f.write(install_script)
    
    with open(dist_path / "uninstall.bat", "w") as f:
        f.write(uninstall_script)
    
    print("Installation scripts created")

def create_installer_package():
    """Create a self-extracting installer using 7-Zip (if available)"""
    dist_path = Path("dist")
    
    # Create installer config
    installer_config = """
;!@Install@!UTF-8!
Title="Broetje Training System Installer"
BeginPrompt="Do you want to install Broetje Training System?"
RunProgram="install.bat"
;!@InstallEnd@!
"""
    
    config_path = dist_path / "installer_config.txt"
    with open(config_path, "w") as f:
        f.write(installer_config)
    
    # If 7-Zip is available, create self-extracting archive
    try:
        subprocess.run([
            "7z", "a", "-sfx7z.sfx", "-y",
            str(dist_path / "BroetjeTrainingSystem_Installer.exe"),
            str(dist_path / "*")
        ], check=True)
        print("Self-extracting installer created successfully")
    except:
        print("7-Zip not found. Manual ZIP creation recommended for distribution.")

if __name__ == "__main__":
    build_executable()