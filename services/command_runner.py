# services/command_runner.py
import subprocess
import threading
import os
import flet as ft # Needed for ft.Control type hint potentially
from typing import TYPE_CHECKING

# Avoid circular import issues at runtime, only import CommandCell for type checking
if TYPE_CHECKING:
    from components.command_cell import CommandCell

def run_command_thread(command_str: str, cell_instance: 'CommandCell'):
    """
    Runs the command in a separate thread and updates the cell's output.

    Args:
        command_str (str): The command to execute.
        cell_instance (CommandCell): The instance of the cell to update.
                                      We use a forward reference string hint
                                      or TYPE_CHECKING to avoid circular imports.
    """
    try:
        # SECURITY WARNING: shell=True is convenient but risky with untrusted input.
        # Consider alternatives like shlex.split() and shell=False if possible.
        process = subprocess.run(
            command_str,
            shell=True,
            capture_output=True,
            text=True,
            check=False, # Don't raise exception on non-zero exit code
            cwd=os.getcwd() # Run in the app's current directory
        )

        output = ""
        error = ""
        is_error = False

        if process.stdout:
            output += f"[STDOUT]:\n{process.stdout.strip()}\n"
        if process.stderr:
            error += f"[STDERR]:\n{process.stderr.strip()}\n"
            is_error = True # Treat any stderr output as potentially an error condition

        if process.returncode != 0:
            error += f"\n[Exit Code: {process.returncode}]"
            is_error = True

        full_output = output + error
        if not full_output.strip():
            full_output = "[INFO] Command executed with no output."

        # Update the cell's UI via its methods
        # Flet handles making control updates thread-safe when called from background threads.
        cell_instance.update_output(full_output.strip(), is_error)

    except Exception as e:
        # Update UI with execution error
        cell_instance.update_output(f"[Execution Error]:\n{str(e)}", is_error=True)
    finally:
        # Re-enable buttons on the main thread via the cell instance method
        cell_instance.set_buttons_enabled(True)