import flet as ft


def main(page: ft.Page):
    page.title = "Photo collage"
    page.window.width = 800
    page.window.height = 800
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

    def change_view(e):
        selected = e.control.selected_index
        if selected == 0:
            work_area.content = photos_area
            content_area.update()
        elif selected == 1:
            work_area.content = layouts_area
            # content_area.content = None
            # content_area.update()
        elif selected == 2:
            work_area.content = ft.Text("New layout", size=24)
        elif selected == 3:
            work_area.content = ft.Text("Save collage", size=24)
        elif selected == 4:
            work_area.content = ft.Text("Background", size=24)
        work_area.update()

    def handle_file_picker(e: ft.FilePickerResultEvent):

        for i in e.files:
            photos_area.controls.append(
                ft.Draggable(
                    group="photo",
                    content=ft.Image(
                        src=i.path,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.SCALE_DOWN,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        border_radius=ft.border_radius.all(10),
                    ),
                )
            )
            photos_area.controls.append(ft.Text(value=i.name))
            photos_area.update()

    file_picker = ft.FilePicker(on_result=handle_file_picker)
    page.overlay.append(file_picker)

    photos_area = ft.Column(
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

    layouts_area = ft.Column(
        controls=[
            ft.Draggable(
                group="layout",
                content=ft.Image(
                    src=r".\assets\layout_01_image.png",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.SCALE_DOWN,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(10),
                ),
            ),
        ],
        width=300,
        expand=False,
        alignment=ft.MainAxisAlignment.START,
        scroll="always",
    )

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
        e.control.update()

    def drag_accept_layout(e):
        # e.control => DragTarget
        # e.control.content => Container
        # e.control.content.content => Image
        # src = e.control.page.get_control(e.src_id)
        e.control.content.content = layout_00_content
        e.control.update()

    def drag_leave(e):
        e.control.content.border = ft.border.all(
            2, ft.Colors.WHITE if e.data == "true" else ft.Colors.RED
        )
        e.control.update()

    space_between_photos = 10
    layout_00_content=ft.Stack(
        [ft.Container(
            content=ft.DragTarget(
                group="photo",
                content=ft.Container(
                    content=ft.Image(
                        src=r".\assets\placeholder.png",
                    ),
                width=150,
                height=150,
                border = ft.border.all(2, ft.Colors.WHITE),
                ),
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
            ),
        left=0,
        top=0,
        ),
        ft.Container(
            content=ft.DragTarget(
                group="photo",
                content=ft.Container(
                    content=ft.Image(
                        src=r".\assets\placeholder.png",
                    ),
                    border = ft.border.all(2, ft.Colors.WHITE),
                    width=150,
                    height=150,
                    ),
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
            ),
        left=150+space_between_photos,
        top=0
        ),
        ft.Container(
            content=ft.DragTarget(
                group="photo",
                content=ft.Container(
                    content=ft.Image(
                        src=r".\assets\placeholder.png",
                    ),
                    border = ft.border.all(2, ft.Colors.WHITE),
                    width=150,
                    height=300,
                    ),
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
            ),
        left=0,
        top=150 +space_between_photos,
        ),
        ft.Container(
            content=ft.DragTarget(
                group="photo",
                content=ft.Container(
                    content=ft.Image(
                        src=r".\assets\placeholder.png",
                    ),
                    border = ft.border.all(2, ft.Colors.WHITE),
                    width=150,
                    height=150,
                    ),
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
            ),
        left=150+space_between_photos,
        top=225+space_between_photos
        ),
        ft.Container(
            content=ft.DragTarget(
                group="photo",
                content=ft.Container(
                    content=ft.Image(
                        src=r".\assets\placeholder.png",
                    ),
                    border = ft.border.all(2, ft.Colors.WHITE),
                    width=300+space_between_photos,
                    height=150,
                    ),
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
            ),
        left=0,
        top=450 + 2* space_between_photos),
        ],
        width=400,
        height=400,
        )

    content_area = ft.Container(
        content=ft.DragTarget(
            group="layout",
            content=ft.Container(
                content=ft.Image(
                    src=r".\assets\placeholder.png",
                ),
            width=400,
            height=400,
            border = ft.border.all(2, ft.Colors.WHITE),
            ),
            on_will_accept=drag_will_accept,
            on_accept=drag_accept_layout,
            on_leave=drag_leave,
        ),
        expand=False,
        padding=30,
        width=400,
        height=page.window.height,
        bgcolor=ft.Colors.GREY_500,
        border = ft.border.all(2, ft.Colors.BLACK),
    )

    work_area = ft.Container(
        content=ft.Text("work area text", size=24),
        expand=False,
        padding=30,
        width=200,
        height=page.window.height,
        border = ft.border.all(2, ft.Colors.BLACK),
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
                icon=ft.Icons.PHOTO_LIBRARY,
                selected_icon=ft.Icons.PHOTO_LIBRARY_OUTLINED,
                label="Photos",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PAGES,
                selected_icon=ft.Icons.PAGES_OUTLINED,
                label="Layouts",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BUILD,
                selected_icon=ft.Icons.BUILD_OUTLINED,
                label="New Layout",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SAVE,
                selected_icon=ft.Icons.SAVE_OUTLINED,
                label="Save Collage",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.COLOR_LENS,
                selected_icon=ft.Icons.COLOR_LENS_OUTLINED,
                label="Background",
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
                content_area,
            ],
            spacing=5,
            expand=False,
            alignment=ft.MainAxisAlignment.START,
        )
    )


ft.app(main)
