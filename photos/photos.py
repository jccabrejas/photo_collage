import flet as ft

def handle_file_picker(e: ft.FilePickerResultEvent):
    
    if e.files:
        # selected_files_text.value = (
        #     " ; ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        # )
        # selected_files_text.update()
        text = (" ; ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!")
        print(text)
        return text
              


if "__name__" == "__main__":
    pass
