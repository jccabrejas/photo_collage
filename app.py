import base64
import flet as ft
import yaml

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

    # Manage RAIL area
    def change_view(e):
        selected = e.control.selected_index
        if selected == 0:
            work_area.content = layouts_work_area
            collage_area.content = layouts_init_content
            collage_area.update()
        elif selected == 1:
            work_area.content = photos_work_area
        elif selected == 2:
            work_area.content = ft.Text("Background", size=24)
        elif selected == 3:
            work_area.content = ft.Text("Save collage", size=24)
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
    layouts_work_area = ft.Column(
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

    ## Manage Background work area

    ## Manage Save Collage work area

    ## Manage New Layout work area
    new_collage_width = ft.TextField(
        label="Width", prefix_icon=ft.Icons.WIDTH_NORMAL_SHARP
    )
    new_collage_height = ft.TextField(label="Height", prefix_icon=ft.Icons.HEIGHT)
    new_collage_name = ft.TextField(
        label="Name", prefix_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_SHARP
    )
    new_collage_tags = ft.TextField(label="Tags (comma sep)", prefix_icon=ft.Icons.TAG)

    new_layout_area_content = ft.Container(ft.Stack())

    def add_collage_area(e):
        new_layout_area_content.content.controls.append(
            ft.GestureDetector(
                drag_interval=10,
                top=10,
                left=10,
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_update=change_position,
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
        filename= '.\\assets\\layouts\\' + new_collage_name.value + '.yml'
        data = dict()
        data['layout']=dict()
        data['layout']['name'] = new_collage_name.value.replace(' ','_')
        data['layout']['tags'] = new_collage_tags.value.replace(' ','').replace(',,',',')
        data['layout']['src'] = 'to be done' # TODO screenshot the collage, convert to base64 and store here to be used as thumbnail
        data['layout']['controls'] = dict()
        for index, c in enumerate(new_layout_area_content.content.controls):
            data['layout']['controls'][index] = dict()
            data['layout']['controls'][index]['top'] = c.top
            data['layout']['controls'][index]['left'] = c.left
            data['layout']['controls'][index]['width'] = c.content.width
            data['layout']['controls'][index]['height'] = c.content.height

        with open(filename, 'w') as file:
            yaml.safe_dump(data, file)

    def load_layout(filename: str) -> ft.Stack:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
        result = list()
        for _, v in data['layout']['controls'].items():
            collage_item = ft.Container()
            collage_item.content = ft.DragTarget(
                group='photo',
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
                content = ft.Container(
                    content=ft.Image(
                        src=r".\assets\placeholder.png",
                        fit=ft.ImageFit.NONE,
                    ),
                    width=v['width'],
                    height=v['height'],
                    border=ft.border.all(2, ft.Colors.WHITE),
                    ),
                )
            collage_item.top=v['top']
            collage_item.left=v['left']
            result.append(collage_item)
        return ft.Stack(result, width=400, height=400)

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

    ## Manage Layouts and Photos collage areaa
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
        e.control.content.content.offset = ft.transform.Offset(
            0, 0
        )  # TODO clean up if not required
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

    def edit_photo(e):
        pass

    space_between_photos = 10
    layout_library = []
    layout_00_content = load_layout(r'.\assets\layouts\test.yml')
    # layout_00_content = ft.Stack(
    #     [
    #         ft.Container(
    #             content=ft.DragTarget(
    #                 group="photo",
    #                 content=ft.Container(
    #                     content=ft.Image(
    #                         src=r".\assets\placeholder.png",
    #                         fit=ft.ImageFit.NONE,
    #                     ),
    #                     width=150,
    #                     height=150,
    #                     border=ft.border.all(2, ft.Colors.WHITE),
    #                 ),
    #                 on_will_accept=drag_will_accept,
    #                 on_accept=drag_accept,
    #                 on_leave=drag_leave,
    #             ),
    #             left=0,
    #             top=0,
    #             on_click=edit_photo,
    #         ),
    #         ft.Container(
    #             content=ft.DragTarget(
    #                 group="photo",
    #                 content=ft.Container(
    #                     content=ft.Image(
    #                         src=r".\assets\placeholder.png",
    #                         fit=ft.ImageFit.NONE,
    #                     ),
    #                     border=ft.border.all(2, ft.Colors.WHITE),
    #                     width=150,
    #                     height=150,
    #                 ),
    #                 on_will_accept=drag_will_accept,
    #                 on_accept=drag_accept,
    #                 on_leave=drag_leave,
    #             ),
    #             left=150 + space_between_photos,
    #             top=0,
    #         ),
    #         ft.Container(
    #             content=ft.DragTarget(
    #                 group="photo",
    #                 content=ft.Container(
    #                     content=ft.Image(
    #                         src=r".\assets\placeholder.png",
    #                         fit=ft.ImageFit.NONE,
    #                     ),
    #                     border=ft.border.all(2, ft.Colors.WHITE),
    #                     width=150,
    #                     height=300,
    #                 ),
    #                 on_will_accept=drag_will_accept,
    #                 on_accept=drag_accept,
    #                 on_leave=drag_leave,
    #             ),
    #             left=0,
    #             top=150 + space_between_photos,
    #         ),
    #         ft.Container(
    #             content=ft.DragTarget(
    #                 group="photo",
    #                 content=ft.Container(
    #                     content=ft.Image(
    #                         src=r".\assets\placeholder.png",
    #                         fit=ft.ImageFit.NONE,
    #                     ),
    #                     border=ft.border.all(2, ft.Colors.WHITE),
    #                     width=150,
    #                     height=150,
    #                 ),
    #                 on_will_accept=drag_will_accept,
    #                 on_accept=drag_accept,
    #                 on_leave=drag_leave,
    #             ),
    #             left=150 + space_between_photos,
    #             top=225 + space_between_photos,
    #         ),
    #         ft.Container(
    #             content=ft.DragTarget(
    #                 group="photo",
    #                 content=ft.Container(
    #                     content=ft.Image(
    #                         src=r".\assets\placeholder.png",
    #                         fit=ft.ImageFit.NONE,
    #                     ),
    #                     border=ft.border.all(2, ft.Colors.WHITE),
    #                     width=300 + space_between_photos,
    #                     height=150,
    #                 ),
    #                 on_will_accept=drag_will_accept,
    #                 on_accept=drag_accept,
    #                 on_leave=drag_leave,
    #             ),
    #             left=0,
    #             top=450 + 2 * space_between_photos,
    #         ),
    #     ],
    #     width=400,
    #     height=400,
    # )
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

    ## Manage New Layout collage area

    def change_position(e: ft.DragUpdateEvent):
        e.control.top = max(0, e.control.top + e.delta_y)
        e.control.left = max(0, e.control.left + e.delta_x)
        page.update()

    # Manage PAGE

    collage_area = ft.Container(
        content=layouts_init_content,
        expand=False,
        padding=30,
        width=400,
        height=page.window.height,
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
