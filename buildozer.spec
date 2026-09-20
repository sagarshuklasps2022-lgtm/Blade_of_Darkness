[app]

title = Blade of Darkness
package.name = bladeofdarkness
package.domain = org.sagar
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3==3.11.9,pygame==2.5.2,sdl2_image,sdl2_mixer,sdl2_ttf,sdl2
orientation = landscape
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
