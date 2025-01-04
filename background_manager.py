import flet as ft

def apply_color(background_color_text, layouts_init_content):
    """
    Apply the selected color to the background.
    """
    if background_color_text.value.lower() in ft.Colors:
        layouts_init_content.content.bgcolor = background_color_text.value
    else:
        layouts_init_content.content.bgcolor = ft.Colors.WHITE
    layouts_init_content.update()
