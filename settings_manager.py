import os
import tkinter
from tkinter import ttk, Tk, Canvas, BOTH, Frame
import time
import json

import _tkinter

SETTINGS_FOLDER = os.getenv('APPDATA')+"\\AlcasarAuto\\"
SETTINGS_FILE = SETTINGS_FOLDER + "settings.json"


class SettingsManager:
    def __init__(self):
        if not os.path.isdir(SETTINGS_FOLDER):
            os.mkdir(SETTINGS_FOLDER)

        self.settings = {}

        if not os.path.isfile(SETTINGS_FILE):
            self.setup_default_settings()
        else:
            self.load_settings()

    def load_settings(self):
        with open(SETTINGS_FILE, "r") as file:
            self.settings = json.loads(file.read())

    def get(self, key):
        return self.settings[key]

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as file:
            file.write(json.dumps(self.settings))

    def setup_default_settings(self):
        self.settings = {
            "username": "",
            "password": "",
            "auto_connect": False
        }
        self.save_settings()


class SettingsWindow(Tk):
    def __init__(self):
        super().__init__()
        self.width = 220
        self.height = 200

        self.bg_color = "#2F2F3F"
        self.text_color = "#B5B5B5"
        self.field_bg_color = "#43435B"
        self.active_field_bg_color = "#1C1C59"
        self.outline_color = "#8B8B9E"
        self.theme = ttk.Style()
        self.theme.theme_use('clam')
        self.theme.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.theme.configure("TEntry", background=self.bg_color, foreground=self.text_color,
                             fieldbackground=self.field_bg_color, bordercolor=self.outline_color,
                             lightcolor=self.outline_color, darkcolor=self.outline_color)
        self.theme.configure("TButton", background=self.bg_color, foreground=self.text_color,
                             fieldbackground=self.field_bg_color, bordercolor=self.outline_color,
                             lightcolor=self.outline_color, darkcolor=self.outline_color)

        self.theme.map("TButton",
                       background=[('!active', self.bg_color), ('active', self.active_field_bg_color)])

        self.geometry(f"{self.width}x{self.height}+{self.winfo_screenwidth()-self.width-5}+{self.winfo_screenheight()-self.height-50}")
        self.overrideredirect(True)
        self.focus_force()
        self.config(background='grey')
        self.attributes("-transparentcolor", "grey")

        self.base_canvas = Canvas(self, bg="grey", highlightthickness=0)
        self.round_rectangle(0, 0, self.width - 1, self.height - 1, radius=40, width=5, outline="#161616")

        self.title_label = ttk.Label(self.base_canvas, text="AlcasarAuto", font=("Arial", 20), style="TLabel")

        self.credential_frame = Frame(self.base_canvas, bg=self.bg_color)
        self.username_label = ttk.Label(self.credential_frame, text="Username", style="TLabel")
        self.password_label = ttk.Label(self.credential_frame, text="Password", style="TLabel")
        self.username_entry = ttk.Entry(self.credential_frame, style="TEntry")
        self.password_entry = ttk.Entry(self.credential_frame, show="●", style="TEntry")

        self.save_button = ttk.Button(self.base_canvas, text="Save", style="TButton", command=self.close)

        self.username = ""
        self.password = ""

    def close(self):
        self.state = None
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.withdraw()

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):  # Creating a rounded rectangle
        """Draw a rounded rectangle
        By IJ_123 on StackOverflow"""

        points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
                  x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius,
                  x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
                  x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y2 - radius,
                  x1, y1 + radius, x1, y1 + radius, x1, y1]

        return self.base_canvas.create_polygon(points, **kwargs, smooth=True, fill=self.bg_color)
    
    def fill_credentials(self, username, password):
        self.username_entry.delete(0, tkinter.END)
        self.password_entry.delete(0, tkinter.END)
        self.username_entry.insert(0, username)
        self.password_entry.insert(0, password)
    
    def setup(self):
        self.title_label.pack(expand=True)

        self.username_label.grid(row=0, column=0, pady=4)
        self.password_label.grid(row=1, column=0, pady=4)
        self.username_entry.grid(row=0, column=1, padx=8)
        self.password_entry.grid(row=1, column=1, padx=8)
        self.credential_frame.pack(expand=True)

        self.save_button.pack(expand=True, pady=5)

        self.base_canvas.pack(expand=True, fill=BOTH)

    def loop(self):
        self.state = "normal"
        self.update()
        while self.state == "normal":
            self.update()
            try:
                if self.focus_get() is None:
                    self.close()
                    break
            except _tkinter.TclError:
                break
            time.sleep(0.05)

    def get_credentials(self, username, password):
        """Username and password used to prefill entries"""
        self.fill_credentials(username, password)
        self.deiconify()
        self.focus_force()
        self.setup()
        self.loop()
        return self.username, self.password

