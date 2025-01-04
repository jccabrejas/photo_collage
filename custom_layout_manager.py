import base64
import flet as ft
import yaml
from PIL import ImageGrab
from io import BytesIO
import keyboard

def save_layout(page: ft.Page,
                new_collage_name: ft.TextField,
                new_collage_tags: ft.TextField,
                new_layout_area_content: ft.Container):
    """
    Save the current layout to a YAML file and create a thumbnail image.
    """
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


def change_position_and_size(
    e: ft.DragUpdateEvent,
    selected_top: ft.Text,
    selected_left: ft.Text,
    selected_width: ft.Text,
    selected_height: ft.Text,
    page: ft.Page,
):
    """
    Change the position of a draggable item.
    If you click close to left and bottom borders, resize the item.
    """
    if abs(e.control.content.width - e.local_x) < 10 and keyboard.is_pressed("ctrl"):
        e.control.content.width = max(0, e.local_x)
    elif abs(e.control.content.height - e.local_y) < 10 and keyboard.is_pressed("ctrl"):
        e.control.content.height = max(0, e.local_y)
    elif not keyboard.is_pressed("ctrl"):
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
    grid_spacing : ft.TextField,
    selected_top: ft.Text,
    selected_left: ft.Text,
    selected_width: ft.Text,
    selected_height: ft.Text,
    page: ft.Page,
):
    """
    Adjust the position of a draggable item to a grid
    and feed back position (top & left) and size (width & height).
    """
    grid_space = max(1, int(grid_spacing.value))
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


def add_collage_area(
    e,
    page,
    new_layout_area_content,
    new_collage_width,
    new_collage_height,
    grid_spacing,
    selected_top,
    selected_left,
    selected_width,
    selected_height,
):
    """
    Add a new collage area to the layout.
    """
    new_layout_area_content.content.controls.append(
        ft.GestureDetector(
            drag_interval=10,
            top=10,
            left=10,
            mouse_cursor=ft.MouseCursor.MOVE,
            on_pan_update=lambda e: change_position_and_size(
                e,
                selected_top,
                selected_left,
                selected_width,
                selected_height,
                page,
            ),
            on_pan_end=lambda e: adjust_to_grid(
                e,
                grid_spacing,
                selected_top,
                selected_left,
                selected_width,
                selected_height,
                page,
            ),
            on_secondary_tap=make_not_visible,
            content=ft.Container(
                border=ft.border.all(5, "white"),
                width=(
                    int(new_collage_width.value)
                    if new_collage_width.value != ""
                    else 100
                ),
                height=(
                    int(new_collage_height.value)
                    if new_collage_height.value != ""
                    else 100
                ),
                visible=True,
            ),
        )
    )
    new_layout_area_content.update()
    page.update()
