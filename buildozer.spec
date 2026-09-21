[app]

# (str) Title of your application
title = Blade of Darkness

# (str) Package name
package.name = bladeofdarkness

# (str) Package domain (needed for android packaging)
package.domain = org.sagar.ninja

# (str) Source files to include (let it include python and assets)
source.include_exts = py,png,jpg,mp3

# (list) Source files to include
source.include_patterns = images/*,sounds/*,*.png,*.jpg,*.mp3

# (list) Application requirements
requirements = python3,pygame,sdl2_image,sdl2_mixer,sdl2_ttf,sdl2

# (str) Supported orientations (landscape is best for this platformer game)
orientation = landscape

# (list) Permissions
android.permissions = INTERNET

# (int) Target API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (bool) Indicate whether the application is a game or not
android.add_package_data = True
