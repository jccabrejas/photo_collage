import base64
import flet as ft
import yaml
from PIL import ImageGrab
from io import BytesIO


def save_layout(page, new_collage_name, new_collage_tags, new_layout_area_content):
    filename = ".\\assets\\layouts\\" + new_collage_name.value + ".yml"
    data = dict()
    data["layout"] = dict()
    data["layout"]["name"] = new_collage_name.value.replace(" ", "_")
    data["layout"]["tags"] = new_collage_tags.value.replace(" ", "").replace(",,", ",")

    data["layout"]["controls"] = dict()
    min_top, max_top, min_left, max_left = 0, 0, 0, 0
    for index, c in enumerate(new_layout_area_content.content.controls):
        if c.visible:
            data["layout"]["controls"][index] = dict()
            data["layout"]["controls"][index]["top"] = c.top
            data["layout"]["controls"][index]["left"] = c.left
            data["layout"]["controls"][index]["width"] = c.content.width
            data["layout"]["controls"][index]["height"] = c.content.height

        min_top = min(min_top, c.top)
        max_top = max(max_top, c.top + c.content.height)
        min_left = min(min_left, c.left)
        max_left = max(max_left, c.left + c.content.width)

    # Define the region to capture (left, top, right, bottom)
    bbox = (
        page.window.left + 360 + min_left,
        page.window.top + 150 + min_top,
        page.window.left + 380 + max_left,
        page.window.top + 170 + max_top,
    )

    image = ImageGrab.grab(bbox)
    temp = (
        ".\\assets\\layouts\\thumbnails\\"
        + new_collage_name.value.replace(" ", "_")
        + ".png"
    )
    image.save(temp)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data["layout"]["src"] = temp
    data["layout"]["src_base64"] = img_str
    with open(filename, "w") as file:
        yaml.safe_dump(data, file)


def change_position(
    e: ft.DragUpdateEvent,
    selected_top,
    selected_left,
    selected_width,
    selected_height,
    page,
):
    if abs(e.control.content.width - e.local_x) < 10:
        e.control.content.width = max(0, e.local_x)
    elif abs(e.control.content.height - e.local_y) < 10:
        e.control.content.height = max(0, e.local_y)
    else:
        e.control.top = max(0, e.control.top + e.delta_y)
        e.control.left = max(0, e.control.left + e.delta_x)
    print(e.control.content.width, e.control.content.height)
    selected_top.value = e.control.top
    selected_left.value = e.control.left
    selected_width.value = e.control.content.width
    selected_height.value = e.control.content.height
    e.control.content.update()
    e.control.update()
    page.update()


def adjust_to_grid(
    e: ft.DragEndEvent,
    grid_spacing,
    selected_top,
    selected_left,
    selected_width,
    selected_height,
    page,
):
    grid_space = int(grid_spacing.value)
    remainder_top = (e.control.top) % grid_space
    remainder_left = (e.control.left) % grid_space
    e.control.top = max(0, e.control.top - remainder_top)
    e.control.left = max(0, e.control.left - remainder_left)
    selected_top.value = e.control.top
    selected_left.value = e.control.left
    selected_width.value = e.control.content.width
    selected_height.value = e.control.content.height
    e.control.update()
    page.update()


def make_not_visible(e):
    e.control.visible = False
    e.control.update()