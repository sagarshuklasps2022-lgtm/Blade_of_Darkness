[app]

# Application title
title = Blade of Darkness

# Package identifier
package.name = bladeofdarkness
package.domain = org.sagar

# Application source
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,ogg,wav,mp3

# Application version
version = 0.1

# Python and library dependencies
requirements = python3,pygame==2.5.2,sdl2_image,sdl2_mixer,sdl2_ttf

# Display settings
orientation = landscape
fullscreen = 0

# Android settings
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

# Use the tagged python-for-android release.
# The "v" prefix is required because this is a release tag.
p4a.url = https://github.com/kivy/python-for-android.git
p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
