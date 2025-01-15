import flet as ft
import yaml
import os
from pathlib import Path

from drag_handlers import *


def load_layout(filename: str) -> ft.Stack:
    """
    Load a layout from a YAML file.
    """
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
    result = list()
    min_top, max_top, min_left, max_left = 0, 0, 0, 0

    for _, v in data["layout"]["controls"].items():
        collage_item = ft.Container()
        collage_item.content = ft.DragTarget(
            group="photo",
            on_will_accept=drag_will_accept_photo,
            on_accept=drag_accept_photo,
            on_leave=drag_leave_photo,
            content=ft.Container(
                content=ft.Image(
                    src_base64=data["layout"]["src_base64"],
                    fit=ft.ImageFit.CONTAIN,
                ),
                width=v["width"],
                height=v["height"],
                border=ft.border.all(2, ft.Colors.BLUE),
            ),
        )
        collage_item.top = v["top"]
        collage_item.left = v["left"]
        result.append(collage_item)
        min_top = min(min_top, collage_item.top)
        max_top = max(max_top, collage_item.content.content.height)
        min_left = min(min_left, collage_item.left)
        max_left = max(max_left, collage_item.content.content.width)

    return ft.Stack(result, width=max_left - min_left + 0, height=max_top - min_top + 0)


def refresh_layouts(
    layouts_work_area: ft.Column, 
    layout_filter_dropdown: ft.Dropdown,
    work_area: ft.Container
):
    """
    Refresh the layouts work area based on the selected filter.
    """
    layouts_work_area.controls = list()
    layouts_work_area.controls.append(layout_filter_dropdown)
    filter_selection = {
        "All": 0,
        "2 Photos": 2,
        "3 Photos": 3,
        "4 Photos": 4,
        "> Photos": 5,
    }
    filter_value = filter_selection[layout_filter_dropdown.value]

    p = Path('./assets/layouts') 

    layouts = [x.name for x in Path('./assets/layouts').glob("*.yml")]
    for filename in layouts:
        with open(str(p / filename), "r") as file:
            data = yaml.safe_load(file)
        temp = ft.Draggable(
            group="layout",
            content=ft.Image(
                src_base64=data["layout"]["src_base64"],
                src=str(Path('./assets/layouts\thumbnails') / (filename[:-4] + ".png")),
                width=100,
                height=100,
                fit=ft.ImageFit.CONTAIN,
                repeat=ft.ImageRepeat.NO_REPEAT,
                border_radius=ft.border_radius.all(10),
            ),
            data=load_layout(str(p / filename)),
        )

        if layout_filter_dropdown.value == "All":
            layouts_work_area.controls.append(temp)
            layouts_work_area.controls.append(ft.Text(filename))
        elif layout_filter_dropdown.value == "> Photos":
            if len(data["layout"]["controls"].keys()) > 4:
                layouts_work_area.controls.append(temp)
                layouts_work_area.controls.append(ft.Text(filename))
        else:
            if len(data["layout"]["controls"].keys()) == filter_value:
                layouts_work_area.controls.append(temp)
                layouts_work_area.controls.append(ft.Text(filename))

    work_area.content = layouts_work_area
    work_area.update()

if __name__ == "__main__":
    pass