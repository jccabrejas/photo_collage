import flet as ft

def drag_will_accept_photo(e):
    e.control.content.border = ft.border.all(
        2, ft.Colors.BLACK45 if e.data == "true" else ft.Colors.RED
    )
    e.control.update()

def drag_accept_photo(e):
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

def drag_leave_photo(e):
    e.control.content.border = ft.border.all(
        2, ft.Colors.WHITE if e.data == "true" else ft.Colors.RED
    )
    e.control.update()

def drag_will_accept_layout(e):
    e.control.content.border = ft.border.all(
        2, ft.Colors.BLACK45 if e.data == "true" else ft.Colors.RED
    )
    e.control.update()

def drag_accept_layout(e):
    # e.control => DragTarget
    # e.control.content => Container
    # e.control.content.content => Image
    src = e.control.page.get_control(e.src_id)
    e.control.content.content = src.data
    e.control.update()

def drag_leave_layout(e):
    e.control.content.border = ft.border.all(
        2, ft.Colors.WHITE if e.data == "true" else ft.Colors.RED
    )
    e.control.update()
