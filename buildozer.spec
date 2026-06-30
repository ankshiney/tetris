[app]

title = Tetris
package.name = tetris
package.domain = org.alphatetris
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = tests, bin, .git, .buildozer, .venv, __pycache__, .github, terminals
version = 1.0.0

requirements = python3,pygame,hostpython3,setuptools,cython==0.29.36,android,pyjnius

orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/assets/images/logo_glow.png
presplash.filename = %(source.dir)s/assets/images/menu_bg.png

p4a.bootstrap = sdl2

android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.permissions = INTERNET
android.allow_backup = True
android.wakelock = True
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = "@android:style/Theme.NoTitleBar.Fullscreen"

[buildozer]

log_level = 2
warn_on_root = 0