import tkinter as tk
from tkinter import ttk, messagebox
from utils import center_toplevel_window

class LoginWindow(tk.Toplevel):
    def __init__(self, parent_root, master_password_callback, is_first_time = False):
        super().__init__(parent_root)
        self.withdraw()
        self.parent_root = parent_root
        self.master_password_callback = master_password_callback # Callback to check password
        self.is_first_time = is_first_time

        self.title("Secure Password Vault - Login")
        self.geometry("350x200")
        # self.resizable(False, False) # Disable resizing

        self.protocol("WM_DELETE_WINDOW", self.parent_root.on_app_close)

        # --- Widgets ---
        if is_first_time:
            self.lbl_password = tk.Label(self, text="Master Password:", font=('Arial', 10))
            self.lbl_password.pack(pady=(20, 5))

            self.txt_password = tk.Entry(self, show="*", width=30, font=('Arial', 10))
            self.txt_password.pack(pady=5)

            self.lbl_confirm = tk.Label(self, text="Confirm Password:", font=('Arial', 10))
            self.lbl_confirm.pack(pady=(10, 5))

            self.txt_confirm = tk.Entry(self, show="*", width=30, font=('Arial', 10))
            self.txt_confirm.pack(pady=10)

            # Button frame for better layout
            self.button_frame = tk.Frame(self)
            self.button_frame.pack(pady=10)

            self.btn_login = tk.Button(self.button_frame, text="Create Vault", command=self.login, width=12, font=('Arial', 10))
            self.btn_login.pack(side=tk.LEFT, padx=(0, 20))

            self.btn_exit = tk.Button(self.button_frame, text="Exit", command=self.parent_root.on_app_close, width=10, font=('Arial', 10))
            self.btn_exit.pack(side=tk.RIGHT)
        else:
            self.lbl_password = tk.Label(self, text="Master Password:", font=('Arial', 10))
            self.lbl_password.pack(pady=(20, 5))

            self.txt_password = tk.Entry(self, show="*", width=30, font=('Arial', 10))
            self.txt_password.pack(pady=5)
            self.txt_password.bind("<Return>", self.login) # Allow pressing Enter to login

            self.lbl_error_message = tk.Label(self, text="", fg="red", font=('Arial', 9))
            self.lbl_error_message.pack(pady=5)

            self.btn_login = tk.Button(self, text="Login", command=self.login, width=10, font=('Arial', 10))
            self.btn_login.pack(side=tk.LEFT, padx=(60, 10), pady=10)

            self.btn_exit = tk.Button(self, text="Exit", command=self.parent_root.on_app_close, width=10, font=('Arial', 10))
            self.btn_exit.pack(side=tk.RIGHT, padx=(10, 60), pady=10)

        self.txt_password.focus_set() # Set focus on the password entry field

        self.update_idletasks()
        center_toplevel_window(self, None)
        self.deiconify()

    def login(self, event=None):
        entered_password = self.txt_password.get()

        if self.is_first_time:
            confirm_password = self.txt_confirm.get()
            if not entered_password:
                self.show_error("Please enter a master password.")
                return

            if not confirm_password:
                self.show_error("Please confirm your master password.")
                return

            if entered_password != confirm_password:
                self.show_error("Failed to create vault. Please try again.")
                self.txt_password.delete(0, tk.END)
                self.txt_confirm.delete(0, tk.END)
                self.txt_password.focus_set()
                return
            
            # Passwords match, proceed with vault creation
            if self.master_password_callback(entered_password):
                # Main application will handle closing this window
                pass
            else:
                self.show_error("Failed to create vault. Please try again.")

        if self.master_password_callback(entered_password):
            # Main application (parent_root) will handle closing this window
            pass
        else:
            self.show_error("Incorrect master password. Please try again.")
            self.txt_password.delete(0, tk.END)
            self.txt_password.focus_set()

    def show_error(self, error_message):
        self.lbl_error_message.config(text=error_message)
        if self.is_first_time:
            # Clear both password fields
            self.txt_password.delete(0, tk.END)
            self.txt_confirm.delete(0, tk.END)
            self.txt_password.focus_set()
        else:
            # Clear single password field
            self.txt_password.delete(0, tk.END)
            self.txt_password.focus_set()