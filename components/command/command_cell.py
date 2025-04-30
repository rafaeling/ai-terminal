# components/command_cell.py
import os
import flet as ft
import threading
from typing import Callable
from services.command_runner import run_command_thread # Import the runner function
from services.llm_model_sdks.gemini.gemini_client import GeminiClient

class CommandCell:
    """Represents a single interactive command cell in the notebook."""

    def __init__(self, context: str, command_text: str, page: ft.Page, delete_callback: Callable[['CommandCell'], None], update_ai_error_callback: Callable[['CommandCell'], None]):
        """
        Initializes a CommandCell.

        Args:
            page (ft.Page): The Flet Page object.
            delete_callback (Callable): A function to call when this cell's
                                       delete button is clicked. It receives the
                                       CommandCell instance itself as an argument.
        """
        self.path_context = context
        self.page = page
        self.delete_callback = delete_callback
        self.update_ai_error_callback = update_ai_error_callback
        self._run_thread: threading.Thread | None = None
        self.gemini_client = GeminiClient()
        self.ai_command_error_suggestion = ""

        # --- Flet Controls for the Cell ---
        self.path_context_fix = ft.TextField(
            value=self.path_context,
            multiline=False,
            expand=True,
            read_only=True,
            border_color=ft.colors.with_opacity(0.5, ft.colors.OUTLINE),
            focused_border_color=ft.colors.PRIMARY,
            cursor_color=ft.colors.PRIMARY,
            # text_style=ft.TextStyle(font_family="monospace"), # Requires font setup
            on_submit=self.run_command_click # Allow running with Enter key
        )

        self.command_input = ft.TextField(
            value=command_text,
            multiline=False,
            expand=True,
            border_color=ft.colors.with_opacity(0.5, ft.colors.OUTLINE),
            focused_border_color=ft.colors.PRIMARY,
            cursor_color=ft.colors.PRIMARY,
            # text_style=ft.TextStyle(font_family="monospace"), # Requires font setup
            on_submit=self.run_command_click # Allow running with Enter key
        )

        self.run_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW_ROUNDED,
            tooltip="Run Command",
            on_click=self.run_command_click,
            icon_color=ft.colors.GREEN_ACCENT_400,
        )

        self.edit_button = ft.IconButton(
            icon=ft.icons.EDIT_ROUNDED,
            tooltip="Focus Command Input",
            on_click=self.edit_command_click,
            icon_color=ft.colors.BLUE_ACCENT_200,
        )

        self.delete_button = ft.IconButton(
            icon=ft.icons.DELETE_ROUNDED,
            tooltip="Delete Cell",
            on_click=self._handle_delete, # Use internal handler
            icon_color=ft.colors.RED_ACCENT_400,
        )

        self.ask_ai_button = ft.ElevatedButton(
            text="Ask AI",
            icon=ft.icons.SEND,
            tooltip="Ask AI",
            on_click=self.ask_ai_with_error,
            icon_color=ft.colors.GREEN_ACCENT_400,
            #animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
            visible=False
        )

        self.output_text = ft.Text(
            "[Output will appear here]",
            selectable=True,
            # style=ft.TextStyle(font_family="monospace"), # Requires font setup
        )

        self.output_container = ft.Container(
            content=ft.Row(
                [
                    self.output_text,
                    self.ask_ai_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(10),
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
            border_radius=ft.border_radius.all(4),
            margin=ft.margin.only(top=5),
            visible=False # Initially hidden until first run
        )

        # --- Main Layout for this Cell ---
        self.view = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.path_context_fix,
                            self.command_input,
                            self.run_button,
                            self.edit_button,
                            self.delete_button,
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

    def _handle_delete(self, e: ft.ControlEvent):
        """Internal method to call the provided delete callback."""
        self.delete_callback(self) # Pass the cell instance itself

    def update_ai_error_response(self):
        self.update_ai_error_callback(self)
        
    def send_error_request(self, command, error):
        return self.gemini_client.send_error_request(command, error)
    
    def ask_ai_with_error(self, e: ft.ControlEvent):
        command = self.command_input.value.strip()
        error = self.output_text.value
        self.ai_command_error_suggestion = self.send_error_request(command, error)
        self.update_ai_error_response()
    
    def get_ai_command_error_suggestion(self):
        return self.ai_command_error_suggestion
    
    def change_directory(self, path):
        """Changes the current working directory."""
        global PROMPT # We need to modify the global prompt
        try:
            os.chdir(path)
            # Update the prompt to reflect the new directory
            PROMPT = f"{os.getcwd()}:~$ "
            self.path_context_fix.value = PROMPT
            self.path_context_fix.update()
            return None # No error message needed for success
        except FileNotFoundError:
            return f"cd: no such file or directory: {path}"
        except NotADirectoryError:
            return f"cd: not a directory: {path}"
        except PermissionError:
            return f"cd: permission denied: {path}"
        except Exception as e:
            return f"cd: failed to change directory: {e}"
    
    def run_command_click(self, e: ft.ControlEvent):
        """Handles the click event for the run button or Enter key in TextField."""
        command = self.command_input.value.strip()
        if not command:
            self.update_output("[INFO] No command entered.", is_error=False)
            self.output_container.visible = True
            self.output_container.update()
            return

        if command.startswith("cd "):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                path_to_change = parts[1]
                # Handle cd ~ manually
                if path_to_change == '~':
                    path_to_change = os.path.expanduser("~")
                error_msg = self.change_directory(path_to_change)
                if error_msg:
                    print(f"{error_msg}")
            else:
                # 'cd' without arguments usually goes to home directory
                error_msg = self.change_directory(os.path.expanduser("~"))
                if error_msg:
                    print(f"{error_msg}")

        if self._run_thread and self._run_thread.is_alive():
            # Optionally provide feedback that a command is running
            # self.update_output("[INFO] A command is already running...", is_error=False)
            print("Command already running in this cell.") # Console feedback
            return

        # Show output area and indicate running status
        self.output_container.visible = True
        self.update_output(f"[Running]: {command}\n...", is_error=False)
        self.set_buttons_enabled(False) # Disable buttons

        # Run the command execution in a separate thread
        self._run_thread = threading.Thread(
            target=run_command_thread, # Use the imported function
            args=(command, self),      # Pass command and this cell instance
            daemon=True
        )
        self._run_thread.start()

    def edit_command_click(self, e: ft.ControlEvent):
        """Focuses the input field."""
        self.command_input.focus()
        # No need to call page.update() here, focus should work directly

    def update_output(self, text: str, is_error: bool = False):
        """Updates the output text control's value and appearance."""
        self.output_text.value = text
        self.output_text.color = ft.colors.RED_ACCENT_200 if is_error else None # Use theme default

        # Ensure the container is visible when output is updated
        self.output_container.visible = True
        if is_error:
            self.ask_ai_button.visible = True
        else:
            self.ask_ai_button.visible = False

        # Update the specific controls that changed
        self.output_text.update()
        self.output_container.update()
        self.command_input.focus()


    def set_buttons_enabled(self, enabled: bool):
        """Enables or disables the Run, Edit, and Delete buttons."""
        is_disabled = not enabled
        self.run_button.disabled = is_disabled
        self.edit_button.disabled = is_disabled
        self.delete_button.disabled = is_disabled

        # Update the buttons
        self.run_button.update()
        self.edit_button.update()
        self.delete_button.update()

        if enabled:
            self._run_thread = None # Clear thread reference when done/failed


    def get_view(self) -> ft.Control:
        """Returns the main Flet control representing this cell's UI."""
        return self.view