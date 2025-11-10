import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add Backend path (go up one level from Frontend to root, then to Backend)
project_root = os.path.dirname(os.path.dirname(__file__))
backend_path = os.path.join(project_root, 'Backend')
sys.path.insert(0, backend_path)

# Import local Frontend modules (same directory)
from utils import center_toplevel_window

# Import Backend
try:
    from vault_api import change_master_password
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import Backend modules: {e}")
    sys.exit(1)

class ChangeMasterPasswordWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_password_visible = False
        self.new_password_visible = False
        self.confirm_password_visible = False
        self.password_changed = False  # Flag to indicate if password was changed successfully

        self.title("Change Master Password")
        self.geometry("450x350")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.create_widgets()

        # Ensure this window is always on top and waits
        self.transient(parent)
        # Block events from the parent window
        self.grab_set()

        # Center the window after all widgets are created
        self.update_idletasks()
        center_toplevel_window(self, None)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = "Please enter your current master password and choose a new one."
        ttk.Label(self.main_frame, text=instructions, font=('Arial', 9), wraplength=400).pack(anchor=tk.W, pady=(0, 15))

        # Current Password
        ttk.Label(self.main_frame, text="Current Master Password:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        current_password_frame = ttk.Frame(self.main_frame)
        current_password_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.txt_current_password = ttk.Entry(current_password_frame, show="*", width=30, font=('Arial', 10))
        self.txt_current_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.txt_current_password.focus()

        self.btn_toggle_current = ttk.Button(current_password_frame, text="Show", command=self.toggle_current_password_visibility, width=8)
        self.btn_toggle_current.pack(side=tk.LEFT)

        # New Password
        ttk.Label(self.main_frame, text="New Master Password:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        new_password_frame = ttk.Frame(self.main_frame)
        new_password_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.txt_new_password = ttk.Entry(new_password_frame, show="*", width=30, font=('Arial', 10))
        self.txt_new_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        self.btn_toggle_new = ttk.Button(new_password_frame, text="Show", command=self.toggle_new_password_visibility, width=8)
        self.btn_toggle_new.pack(side=tk.LEFT)

        # Confirm New Password
        ttk.Label(self.main_frame, text="Confirm New Password:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        confirm_password_frame = ttk.Frame(self.main_frame)
        confirm_password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.txt_confirm_password = ttk.Entry(confirm_password_frame, show="*", width=30, font=('Arial', 10))
        self.txt_confirm_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        self.btn_toggle_confirm = ttk.Button(confirm_password_frame, text="Show", command=self.toggle_confirm_password_visibility, width=8)
        self.btn_toggle_confirm.pack(side=tk.LEFT)

        # Password requirements
        requirements = "• Minimum 6 characters\n• Should be different from current password"
        ttk.Label(self.main_frame, text=requirements, font=('Arial', 8), foreground='gray', justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_change = ttk.Button(self.button_frame, text="Change Password", command=self.change_password, width=17)
        self.btn_change.pack(side=tk.LEFT, expand=True, padx=(0, 5))

        self.btn_cancel = ttk.Button(self.button_frame, text="Cancel", command=self.on_cancel, width=15)
        self.btn_cancel.pack(side=tk.RIGHT, expand=True, padx=(5, 0))

    def toggle_current_password_visibility(self):
        if self.current_password_visible:
            self.txt_current_password.config(show="*")
            self.btn_toggle_current.config(text="Show")
        else:
            self.txt_current_password.config(show="")
            self.btn_toggle_current.config(text="Hide")
        self.current_password_visible = not self.current_password_visible

    def toggle_new_password_visibility(self):
        if self.new_password_visible:
            self.txt_new_password.config(show="*")
            self.btn_toggle_new.config(text="Show")
        else:
            self.txt_new_password.config(show="")
            self.btn_toggle_new.config(text="Hide")
        self.new_password_visible = not self.new_password_visible

    def toggle_confirm_password_visibility(self):
        if self.confirm_password_visible:
            self.txt_confirm_password.config(show="*")
            self.btn_toggle_confirm.config(text="Show")
        else:
            self.txt_confirm_password.config(show="")
            self.btn_toggle_confirm.config(text="Hide")
        self.confirm_password_visible = not self.confirm_password_visible

    def validate_inputs(self):
        current_password = self.txt_current_password.get().strip()
        new_password = self.txt_new_password.get().strip()
        confirm_password = self.txt_confirm_password.get().strip()

        # Check if fields are filled
        if not current_password:
            messagebox.showwarning("Validation Error", "Please enter your current master password.", parent=self)
            self.txt_current_password.focus()
            return False

        if not new_password:
            messagebox.showwarning("Validation Error", "Please enter a new master password.", parent=self)
            self.txt_new_password.focus()
            return False

        if not confirm_password:
            messagebox.showwarning("Validation Error", "Please confirm your new master password.", parent=self)
            self.txt_confirm_password.focus()
            return False

        # Check minimum length
        if len(new_password) < 6:
            messagebox.showwarning("Validation Error", "New master password must be at least 6 characters long.", parent=self)
            self.txt_new_password.focus()
            return False

        # Check if passwords match
        if new_password != confirm_password:
            messagebox.showerror("Validation Error", "New password and confirm password do not match.", parent=self)
            self.txt_confirm_password.focus()
            return False

        # Check if new password is different from current
        if current_password == new_password:
            messagebox.showwarning("Validation Error", "New password must be different from the current password.", parent=self)
            self.txt_new_password.focus()
            return False

        return True

    def change_password(self):
        if not self.validate_inputs():
            return

        current_password = self.txt_current_password.get().strip()
        new_password = self.txt_new_password.get().strip()

        # Confirm with user
        if not messagebox.askyesno("Confirm Change", 
                                  "Are you sure you want to change your master password?\n\n"
                                  "Make sure you remember the new password, as you will need it to unlock your vault.",
                                  parent=self):
            return

        try:
            # Call backend function to change master password
            result = change_master_password(current_password, new_password)

            if result.get('success'):
                self.password_changed = True
                messagebox.showinfo("Success", 
                                  "Master password changed successfully!\n\n"
                                  "You will be logged out and need to login again with your new password.",
                                  parent=self)
                self.destroy()
            else:
                error_message = result.get('error', 'Failed to change master password')
                messagebox.showerror("Error", error_message, parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change master password: {str(e)}", parent=self)

    def on_cancel(self):
        self.destroy()

