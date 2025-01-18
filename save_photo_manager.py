import flet as ft
from time import sleep
from PIL import ImageGrab
from pathlib import Path

# TODO save image based on states, instead of using ImageGrab

def save_collage(e, page, save_photo_filename_text, photo_extension_dropdown):
    new_color = e.page.controls[0].controls[-1].content.content.bgcolor
    e.page.controls[0].controls[-1].content.content.border = ft.border.all(
        1, new_color
    )
    min_top, max_top, min_left, max_left = 0, 0, 0, 0

    for collage_item in (
        e.page.controls[0].controls[-1].content.content.content.controls
    ):
        photo = collage_item.content.content
        photo.border = ft.border.all(1, new_color)
        photo.update()

        min_top = min(min_top, collage_item.top)
        max_top = max(
            max_top, collage_item.top + collage_item.content.content.height
        )
        min_left = min(min_left, collage_item.left)
        max_left = max(
            max_left, collage_item.left + collage_item.content.content.width
        )

    e.page.controls[0].controls[-1].content.content.update()
    sleep(0.2)  # seconds

    # Define the region to capture (left, top, right, bottom)
    # TODO define this dynamically
    bbox = (
        page.window.left + 370 + min_left,
        page.window.top + 165 + min_top,
        page.window.left + 380 + max_left,
        page.window.top + 170 + max_top,
    )

    image = ImageGrab.grab(bbox)
    temp = str(Path('./output')
        / save_photo_filename_text.value.replace(" ", "_")
        / photo_extension_dropdown.value
    )
    image.save(temp)
