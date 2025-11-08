import tkinter as tk
from tkinter import ttk, messagebox

# Add Frontend and Backend paths
import os
import sys
project_root = os.path.dirname(__file__)
frontend_path = os.path.join(project_root, 'Frontend')
backend_path = os.path.join(project_root, 'Backend')
sys.path.insert(0, frontend_path)
sys.path.insert(0, backend_path)

# Import Frontend
from login_window import LoginWindow
from main_window import MainWindow

# Import Backend
try:
    from vault_api import setup_master_password, verify_master_password, get_vault_status
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import Backend modules: {e}")
    sys.exit(1)

class SecurePasswordVaultApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw() # Hide the root window initially

        # Setup theme
        # style = ttk.Style()
        # try:
        #     style.theme_use('vista') # Try 'vista' on Windows
        # except:
        #     style.theme_use('clam') # 'clam' or 'default' on Mac/Linux

        self.login_window = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        """Show the login window."""
        # Ensure the main window is closed (if it exists)
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        # Check if this is first-time setup or existing vault
        vault_db_path = os.path.join(project_root, 'vault.db')
        vault_exists = os.path.exists(vault_db_path)
        is_first_time = not vault_exists
        self.login_window = LoginWindow(self, self.handle_master_password_check, is_first_time)

    def handle_master_password_check(self, entered_password):
        try:
            # Check if vault exists
            vault_db_path = os.path.join(project_root, 'vault.db')
            vault_exists = os.path.exists(vault_db_path)
            if not vault_exists:
                # First-time setup
                result = setup_master_password(entered_password)
                if result.get('success'):
                    # Vault created successfully, now unlock it
                    unlock_result = verify_master_password(entered_password)
                    if unlock_result.get('success'):
                        if self.login_window:
                            self.login_window.destroy()
                            self.login_window = None
                        self.show_main()
                        return True
                    else:
                        # Vault created but couldn't unlock it
                        if self.login_window:
                            self.login_window.show_error(
                                "Vault created but failed to unlock. Please restart the application and try logging in.")
                        return False
                else:
                    # Show error in login window
                    if self.login_window:
                        self.login_window.show_error(result.get('error', 'Failed to create vault'))
                    return False
            else:
                # Existing vault - verify master password
                result = verify_master_password(entered_password)
                if result.get('success'):
                    if self.login_window:
                        self.login_window.destroy()
                        self.login_window = None
                    self.show_main()
                    return True
                else:
                    # Show error in login window
                    if self.login_window:
                        self.login_window.show_error(result.get('error', 'Incorrect master password'))
                    return False
        except Exception as e:
            # Handle any Backend-related errors
            error_msg = f"Authentication error: {str(e)}"
            messagebox.showerror("Error", error_msg)
            return False

    def show_main(self):
        """Show the main application window."""
        self.main_window = MainWindow(self)

    def on_app_close(self):
        """Handle when the user requests to close the application (clicks X)."""
        if messagebox.askokcancel("Exit Application", "Do you want to exit the Secure Password Vault?"):
            self.destroy() # Close the entire application

if __name__ == "__main__":
    app = SecurePasswordVaultApp()
    app.mainloop()