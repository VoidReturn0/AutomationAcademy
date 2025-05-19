#!/usr/bin/env python3
import PyInstaller.__main__
import shutil
from pathlib import Path

def build():
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
    
    # Basic build without icon (for testing)
    PyInstaller.__main__.run([
        'main.py',
        '--name=BroetjeTrainingSystem',
        '--onefile',
        '--windowed',
        '--add-data=config;config',
        '--clean'
    ])
    
    print("Build complete! Check dist/ folder")

if __name__ == "__main__":
    build()