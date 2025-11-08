import tkinter as tk

def center_toplevel_window(toplevel_window, parent_window=None):
    """Centers a Toplevel window relative to its parent or the screen."""
    toplevel_window.update_idletasks()
    # Get screen dimensions
    screen_width = toplevel_window.winfo_screenwidth()
    screen_height = toplevel_window.winfo_screenheight()
    # Get current window geometry and extract dimensions
    try:
        geom = toplevel_window.geometry()
        if 'x' in geom and '+' in geom:
            # Parse "800x500+100+50"
            size_part = geom.split('+')[0]
            if 'x' in size_part:
                width, height = map(int, size_part.split('x'))
            else:
                width, height = 800, 500
        else:
            width, height = 800, 500
    except:
        width, height = 800, 500
    if parent_window:
        # Center relative to the parent window
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
    else:
        # Center relative to the screen
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
    toplevel_window.geometry(f'{width}x{height}+{x}+{y}')