import flet as ft
import os
import yaml

from PIL import ImageGrab
from time import localtime, strftime, sleep

from custom_layout_manager import (
    save_layout,
    change_position,
    adjust_to_grid,
    make_not_visible,
)

from drag_handlers import (
    drag_will_accept_photo,
    drag_accept_photo,
    drag_leave_photo,
    drag_will_accept_layout,
    drag_accept_layout,
    drag_leave_layout,
)

def main(page: ft.Page):
    page.title = "Photo collage"
    page.window.width = 50 + 350 + 1400
    page.window.height = 1100
    page.padding = 0
    page.bgcolor = ft.Colors.GREY_600
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.ORANGE,
            background=ft.Colors.GREY_900,
            surface=ft.Colors.GREY_800,
        ),
    )
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Manage RAIL area
    def change_view(e):
        selected = e.control.selected_index
        if selected == 0:
            refresh_layouts("")
            work_area.content = layouts_work_area
            collage_area.content = layouts_init_content
            collage_area.update()
        elif selected == 1:
            work_area.content = photos_work_area
        elif selected == 2:
            work_area.content = background_work_area
        elif selected == 3:
            work_area.content = save_photo_work_area
        elif selected == 4:
            work_area.content = new_layout_work_content
            collage_area.content = new_layout_area_content
            collage_area.update()
        work_area.update()

    # Manage WORK area

    ## Manage photos work area

    def handle_file_picker(e: ft.FilePickerResultEvent):
        for i in e.files:
            photos_work_area.controls.append(
                ft.Draggable(
                    group="photo",
                    content=ft.Image(
                        src=i.path,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        border_radius=ft.border_radius.all(10),
                    ),
                )
            )
            photos_work_area.controls.append(ft.Text(value=i.name))
            photos_work_area.update()

    file_picker = ft.FilePicker(on_result=handle_file_picker)
    page.overlay.append(file_picker)
    photos_work_area = ft.Column(
        controls=[
            ft.FilledButton(
                text="Select photos",
                icon=ft.Icons.FOLDER_OPEN,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                on_click=lambda _: file_picker.pick_files(allow_multiple=True),
            ),
        ],
        width=300,
        expand=False,
        alignment=ft.MainAxisAlignment.START,
        scroll="always",
    )

    ## Manage layouts work area

    def load_layout(filename: str) -> ft.Stack:
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
            page.update()
            result.append(collage_item)
            min_top = min(min_top, collage_item.top)
            max_top = max(max_top, collage_item.content.content.height)
            min_left = min(min_left, collage_item.left)
            max_left = max(max_left, collage_item.content.content.width)

        return ft.Stack(
            result, width=max_left - min_left + 0, height=max_top - min_top + 0
        )

    def refresh_layouts(_):
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

        for filename in os.listdir(r".\assets\layouts"):
            if filename[-4:] != ".yml":
                continue
            with open(".\\assets\\layouts\\" + filename, "r") as file:
                data = yaml.safe_load(file)
            temp = ft.Draggable(
                group="layout",
                content=ft.Image(
                    src_base64=data["layout"]["src_base64"],
                    src=".\\assets\\layouts\\thumbnails\\" + filename[:-4] + ".png",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(10),
                ),
                data=load_layout(".\\assets\\layouts\\" + filename),
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

    def helper_refresh():
        refresh_layouts("")
        work_area.content = layouts_work_area
        work_area.update()
        collage_area.content = layouts_init_content
        collage_area.update()

    layout_filter_dropdown = ft.Dropdown(
        width=200,
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("2 Photos"),
            ft.dropdown.Option("3 Photos"),
            ft.dropdown.Option("4 Photos"),
            ft.dropdown.Option("> Photos"),
        ],
        value="All",
        on_change=lambda _: helper_refresh(),
    )

    layouts_work_area = ft.Column(
        controls=[],
        width=300,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        scroll="always",
    )

    refresh_layouts("")

    ## Manage Background work area

    def apply_color(e):
        if background_color_text.value.lower() in ft.Colors:
            layouts_init_content.content.bgcolor = background_color_text.value
        else:
            layouts_init_content.content.bgcolor = ft.Colors.WHITE
        layouts_init_content.update()

    background_color_text = ft.TextField(label="Color", prefix_icon=ft.Icons.COLOR_LENS)
    background_work_area = ft.Column(
        controls=[
            background_color_text,
            ft.FilledButton(
                text="Apply color",
                icon=ft.Icons.SAVE_OUTLINED,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                on_click=apply_color,
            ),
        ],
        width=300,
        expand=False,
        alignment=ft.MainAxisAlignment.START,
        scroll="always",
    )

    ## Manage Save Collage work area
    # TODO save image based on states, instead of using ImageGrab

    # collage_details = dict()
    # collage_details['width']
    # collage_details['height']
    # collage_details['bgcolor']
    # collage_details['items'] = list()
    # collage_details['items'][0] = dict()
    # collage_details['items'][0]['uid']
    # collage_details['items'][0]['src']
    # collage_details['items'][0]['top']
    # collage_details['items'][0]['left']

    def save_collage(e):
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
        temp = (
            ".\\output\\"
            + save_photo_filename_text.value.replace(" ", "_")
            + photo_extension_dropdown.value
        )
        image.save(temp)

    save_photo_filename_text = ft.TextField(
        label="File name",
        value="collage_" + strftime("%Y-%m-%d_%H%M%S", localtime()),
        prefix_icon=ft.Icons.DRIVE_FILE_MOVE,
    )

    photo_extension_dropdown = ft.Dropdown(
        width=200,
        options=[
            ft.dropdown.Option(".PNG"),
            ft.dropdown.Option(".JPG"),
            ft.dropdown.Option(".WebP"),
        ],
        value=".PNG",
    )
    save_photo_work_area = ft.Column(
        controls=[
            save_photo_filename_text,
            photo_extension_dropdown,
            ft.FilledButton(
                text="Save collage",
                icon=ft.Icons.SAVE_OUTLINED,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                on_click=save_collage,
            ),
        ],
        width=300,
        expand=False,
        alignment=ft.MainAxisAlignment.START,
        scroll="always",
    )

    ## Manage New Layout work area
    new_collage_width = ft.TextField(
        label="Width", prefix_icon=ft.Icons.WIDTH_NORMAL_SHARP
    )
    new_collage_height = ft.TextField(label="Height", prefix_icon=ft.Icons.HEIGHT)
    new_collage_name = ft.TextField(
        label="Name", prefix_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_SHARP
    )
    new_collage_tags = ft.TextField(label="Tags (comma sep)", prefix_icon=ft.Icons.TAG)
    grid_spacing = ft.TextField(
        value=10, label="Grid Space", prefix_icon=ft.Icons.GRID_ON
    )
    selected_top = ft.Text()
    selected_left = ft.Text()
    selected_width = ft.Text()
    selected_height = ft.Text()

    new_layout_area_content = ft.Container(ft.Stack())

    def add_collage_area(e):
        new_layout_area_content.content.controls.append(
            ft.GestureDetector(
                drag_interval=10,
                top=10,
                left=10,
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_update=lambda e: change_position(
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

    new_layout_work_content = ft.Column(
        controls=[
            new_collage_width,
            new_collage_height,
            ft.FilledButton(
                text="Create collage area",
                icon=ft.Icons.ADD_PHOTO_ALTERNATE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                on_click=add_collage_area,
            ),
            new_collage_name,
            new_collage_tags,
            grid_spacing,
            ft.FilledButton(
                text="Save layout",
                icon=ft.Icons.SAVE_OUTLINED,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                on_click=lambda e: save_layout(
                    page, new_collage_name, new_collage_tags, new_layout_area_content
                ),
            ),
            ft.Row(controls=[ft.Text("Top: "), selected_top]),
            ft.Row(controls=[ft.Text("Left: "), selected_left]),
            ft.Row(controls=[ft.Text("Width: "), selected_width]),
            ft.Row(controls=[ft.Text("Height: "), selected_height]),
        ]
    )

    # Manage COLLAGE area

    layouts_init_content = ft.DragTarget(
        group="layout",
        content=ft.Container(
            bgcolor=ft.Colors.WHITE,
            width=page.window.width - 350,
            height=page.window.height - 200,
            expand=False,
            border=ft.border.all(2, ft.Colors.WHITE),
        ),
        on_will_accept=drag_will_accept_layout,
        on_accept=drag_accept_layout,
        on_leave=drag_leave_layout,
    )

    # Manage PAGE

    collage_area = ft.Container(
        content=layouts_init_content,
        alignment=ft.alignment.top_center,
        padding=30,
        expand=False,
        width=page.window.width - 350,
        height=page.window.height - 200,
        bgcolor=ft.Colors.GREY_500,
        border=ft.border.all(2, ft.Colors.BLACK),
    )

    work_area = ft.Container(
        content=layouts_work_area,
        expand=False,
        padding=30,
        width=200,
        height=page.window.height,
        border=ft.border.all(2, ft.Colors.BLACK),
    )

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        width=100,
        min_width=100,
        min_extended_width=100,
        extended=False,
        group_alignment=-0.9,
        height=page.window.height,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.PAGES,
                selected_icon=ft.Icons.PAGES_OUTLINED,
                label="Layouts",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PHOTO_LIBRARY,
                selected_icon=ft.Icons.PHOTO_LIBRARY_OUTLINED,
                label="Photos",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.COLOR_LENS,
                selected_icon=ft.Icons.COLOR_LENS_OUTLINED,
                label="Background",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SAVE,
                selected_icon=ft.Icons.SAVE_OUTLINED,
                label="Save Collage",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BUILD,
                selected_icon=ft.Icons.BUILD_OUTLINED,
                label="New Layout",
            ),
        ],
        on_change=change_view,
        bgcolor=ft.Colors.GREY_900,
        expand=False,
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=5, thickness=3, color="white"),
                work_area,
                ft.VerticalDivider(width=5, thickness=3, color=ft.Colors.BLUE),
                collage_area,
            ],
            spacing=5,
            expand=False,
            alignment=ft.MainAxisAlignment.START,
        )
    )


ft.app(target=main)
