# components/command_cell.py
import flet as ft
import threading
from typing import Callable
from services.command_runner import run_command_thread # Import the runner function
from services.llm_model_sdks.gemini.gemini_client import GeminiClient

class ChatBoxCell:
    """Represents a single interactive ChatBox cell in the notebook."""

    def __init__(self, page: ft.Page, update_response: Callable[['str'], None]):
        """
        Initializes a ChatBox.

        Args:
            page (ft.Page): The Flet Page object.
            update_response (Callable): A function to call when this cell's
                                       delete button is clicked. It receives the
                                       ChatBox instance itself as an argument.
        """
        self.page = page
        self.update_response = update_response
        self.gemini_client = GeminiClient()

        # --- Flet Controls for the Cell ---
        self.command_input = ft.TextField(
            hint_text="What would you like to execute: ",
            multiline=False,
            expand=True,
            border_color=ft.colors.with_opacity(0.8, ft.colors.OUTLINE),
            focused_border_color=ft.colors.PRIMARY,
            border_radius=ft.border_radius.all(40),
            cursor_color=ft.colors.PRIMARY,
            # text_style=ft.TextStyle(font_family="monospace"), # Requires font setup
            on_submit=self.run_command_click # Allow running with Enter key
        )

        self.run_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW_ROUNDED,
            tooltip="Send request",
            on_click=self.run_command_click,
            icon_color=ft.colors.GREEN_ACCENT_400,
        )
        
        self.output_text = ft.Text(
            "[Output will appear here]",
            selectable=True,
            # style=ft.TextStyle(font_family="monospace"), # Requires font setup
        )

        self.output_container = ft.Container(
             content=self.output_text,
             padding=ft.padding.all(10),
             bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
             border_radius=ft.border_radius.all(10),
             margin=ft.margin.only(top=5),
             visible=False # Initially hidden until first run
        )

        # --- Main Layout for this Cell ---
        self.view = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.command_input,
                            self.run_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    self.output_container,
                ]
            ),
            padding=10,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.with_opacity(0.2, ft.colors.OUTLINE))),
        )

    def send_request(self, request):
        return self.gemini_client.send_request(request)
        
    def run_command_click(self, e: ft.ControlEvent):
        """Handles the click event for the run button or Enter key in TextField."""
        command = self.command_input.value.strip()
        if not command:
            self.update_output("[INFO] No command entered.", is_error=False)
            self.output_container.visible = True
            self.output_container.update()
            return

        # Show output area and indicate running status
        self.output_container.visible = True
        self.update_output(f"[Running]: {command}\n...", is_error=False)
        self.set_buttons_enabled(False) # Disable buttons

        # Run the command execution in a separate thread
        response = self.send_request(command)
        self.update_output("Printing output")
        self.update_response(response)


    def update_output(self, text: str, is_error: bool = False):
        """Updates the output text control's value and appearance."""
        self.output_text.value = text
        self.output_text.color = ft.colors.RED_ACCENT_200 if is_error else None # Use theme default

        # Ensure the container is visible when output is updated
        self.output_container.visible = True

        # Update the specific controls that changed
        self.output_text.update()
        self.output_container.update()


    def set_buttons_enabled(self, enabled: bool):
        """Enables or disables the Run, Edit, and Delete buttons."""
        is_disabled = not enabled
        self.run_button.disabled = is_disabled

        # Update the buttons
        self.run_button.update()


    def get_view(self) -> ft.Control:
        """Returns the main Flet control representing this cell's UI."""
        return self.view