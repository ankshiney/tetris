[app]

title = Tetris
package.name = tetris
package.domain = org.alphatetris
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = tests, bin, .git, .buildozer, .venv, __pycache__, .github, terminals
version = 1.0.0

# Python 3.10 + pinned deps avoid pyjnius/Cython breakage on 3.11+
requirements = python3==3.10.12,pygame,pyjnius==1.6.1,android,hostpython3==3.10.12,setuptools,cython==0.29.36

orientation = landscape
fullscreen = 1

p4a.bootstrap = sdl2

android.api = 31
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.permissions = INTERNET
android.allow_backup = True
android.wakelock = True
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 0