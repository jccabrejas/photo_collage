import flet as ft

from PIL import ImageGrab
from time import localtime, strftime, sleep

from custom_layout_manager import save_layout, add_collage_area
from layout_loader_manager import load_layout, refresh_layouts, helper_refresh
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
        """
        Change the view based on the selected index in the navigation rail.
        """
        selected = e.control.selected_index
        if selected == 0:
            refresh_layouts("", page, layouts_work_area, layout_filter_dropdown)
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
        """
        Handle the file picker result event.
        """
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
        on_change=lambda _: helper_refresh(
            page,
            layouts_work_area,
            layout_filter_dropdown,
            work_area,
            collage_area,
            layouts_init_content,
        ),
    )

    layouts_work_area = ft.Column(
        controls=[],
        width=300,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        scroll="always",
    )

    refresh_layouts("", page, layouts_work_area, layout_filter_dropdown)

    ## Manage Background work area

    def apply_color(e):
        """
        Apply the selected color to the background.
        """
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

    new_layout_work_content = ft.Column(
        controls=[
            new_collage_width,
            new_collage_height,
            ft.FilledButton(
                text="Create collage area",
                icon=ft.Icons.ADD_PHOTO_ALTERNATE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                on_click=lambda e: add_collage_area(
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
                ),
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

    # Manage PAGE

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
