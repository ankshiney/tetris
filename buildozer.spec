[app]

title = Tetris
package.name = tetris
package.domain = org.alphatetris
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = tests, bin, .git, .buildozer, .venv, __pycache__, .github, terminals
version = 1.0.0

requirements = python3==3.11.9,pygame==2.6.1,hostpython3,setuptools,cython==0.29.36,android,pyjnius

orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/assets/images/logo_glow.png
presplash.filename = %(source.dir)s/assets/images/menu_bg.png

android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET
android.allow_backup = True
android.wakelock = True
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = "@android:style/Theme.NoTitleBar.Fullscreen"
android.gradle_dependencies =

[buildozer]

log_level = 2
warn_on_root = 1