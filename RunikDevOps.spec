# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('logs', 'logs')],
    hiddenimports=['tkinter', 'psutil', 'winreg', 'ctypes', '..base_tab', '..build_exe', '..disk_optimizer_tab', '..docker_tab', '..environment_tab', '..flutter_tab', '..gradle_tab', '..java_tab', '..main', '..mysqlfixer', '..nodejs_tab', '..python_tab', '..vram_tab', '..vscode_tab', '..wsl_tab', '..xampp_tab'],
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
    name='RunikDevOps',
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
    icon=['icon.ico'],
)
