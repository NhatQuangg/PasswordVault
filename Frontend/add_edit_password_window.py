import tkinter as tk
from tkinter import ttk, messagebox
import re
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
    from vault_api import generate_strong_password, check_strength
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import Backend modules: {e}")
    sys.exit(1)

class AddEditPasswordWindow(tk.Toplevel):
    def __init__(self, parent, mode="add", entry_data=None):
        super().__init__(parent)
        self.parent = parent
        self.mode = mode # "add" or "edit"
        self.entry_data = entry_data # Object PasswordEntry if "edit"
        self.result = None # Will contain data after successful "Save"
        self.password_visible = False

        self.title("Add New Password" if mode == "add" else "Edit Password")
        self.geometry("450x320")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.create_widgets()
        if self.mode == "edit" and self.entry_data:
            self.load_entry_data()

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

        # Service/Website
        ttk.Label(self.main_frame, text="Service/Website Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        self.txt_service_name = ttk.Entry(self.main_frame, width=40, font=('Arial', 10))
        self.txt_service_name.pack(fill=tk.X, pady=(0, 10))

        # Username
        ttk.Label(self.main_frame, text="Username:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        self.txt_username = ttk.Entry(self.main_frame, width=40, font=('Arial', 10))
        self.txt_username.pack(fill=tk.X, pady=(0, 10))

        # Password
        ttk.Label(self.main_frame, text="Password:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        self.password_frame = ttk.Frame(self.main_frame)
        self.password_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.txt_password = ttk.Entry(self.password_frame, show="*", width=30, font=('Arial', 10))
        self.txt_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.txt_password.bind("<KeyRelease>", self.update_password_strength_event)

        self.btn_toggle_password_visibility = ttk.Button(self.password_frame, text="Show", command=self.toggle_password_visibility, width=6)
        self.btn_toggle_password_visibility.pack(side=tk.LEFT)

        self.btn_generate_password = ttk.Button(self.password_frame, text="Generate", command=self.generate_password, width=10)
        self.btn_generate_password.pack(side=tk.LEFT, padx=(5,0))

        # Password Strength
        ttk.Label(self.main_frame, text="Password Strength:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        self.pb_password_strength = ttk.Progressbar(self.main_frame, orient="horizontal", length=200, mode="determinate")
        self.pb_password_strength.pack(fill=tk.X, pady=(0, 5))
        self.lbl_password_strength_text = ttk.Label(self.main_frame, text="", font=('Arial', 9))
        self.lbl_password_strength_text.pack(anchor=tk.W, pady=(0, 10))
        
        # Notes
        # ttk.Label(self.main_frame, text="Notes (optional):", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        # self.txt_notes = tk.Text(self.main_frame, height=4, width=40, font=('Arial', 10))
        # self.txt_notes.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_save = ttk.Button(self.button_frame, text="Save", command=self.save_entry, width=10)
        self.btn_save.pack(side=tk.LEFT, expand=True, padx=(0, 5))

        self.btn_cancel = ttk.Button(self.button_frame, text="Cancel", command=self.on_cancel, width=10)
        self.btn_cancel.pack(side=tk.RIGHT, expand=True, padx=(5, 0))

    def load_entry_data(self):
        self.txt_service_name.insert(0, self.entry_data.service)
        self.txt_username.insert(0, self.entry_data.username)
        self.txt_password.insert(0, self.entry_data.password)
        # self.txt_notes.insert(tk.END, self.entry_data.notes)
        self.update_password_strength() # Update strength on load

    def toggle_password_visibility(self):
        if self.password_visible:
            self.txt_password.config(show="*")
            self.btn_toggle_password_visibility.config(text="Show")
        else:
            self.txt_password.config(show="")
            self.btn_toggle_password_visibility.config(text="Hide")
        self.password_visible = not self.password_visible

    def generate_password(self):
        try:
            generated_password = generate_strong_password()
            if generated_password:
                self.txt_password.delete(0, tk.END)
                self.txt_password.insert(0, generated_password)
                self.update_password_strength()
                messagebox.showinfo("Generated", f"Strong password generated!\n\nPassword: {generated_password}", parent=self)
            else:
                messagebox.showerror("Error", "Failed to generate password", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}", parent=self)

    def update_password_strength_event(self, event=None):
        self.update_password_strength()

    def update_password_strength(self):
        password = self.txt_password.get()
        score = 0
        strength_text = "Very Weak"
        color = "red"

        # Length
        if len(password) >= 8: score += 20
        if len(password) >= 12: score += 20
        if len(password) >= 16: score += 20

        # Character types
        if re.search(r"[a-z]", password): score += 10
        if re.search(r"[A-Z]", password): score += 10
        if re.search(r"[0-9]", password): score += 10
        if re.search(r"[!@#$%^&*()_+=\-{}[\]|:;\"'<,>.?/`~]", password): score += 15 # Special chars

        if score == 0 and len(password) > 0:
            score = 5 # Minimum score for non-empty password
        
        if score < 40:
            strength_text = "Weak"
            color = "red"
        elif score < 70:
            strength_text = "Medium"
            color = "orange"
        elif score < 90:
            strength_text = "Strong"
            color = "green"
        else:
            strength_text = "Very Strong"
            color = "darkgreen"
        
        self.pb_password_strength['value'] = min(score, 100)
        self.lbl_password_strength_text.config(text=strength_text, foreground=color)
        return strength_text

    def save_entry(self):
        service = self.txt_service_name.get().strip()
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()
        # notes = self.txt_notes.get("1.0", tk.END).strip()
        current_strength_text = self.update_password_strength() # Get current strength text


        if not service or not username or not password:
            messagebox.showwarning("Validation Error", "Please fill in all required fields (Service/Website, Username, Password).", parent=self)
            return

        self.result = {
            'service': service,
            'username': username,
            'password': password,
            'strength': current_strength_text,
            'notes': '' # optional, will be empty for now
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()