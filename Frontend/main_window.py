import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
import os
import sys

# Add Backend path (go up one level from Frontend to root, then to Backend)
project_root = os.path.dirname(os.path.dirname(__file__))
backend_path = os.path.join(project_root, 'Backend')
sys.path.insert(0, backend_path)

# Import local Frontend modules (same directory)
from utils import center_toplevel_window
from add_edit_password_window import AddEditPasswordWindow
from change_master_password_window import ChangeMasterPasswordWindow

# Import Backend modules
try:
    from password_entry import PasswordEntry
    from vault_api import (get_all_passwords, add_password, update_password, delete_password,
                          generate_strong_password, prepare_password_list)
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import Backend modules: {e}")
    sys.exit(1)

# Toplevel window is used instead of Tk for additional windows
class MainWindow(tk.Toplevel): 
    def __init__(self, parent_root):
        # Call the parent constructor
        super().__init__(parent_root)
        self.title("Secure Password Vault - Your Passwords")
        self.geometry("900x500")
        # prevent x button
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.parent_root = parent_root  # Save reference to main app
        self.password_entries = [] # List of PasswordEntry objects
        self.filtered_entries = [] # List of filtered password entries
        self.next_id = 1
        self.passwords_hidden = True
                
        # Sort and filter state
        self.sort_by = "service"  # "service", "username", "date", "strength"
        self.sort_order = "asc"  # "asc", "desc"
        self.search_term = ""

        self.create_widgets()

        # Load data from Backend
        self.load_passwords_from_backend()

        self.update_status_message()
        self.hide_passwords_in_treeview() # Hide passwords on startup

        self.update_idletasks()
        center_toplevel_window(self, None)

    def create_widgets(self):
        # TOP, fill=X: always fill horizontally
        # LEFT, fill=Y: always fill vertically
        # --- Main Layout: Side Menu and Treeview ---
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Side Menu (Left Panel)
        self.side_menu = ttk.Frame(self.main_frame, width=150)
        self.side_menu.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.side_menu.pack_propagate(False) # Prevent side_menu from shrinking

        # --- Search and Filter Bar (aligned with tree_frame) ---
        self.search_filter_frame = ttk.Frame(self.main_frame)
        self.search_filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Left side: Sort and Filter controls
        controls_left = ttk.Frame(self.search_filter_frame)
        controls_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Sort Label and Combo
        ttk.Label(controls_left, text="Sort by:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.sort_combo = ttk.Combobox(controls_left, width=15, state="readonly", font=('Arial', 9))
        self.sort_combo['values'] = ("Service (A-Z)", "Service (Z-A)", "Username (A-Z)", "Username (Z-A)", 
                                    "Date (Newest)", "Date (Oldest)", "Strength (Strong)", "Strength (Weak)")
        self.sort_combo.set("Service (A-Z)")
        self.sort_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.sort_combo.bind("<<ComboboxSelected>>", self.on_sort_changed)
        
        # Right side: Search
        controls_right = ttk.Frame(self.search_filter_frame)
        controls_right.pack(side=tk.RIGHT)
        
        ttk.Label(controls_right, text="Search:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(controls_right, width=30, font=('Arial', 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0,5))
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)

        # Treeview (Right Panel)
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.treeview = ttk.Treeview(self.tree_frame, columns=("Service", "Username", "Password", "Strength", "Last Updated"), show="headings")
        self.treeview.heading("Service", text="Service/Website", command=lambda: self.sort_by_column("service"))
        self.treeview.heading("Username", text="Username", command=lambda: self.sort_by_column("username"))
        self.treeview.heading("Password", text="Password")
        self.treeview.heading("Strength", text="Strength", command=lambda: self.sort_by_column("strength"))
        self.treeview.heading("Last Updated", text="Last Updated", command=lambda: self.sort_by_column("date"))

        self.treeview.column("Service", width=150, anchor=tk.W)
        self.treeview.column("Username", width=120, anchor=tk.W)
        self.treeview.column("Password", width=120, anchor=tk.W)
        self.treeview.column("Strength", width=80, anchor=tk.CENTER)
        self.treeview.column("Last Updated", width=120, anchor=tk.CENTER)
        
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar cho Treeview
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.treeview.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        # --- Side Menu Buttons ---
        self.btn_add = ttk.Button(self.side_menu, text="Add New", command=self.add_password)
        self.btn_add.pack(fill=tk.X, pady=(10, 5), padx=5)

        self.btn_edit = ttk.Button(self.side_menu, text="Edit", command=self.edit_password)
        self.btn_edit.pack(fill=tk.X, pady=5, padx=5)

        self.btn_delete = ttk.Button(self.side_menu, text="Delete", command=self.delete_password)
        self.btn_delete.pack(fill=tk.X, pady=5, padx=5)

        self.btn_generate_pwd = ttk.Button(self.side_menu, text="Generate Password", command=self.generate_password)
        self.btn_generate_pwd.pack(fill=tk.X, pady=(15, 5), padx=5)

        self.btn_copy_pwd = ttk.Button(self.side_menu, text="Copy Password", command=self.copy_password)
        self.btn_copy_pwd.pack(fill=tk.X, pady=5, padx=5)

        self.btn_show_hide_pwd = ttk.Button(self.side_menu, text="Show Passwords", command=self.toggle_password_visibility)
        self.btn_show_hide_pwd.pack(fill=tk.X, pady=5, padx=5)

        # self.btn_settings = ttk.Button(self.side_menu, text="Settings", command=self.open_settings, state="disabled")
        # self.btn_settings.pack(fill=tk.X, pady=(15, 5), padx=5)

        self.btn_logout = ttk.Button(self.side_menu, text="Logout", command=self.logout)
        self.btn_logout.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)

        self.btn_change_master_pwd = ttk.Button(self.side_menu, text="Change Master Password", command=self.change_master_password)
        self.btn_change_master_pwd.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)



        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text="Total Passwords: 0", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_passwords_from_backend(self):
        try:
            # Get passwords from Backend
            result = get_all_passwords()
            if result.get('success'):
                # Format passwords for display
                formatted_passwords = prepare_password_list(result)
                self.password_entries = []  # Reset list

                # Convert Backend format to frontend format
                for backend_entry in formatted_passwords:
                    if backend_entry:  # Skip None entries
                        try:
                            # Parse datetime strings if they exist, otherwise use current time
                            last_updated_str = backend_entry.get('last_updated', '')
                            created_at_str = backend_entry.get('created_at', '')
                            
                            # Parse datetime strings
                            if last_updated_str:
                                try:
                                    if isinstance(last_updated_str, str):
                                        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
                                    else:
                                        last_updated = last_updated_str
                                except Exception as e:
                                    last_updated = datetime.now()
                            else:
                                last_updated = datetime.now()
                                
                            if created_at_str:
                                try:
                                    if isinstance(created_at_str, str):
                                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                                    else:
                                        created_at = created_at_str
                                except Exception as e:
                                    created_at = None
                            else:
                                created_at = None

                            # Create frontend entry with properly parsed date
                            frontend_entry = PasswordEntry(
                                backend_entry['id'],
                                backend_entry['service'],
                                backend_entry['username'],
                                backend_entry['password'],
                                backend_entry['strength'],
                                backend_entry.get('notes', ''),
                                created_at,
                                last_updated
                            )
                            self.password_entries.append(frontend_entry)
                        except Exception as e:
                            # Skip problematic entries
                            print(f"Skipping invalid password entry: {str(e)}")
                            continue
            else:
                # Handle case where no passwords exist yet (empty vault)
                self.password_entries = []

            self.refresh_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load passwords: {str(e)}")
            self.password_entries = []
            self.refresh_treeview()

    def refresh_treeview(self):
        """Update the Treeview with current password entries (applies filter, sort, and search)"""
        # Apply filters and sorting
        self.apply_filters_and_sort()
        
        # Clear all existing items
        for i in self.treeview.get_children():
            self.treeview.delete(i)

        # Add filtered and sorted data
        for entry in self.filtered_entries:
            display_password = entry.password if not self.passwords_hidden else "********"
            self.treeview.insert("", tk.END, values=(
                entry.service,
                entry.username,
                display_password,
                entry.strength,
                entry.last_updated.strftime("%Y-%m-%d")
            ), iid=entry.id) # Use ID of the object as the iid of the Treeview

        self.update_status_message()

    def update_status_message(self):
        self.status_bar.config(text=f"Total Passwords: {len(self.password_entries)}")

    def hide_passwords_in_treeview(self):
        self.passwords_hidden = True
        self.btn_show_hide_pwd.config(text="Show Passwords")
        self.refresh_treeview()

    def show_passwords_in_treeview(self):
        self.passwords_hidden = False
        self.btn_show_hide_pwd.config(text="Hide Passwords")
        self.refresh_treeview()

    def toggle_password_visibility(self):
        if self.passwords_hidden:
            self.show_passwords_in_treeview()
        else:
            self.hide_passwords_in_treeview()

    def get_selected_password_entry(self):
        """Get the currently selected PasswordEntry from the Treeview."""
        try:
            selected_item_id = self.treeview.focus()
            if not selected_item_id:
                messagebox.showinfo("No Selection", "Please select a password entry.", parent=self)
                return None

            # Get the PasswordEntry object based on iid
            selected_id = int(selected_item_id)
            # Search in filtered_entries first (current view), then fallback to all entries
            for entry in self.filtered_entries:
                if entry.id == selected_id:
                    return entry
            # Fallback to all entries if not found in filtered (shouldn't happen, but safety check)
            for entry in self.password_entries:
                if entry.id == selected_id:
                    return entry
            return None 
        except ValueError:
             messagebox.showinfo("No Selection", "Please select a password entry.", parent=self)
             return None


    def add_password(self):
        add_edit_window = AddEditPasswordWindow(self, mode="add")
        self.wait_window(add_edit_window) # wait until window is closed

        if add_edit_window.result: # If user pressed Save
            new_entry_data = add_edit_window.result
            try:
                # Save password to backend database
                result = add_password(
                    new_entry_data['service'],
                    new_entry_data['username'],
                    new_entry_data['password'],
                    new_entry_data['notes']
                )

                if result.get('success'):
                    # Reload passwords from Backend to ensure sync
                    self.load_passwords_from_backend()
                    messagebox.showinfo("Success", "Password added successfully!", parent=self)
                else:
                    messagebox.showerror("Error", result.get('error', 'Failed to add password'), parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add password: {str(e)}", parent=self)

    def edit_password(self):
        selected_entry = self.get_selected_password_entry()
        if selected_entry:
            add_edit_window = AddEditPasswordWindow(self, mode="edit", entry_data=selected_entry)
            self.wait_window(add_edit_window)
            
            if add_edit_window.result: # Nếu người dùng nhấn Save
                updated_data = add_edit_window.result
                try:
                    # Update password in Backend database
                    result = update_password(
                        selected_entry.id,
                        updated_data['service'],
                        updated_data['username'],
                        updated_data['password'],
                        updated_data['notes']
                    )

                    if result.get('success'):
                        # Reload passwords from Backend to ensure sync
                        self.load_passwords_from_backend()
                        messagebox.showinfo("Success", "Password updated successfully!", parent=self)
                    else:
                        messagebox.showerror("Error", result.get('error', 'Failed to update password'), parent=self)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update password: {str(e)}", parent=self)

    def delete_password(self):
        selected_entry = self.get_selected_password_entry()
        if selected_entry:
            if messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete the password for '{selected_entry.service}'?",
                                   parent=self):
                try:
                    # Delete password from Backend database
                    result = delete_password(selected_entry.id)

                    if result.get('success'):
                        # Reload passwords from Backend to ensure sync
                        self.load_passwords_from_backend()
                        messagebox.showinfo("Success", "Password deleted successfully!", parent=self)
                    else:
                        messagebox.showerror("Error", result.get('error', 'Failed to delete password'), parent=self)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete password: {str(e)}", parent=self)

    def generate_password(self):
        try:
            generated_password = generate_strong_password()
            if generated_password:
                # Copy to clipboard for easy use
                self.clipboard_clear()
                self.clipboard_append(generated_password)
                messagebox.showinfo("Generated", f"Strong password generated and copied to clipboard!\n\nPassword: {generated_password}", parent=self)
            else:
                messagebox.showerror("Error", "Failed to generate password", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}", parent=self)

    def copy_password(self):
        selected_entry = self.get_selected_password_entry()
        if selected_entry:
            self.clipboard_clear()
            self.clipboard_append(selected_entry.password)
            messagebox.showinfo("Copied", "Password copied to clipboard!", parent=self)
        
    def open_settings(self):
        messagebox.showinfo("Settings", "Settings functionality not yet implemented.", parent=self)
    
    def change_master_password(self):
        """Open the change master password window."""
        change_password_window = ChangeMasterPasswordWindow(self)
        self.wait_window(change_password_window)
        
        # If password was changed successfully, logout user for security
        if change_password_window.password_changed:
            # Automatically logout and show login window
            self.parent_root.show_login()  # Show login window
            self.destroy()  # Close main window

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?", parent=self):
            self.parent_root.show_login() # Call function in main app to show login
            self.destroy() # Close main window

    def apply_filters_and_sort(self):
        """Apply search filter and sorting to password entries"""
        # Start with all entries
        filtered = list(self.password_entries)
        
        # Apply search filter
        if self.search_term:
            search_lower = self.search_term.lower()
            filtered = [entry for entry in filtered 
                       if search_lower in entry.service.lower() 
                       or search_lower in entry.username.lower()]
        
        # Apply sorting
        if self.sort_by == "service":
            filtered.sort(key=lambda x: x.service.lower(), reverse=(self.sort_order == "desc"))
        elif self.sort_by == "username":
            filtered.sort(key=lambda x: x.username.lower(), reverse=(self.sort_order == "desc"))
        elif self.sort_by == "date":
            filtered.sort(key=lambda x: x.last_updated, reverse=(self.sort_order == "desc"))
        elif self.sort_by == "strength":
            # Sort by strength: Strong > Medium > Weak
            strength_order = {"strong": 3, "medium": 2, "weak": 1, "very strong": 4, "very weak": 0}
            filtered.sort(key=lambda x: strength_order.get(x.strength.lower() if x.strength else "", 0), reverse=(self.sort_order == "desc"))
        
        self.filtered_entries = filtered
    
    def on_sort_changed(self, event=None):
        """Handle sort change"""
        sort_value = self.sort_combo.get()
        
        if "Service (A-Z)" in sort_value:
            self.sort_by = "service"
            self.sort_order = "asc"
        elif "Service (Z-A)" in sort_value:
            self.sort_by = "service"
            self.sort_order = "desc"
        elif "Username (A-Z)" in sort_value:
            self.sort_by = "username"
            self.sort_order = "asc"
        elif "Username (Z-A)" in sort_value:
            self.sort_by = "username"
            self.sort_order = "desc"
        elif "Date (Newest)" in sort_value:
            self.sort_by = "date"
            self.sort_order = "desc"
        elif "Date (Oldest)" in sort_value:
            self.sort_by = "date"
            self.sort_order = "asc"
        elif "Strength (Strong)" in sort_value:
            self.sort_by = "strength"
            self.sort_order = "desc"
        elif "Strength (Weak)" in sort_value:
            self.sort_by = "strength"
            self.sort_order = "asc"
        
        self.refresh_treeview()
    
    def on_search_changed(self, event=None):
        """Handle search entry change"""
        self.search_term = self.search_entry.get().strip()
        self.refresh_treeview()
    
    def sort_by_column(self, column):
        """Handle column header click for sorting"""
        # If clicking the same column, toggle order
        if self.sort_by == column:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_by = column
            self.sort_order = "asc"
        
        # Update combo box to reflect current sort
        if column == "service":
            self.sort_combo.set("Service (Z-A)" if self.sort_order == "desc" else "Service (A-Z)")
        elif column == "username":
            self.sort_combo.set("Username (Z-A)" if self.sort_order == "desc" else "Username (A-Z)")
        elif column == "date":
            self.sort_combo.set("Date (Newest)" if self.sort_order == "desc" else "Date (Oldest)")
        elif column == "strength":
            self.sort_combo.set("Strength (Strong)" if self.sort_order == "desc" else "Strength (Weak)")
        
        self.refresh_treeview()
    
    def filter_passwords(self, event=None):
        """Legacy method - redirects to new search handler"""
        self.on_search_changed(event)

    def on_close(self):
        """Handle the close event of the main window."""
        self.parent_root.on_app_close() # Call the main app's close function