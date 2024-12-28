import base64
import flet as ft
import os
import yaml

from PIL import ImageGrab
from io import BytesIO
from time import localtime, strftime, sleep


def main(page: ft.Page):
    page.title = "Photo collage"
    page.window.width = 1400
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
    def drag_will_accept(e):
        e.control.content.border = ft.border.all(
            2, ft.Colors.BLACK45 if e.data == "true" else ft.Colors.RED
        )
        e.control.update()

    def drag_accept(e):
        # e.control => DragTarget
        # e.control.content => Container
        # e.control.content.content => Image
        src = e.control.page.get_control(e.src_id)
        e.control.content.content.src = src.content.src
        e.control.content.content = ft.InteractiveViewer(
            min_scale=0.1,
            max_scale=15,
            scale_factor=500,
            boundary_margin=ft.margin.all(20),
            content=ft.Image(src.content.src),
        )
        e.control.content.content.content.src_base64 = None  # needed because otherwise there is a clash with both src and src_base64
        e.control.update()

    def drag_accept_layout(e):
        # e.control => DragTarget
        # e.control.content => Container
        # e.control.content.content => Image
        src = e.control.page.get_control(e.src_id)
        e.control.content.content = src.data
        e.control.update()

    def drag_leave(e):
        e.control.content.border = ft.border.all(
            2, ft.Colors.WHITE if e.data == "true" else ft.Colors.RED
        )
        e.control.update()

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
        for _, v in data["layout"]["controls"].items():
            collage_item = ft.Container()
            collage_item.content = ft.DragTarget(
                group="photo",
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
                content=ft.Container(
                    content=ft.Image(
                        src_base64=data["layout"]["src_base64"],
                        fit=ft.ImageFit.FILL,
                    ),
                    width=v["width"],
                    height=v["height"],
                    border=ft.border.all(2, ft.Colors.WHITE),
                ),
            )
            collage_item.top = v["top"]
            collage_item.left = v["left"]
            result.append(collage_item)
        return ft.Stack(result, width=400, height=400)

    def refresh_layouts(_):
        layouts_work_area.controls = list()

        for filename in os.listdir(r".\assets\layouts"):
            if filename[-4:] != ".yml":
                continue
            with open(".\\assets\\layouts\\" + filename, "r") as file:
                data = yaml.safe_load(file)
            layouts_work_area.controls.append(
                ft.Draggable(
                    group="layout",
                    content=ft.Image(
                        src_base64=data["layout"]["src_base64"],
                        src=".\\assets\\layouts\\thumbnails\\" + filename[:-4] + ".png",
                        width=100,
                        height=100,
                        fit=ft.ImageFit.SCALE_DOWN,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        border_radius=ft.border_radius.all(10),
                    ),
                    data=load_layout(".\\assets\\layouts\\" + filename),
                )
            )
            layouts_work_area.controls.append(ft.Text(filename))

    layouts_work_area = ft.Column(
        controls=[],
        width=300,
        expand=False,
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

        for collage_item in (
            e.page.controls[0].controls[-1].content.content.content.controls
        ):
            photo = collage_item.content.content
            photo.border = ft.border.all(1, new_color)
            photo.update()

        e.page.controls[0].controls[-1].content.content.update()
        sleep(0.2)  # seconds

        # Define the region to capture (left, top, right, bottom)
        # TODO define this dynamically
        bbox = (
            page.window.left + 375,
            page.window.top + 63,
            page.window.left + 1075,
            page.window.top + 795,
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
        label="Grid Space", prefix_icon=ft.Icons.GRID_ON
    )


    new_layout_area_content = ft.Container(ft.Stack())

    def add_collage_area(e):
        new_layout_area_content.content.controls.append(
            ft.GestureDetector(
                drag_interval=10,
                top=10,
                left=10,
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_update=change_position,
                on_pan_end=adjust_to_grid,
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

    def save_layout(e):
        filename = ".\\assets\\layouts\\" + new_collage_name.value + ".yml"
        data = dict()
        data["layout"] = dict()
        data["layout"]["name"] = new_collage_name.value.replace(" ", "_")
        data["layout"]["tags"] = new_collage_tags.value.replace(" ", "").replace(
            ",,", ","
        )
        # Define the region to capture (left, top, right, bottom)
        bbox = (
            page.window.left + 350,
            page.window.top + 50,
            page.window.left + 750,
            page.window.top + 700,
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
        data["layout"]["controls"] = dict()
        for index, c in enumerate(new_layout_area_content.content.controls):
            data["layout"]["controls"][index] = dict()
            data["layout"]["controls"][index]["top"] = c.top
            data["layout"]["controls"][index]["left"] = c.left
            data["layout"]["controls"][index]["width"] = c.content.width
            data["layout"]["controls"][index]["height"] = c.content.height

        with open(filename, "w") as file:
            yaml.safe_dump(data, file)

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
                on_click=save_layout,
            ),
        ]
    )

    # Manage COLLAGE area

    layouts_init_content = ft.DragTarget(
        group="layout",
        content=ft.Container(
            bgcolor=ft.Colors.WHITE,
            width=400,
            height=400,
            border=ft.border.all(2, ft.Colors.WHITE),
        ),
        on_will_accept=drag_will_accept,
        on_accept=drag_accept_layout,
        on_leave=drag_leave,
    )

    def change_position(e: ft.DragUpdateEvent):
        e.control.top = max(0, e.control.top + e.delta_y)
        e.control.left = max(0, e.control.left + e.delta_x)
        e.control.update()
        page.update()

    def adjust_to_grid(e: ft.DragEndEvent):
        grid_space = int(grid_spacing.value)
        print(e.control.left)
        remainder_top = (e.control.top ) % grid_space
        remainder_left = (e.control.left ) % grid_space
        e.control.top = max(0, e.control.top - remainder_top)
        e.control.left = max(0, e.control.left - remainder_left)
        e.control.update()
        page.update()

    # Manage PAGE

    collage_area = ft.Container(
        content=layouts_init_content,
        expand=False,
        padding=30,
        width=page.window.width-350,
        height=page.window.height-200,
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
