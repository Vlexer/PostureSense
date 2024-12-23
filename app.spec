# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('__pycache__/*', '__pycache__'), ('auth.py', '.'), ('client_secrets.json', '.'), ('eye-icon.jpg', '.'), ('login.py', '.'), ('notify.mp3', '.'), ('person-workin.webp', '.'), ('posture.png', '.'), ('posture_detection.py', '.'), ('user_data.json', '.'), ('background.jpg', '.'), ('correct.JPG', '.'), ('index.html', '.'), ('main.py', '.'), ('person.avif', '.'), ('posture.jpg', '.'), ('posture_data.csv', '.'), ('requirement.txt', '.'), ('utils.py', '.')],
    hiddenimports=[],
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
    name='app',
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
)
