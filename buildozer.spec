[app]

title = Tetris
package.name = tetris
package.domain = org.alphatetris
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = tests, bin, .git, .buildozer, .venv, __pycache__, .github, terminals
version = 1.0.0

# Kivy bootstrap is the most reliable path for pygame on p4a
requirements = python3,kivy,pygame,pyjnius,android,hostpython3,setuptools,cython==0.29.36

orientation = landscape
fullscreen = 1

android.api = 31
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.permissions = INTERNET
android.allow_backup = True
android.wakelock = True
android.accept_sdk_license = True
android.enable_androidx = True

[buildozer]

log_level = 2
warn_on_root = 0