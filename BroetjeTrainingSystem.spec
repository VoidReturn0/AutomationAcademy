# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy/config', 'config'), ('/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy/modules', 'modules'), ('/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy/resources', 'resources')],
    hiddenimports=['completion_tracker', 'progress_tracker', 'enhanced_progress_system', 'user_manager', 'module_loader', 'training_module', 'module_window', 'module_window_enhanced', 'additional_modules', 'fallback_modules', 'github_integration', 'user_managment', 'path_helper', 'json_progress_tracker'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BroetjeTrainingSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icons/broetje_icon.png'],
)
