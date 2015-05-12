# Capture
variable parameters in "path" and "filename":
    $browser, $date, $url, $random, $hash

# Compare
variable parameters in "save_as":
    $action_name, $date, $images, $random
variable parameters in "results":
    $date, $random

screen_size possible values:
    "fullscreen"
    [640, 960]
    [any_valid_width, any_valid_height]

To create templates for the input and config files, run 'obsidian.py --make-templates'

Database:
    config.json => "database_filename" == sqlite database to use
    input.json => "store_in_db": true/false == store the session's screenshots in the db
    database schema:
        autoincrementing uid
        url of the screenshot
        browser used
        date taken
        width of the screenshot
        height of the screenshot
        relative path of the screenshot image file

deps (maybe?):
    simplecv (hay que bajar el .deb)
    copiar las imagenes faltantes (Lena y el logo)
