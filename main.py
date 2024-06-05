import sys
from tray_manager import TrayManager, CheckBox, Button
import os

from settings_manager import SettingsManager, SettingsWindow

class AlcasarAuto:
    def __init__(self) -> None:
        self.tray = None
        self.settings_manager = SettingsManager()
        self.settings_window = SettingsWindow()

    def connect(self):
        print("Connect")

    def disconnect(self):
        print("Disconnect")

    def open_settings(self):
        print("Open Settings")

    def enable_auto_connect(self):
        print("Enable auto connect")
        self.settings_manager.set("auto_connect", True)

    def disable_auto_connect(self):
        print("Disable auto connect")
        self.settings_manager.set("auto_connect", False)
        
    def quit_alcasarauto(self, *_):
        print("Exiting AlcasarAuto...")
        self.tray.kill()
        sys.exit()

    def start_system_tray_icon(self):
        self.tray = TrayManager("Alcasar Auto", run_in_separate_thread=True)
        self.menu = self.tray.menu

        # Load the icon in memory
        self.tray.load_icon(os.path.join("assets", "active_icon.png"), "active")
        self.tray.load_icon(os.path.join("assets", "unactive_icon.png"), "unactive")

        # Set the icon to unactive at start
        self.tray.set_icon("unactive")

        # Create our items
        self.connect_button = Button("Connect", self.connect)
        self.disconnect_button = Button("Disconnect", self.disconnect)
        self.settings_button = Button("Open settings", self.open_settings)
           

        self.auto_connect_checkbox = CheckBox("Auto-Connect", self.settings_manager.get("auto_connect"), 
                                         checked_callback=self.enable_auto_connect, unchecked_callback=self.disable_auto_connect)
        self.quit_button = Button("Quit", self.quit_alcasarauto, (self.tray, ))

        # Add them to our menu
        self.menu.add(self.connect_button)
        self.menu.add(self.disconnect_button)
        self.menu.add(self.settings_button)
        self.menu.add(self.auto_connect_checkbox)
        self.menu.add(self.quit_button)
    
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    alcasar_auto = AlcasarAuto()
    alcasar_auto.start_system_tray_icon()