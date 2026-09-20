[app]
title = Blade of Darkness
package.name = bladeofdarkness
package.domain = org.sagar

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,ogg,wav,mp3

version = 0.1

requirements = python3,pygame==2.5.2,sdl2_image,sdl2_mixer,sdl2_ttf

orientation = landscape
fullscreen = 0

android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

# Pin python-for-android to a release whose host and target
# Python recipes are from the same Python generation.
p4a.url = https://github.com/kivy/python-for-android.git
p4a.branch = 2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
