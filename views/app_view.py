# views/notebook_view.py
import os
import flet as ft
from components.command.command_cell import CommandCell # Import the component
from components.chat_box.chat_box_cell import ChatBoxCell
from models.app import App
from colorama import Fore, Style

PROMPT = f"{os.getcwd()}" # Default prompt showing current dir

class AppView:
    """Manages the main view containing the command cells."""

    def __init__(self, page: ft.Page):
        global PROMPT
        self.page = page
        # List to hold the CommandCell *instances*
        self.all_cells: list[CommandCell] = []
        # Flet control that displays the cell views
        self.command_list_view = ft.Column(
            controls=[],
            spacing=0, # Let cell container handle padding/margins
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True # Make the list fill available vertical space
        )
        self.app_logic = App()

    def delete_cell(self, cell_to_delete: CommandCell):
        """Callback function to remove a cell from the list and UI."""
        view_to_remove = cell_to_delete.get_view()
        if view_to_remove in self.command_list_view.controls:
            self.command_list_view.controls.remove(view_to_remove)
        if cell_to_delete in self.all_cells:
            self.all_cells.remove(cell_to_delete)

        print(f"Deleted cell. Remaining cells: {len(self.all_cells)}") # Debugging
        self.page.update() # Update the page to reflect the removal
        
    def delete_all_cells(self):
        for _, command_cell in enumerate(self.all_cells):
            self.delete_cell(command_cell)
        self.page.update()
    
    def update_response(self, response: str):
        """Callback function to remove a cell from the list and UI."""
        self.delete_all_cells()
        self.app_logic.set_response(response)
        command_list = self.app_logic.get_commands()
        
        for _, command in enumerate(command_list):
            self.add_cell_click(command, None)
            
        self.page.update() # Update the page
        
    def ask_ai(self, cell_to_process: CommandCell):
        self.app_logic.set_response(cell_to_process.get_ai_command_error_suggestion())
        command_list = self.app_logic.get_commands()
        
        for _, command in enumerate(command_list):
            self.add_cell_click(command, None)
            
        self.page.update() # Update the page

    def add_chat_box_cell_click(self, e: ft.ControlEvent | None):
        """Adds a new command cell to the list and UI."""
        # Pass the page and the delete_cell method of this view instance
        new_cell = ChatBoxCell(self.page, self.update_response)
        #self.all_cells.append(new_cell)
        self.command_list_view.controls.append(new_cell.get_view())
        #print(f"Added cell. Total cells: {len(self.all_cells)}") # Debugging
        self.page.update() # Update the page to show the new cell
        # Optionally focus the new cell's input
        new_cell.command_input.focus()
        # self.page.update() # Update again if focus needs it

    def add_cell_click(self, command_text: str, e: ft.ControlEvent | None):
        """Adds a new command cell to the list and UI."""
        # Pass the page and the delete_cell method of this view instance
        new_cell = CommandCell(PROMPT, command_text, self.page, self.delete_cell, self.ask_ai)
        self.all_cells.append(new_cell)
        self.command_list_view.controls.append(new_cell.get_view())
        print(f"Added cell. Total cells: {len(self.all_cells)}") # Debugging
        self.page.update() # Update the page to show the new cell
        # Optionally focus the new cell's input
        new_cell.command_input.focus()
        # self.page.update() # Update again if focus needs it


    def build(self) -> list[ft.Control]:
        """Builds the list of controls for the main page view."""
        add_button = ft.ElevatedButton(
            "Standard Terminal",
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            on_click=lambda e: self.add_cell_click("ls -a", e)
        )

        # Return the list of top-level controls for this view
        return [
            ft.Row(
                [
                    ft.Text("AI Terminal", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True), # Pushes button to the right
                    add_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(height=1),
            self.command_list_view # The scrollable column holding the cells
        ]