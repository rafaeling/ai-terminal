# main.py
import flet as ft
from views.app_view import AppView # Import the main view manager


def main(page: ft.Page):
    #page.title = "AI Termdinal"
    #page.window.title_bar_hidden = True
    #page.window.title_bar_buttons_hidden = True

    # page.add(
    #     ft.Row(
    #         [
    #             ft.WindowDragArea(ft.Container(ft.ElevatedButton("AI Terminal"), bgcolor=ft.Colors.GREY_900, padding=15), expand=True),
    #             ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: page.window.close())
    #         ]
    #     )
    # )
    page.window.center()
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK # Set theme preference
    page.padding = ft.padding.all(15) # Add some overall padding
    page.window_min_width = 600
    page.window_min_height = 500
    page.window.bgcolor = ft.Colors.BLACK
    

    # Create instance of the main view manager
    notebook_manager = AppView(page)

    # Build the initial UI elements from the view manager
    page_controls = notebook_manager.build()

    # Add the main controls returned by the view manager to the page
    page.add(*page_controls)

    # Add the first initial cell using the view manager's method
    notebook_manager.add_chat_box_cell_click(None)
    notebook_manager.add_cell_click("ls asdf", None)
    
    page.update() # Ensure initial state is rendered


# --- Application Runner ---
if __name__ == "__main__":
    ft.app(target=main)
    # Or for web:
    # ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)