"""Theme and stylesheet helpers for the PieMenu workbench.

Reads the selected theme's QSS file and substitutes the FreeCAD accent
colors so the PieMenu matches the current FreeCAD colour theme.
"""

import os

from piemenu import config, constants, resources


def get_css_color(user_parameter, key):
    """Return a FreeCAD color parameter as an RGB hex string."""
    color = user_parameter.GetUnsigned(key)
    hex_color = hex(color)[2:].zfill(8)
    rgb_hex_color = hex_color[:6]
    return f"#{rgb_hex_color}"


def get_style():
    """Return the QSS stylesheet of the currently selected theme."""
    theme = config.get_params()["main"].GetString(constants.PARAM_THEME)
    if theme == "":
        theme = "Legacy"  # default theme if new installation
    stylesheet_path = f"{os.path.join(resources.stylepath, theme)}.qss"
    if not os.path.exists(stylesheet_path):
        stylesheet_path = f"{os.path.join(resources.stylepath, 'Legacy.qss')}"
        config.get_params()["main"].SetString(constants.PARAM_THEME, "Legacy")

    with open(stylesheet_path, "r") as f:
        style_current_theme = f.read()
    qss_path = resources.stylepath + "\\"
    style_current_theme = style_current_theme.replace(
        "pieMenuQss:", qss_path.replace("\\", "/"))

    # Get FreeCAD ThemeAccentColors
    theme_accent_color1_hex = get_css_color(
        config.get_params()["accents"], "ThemeAccentColor1")
    theme_accent_color2_hex = get_css_color(
        config.get_params()["accents"], "ThemeAccentColor2")
    theme_accent_color3_hex = get_css_color(
        config.get_params()["accents"], "ThemeAccentColor3")
    style_current_theme = style_current_theme.replace(
        "@ThemeAccentColor1", str(theme_accent_color1_hex))
    style_current_theme = style_current_theme.replace(
        "@ThemeAccentColor2", str(theme_accent_color2_hex))
    style_current_theme = style_current_theme.replace(
        "@ThemeAccentColor3", str(theme_accent_color3_hex))
    return style_current_theme
