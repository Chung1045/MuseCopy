# -*- mode: python ; coding: utf-8 -*-
import os
import re
import subprocess
import sys
from PyInstaller.utils.hooks import copy_metadata

pkg_metadata = copy_metadata("PyQt5") + copy_metadata("tinytag") + copy_metadata("mutagen")

def _detect_version():
    v = os.environ.get("APP_VERSION", "")
    if not v:
        try:
            v = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL, text=True,
            ).strip()
        except Exception:
            v = ""
    m = re.match(r"v?(\d+(?:\.\d+)*)", v)
    return m.group(1) if m else "0.0.0"

app_version = _detect_version()
version_info = None

if sys.platform == "win32":
    from PyInstaller.utils.win32.versioninfo import (
        VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable,
        StringStruct, VarFileInfo, VarStruct,
    )
    nums = tuple((list(map(int, app_version.split("."))) + [0] * 4)[:4])
    version_info = VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=nums, prodvers=nums,
            mask=0x3f, flags=0x0, OS=0x40004,
            fileType=0x1, subtype=0x0, date=(0, 0),
        ),
        kids=[
            StringFileInfo([StringTable("040904B0", [
                StringStruct("CompanyName", "Chung1045"),
                StringStruct("FileDescription", "Muse Copy"),
                StringStruct("FileVersion", app_version),
                StringStruct("InternalName", "MuseCopy"),
                StringStruct("OriginalFilename", "MuseCopy.exe"),
                StringStruct("ProductName", "Muse Copy"),
                StringStruct("ProductVersion", app_version),
            ])]),
            VarFileInfo([VarStruct("Translation", [1033, 1200])]),
        ],
    )

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=pkg_metadata,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    noarchive=False,
    optimize=0,
    excludes=[
        "tkinter",
        "PyQt5.QtNetwork", "PyQt5.QtQml", "PyQt5.QtQuick", "PyQt5.QtQuickWidgets",
        "PyQt5.QtSvg", "PyQt5.QtSql", "PyQt5.QtTest", "PyQt5.QtMultimedia",
        "PyQt5.QtMultimediaWidgets", "PyQt5.QtPrintSupport", "PyQt5.QtBluetooth",
        "PyQt5.QtWebChannel", "PyQt5.QtWebSockets", "PyQt5.QtPositioning",
        "PyQt5.QtSensors", "PyQt5.QtDesigner", "PyQt5.QtHelp", "PyQt5.QtXml",
    ],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MuseCopy',
    version=version_info,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MuseCopy',
)
app = BUNDLE(
    coll,
    name='MuseCopy.app',
    icon=None,
    bundle_identifier='com.chung1045.musecopy',
    version=app_version,
    info_plist={
        'CFBundleShortVersionString': app_version,
        'CFBundleVersion': app_version,
    },
)
