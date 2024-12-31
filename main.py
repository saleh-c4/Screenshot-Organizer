import os
import sys
import json
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygetwindow as gw
import shutil
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

CONFIG_FILE = "user_info.json"


def get_user_config():
    """Retrieve or create user configuration for the screenshot directory."""
    user_name = os.getlogin()
    default_screenshot_folder = f"C:\\Users\\{user_name}\\Pictures\\Screenshots"

    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    
    user_config = {
        "username": user_name,
        "screenshots_folder": default_screenshot_folder
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(user_config, f, indent=4)
    return user_config


class FolderMonitorHandler(FileSystemEventHandler):
    """Monitor a folder for added files and organize screenshots."""
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.previous_files = set(os.listdir(folder_path))

    def on_any_event(self, event):
        current_files = set(os.listdir(self.folder_path))
        added_files = current_files - self.previous_files

        for file in added_files:
            if file.endswith(".png"):  # Only handle screenshot files
                try:
                    # Get active application name
                    window = gw.getActiveWindow()
                    app_name = "Unknown"
                    if window:
                        parts = window.title.split(' - ')
                        app_name = parts[-1].strip()

                    # Create a folder for the app if it doesn't exist
                    app_folder = os.path.join(self.folder_path, "..", app_name)
                    os.makedirs(app_folder, exist_ok=True)

                    # Move the screenshot to the app's folder
                    src_path = os.path.join(self.folder_path, file)
                    dest_path = os.path.join(app_folder, file)
                    shutil.move(src_path, dest_path)
                except Exception as e:
                    print(f"Error organizing file {file}: {e}")

        self.previous_files = current_files


def quit_action(icon, item, observer):
    """Exit the program when 'Quit' is clicked."""
    observer.stop()
    observer.join()
    icon.stop()
    os._exit(0)


def create_image():
    """Load the custom tray icon image."""
    # Use _MEIPASS for the path when running as an executable
    if hasattr(sys, '_MEIPASS'):
        script_dir = sys._MEIPASS
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(script_dir, "bootythebootleg.ico")
    return Image.open(icon_path)


def main():
    user_config = get_user_config()
    if not user_config:
        print("Unable to retrieve or create user configuration.")
        return

    folder_to_monitor = user_config["screenshots_folder"]

    if os.path.isdir(folder_to_monitor):
        event_handler = FolderMonitorHandler(folder_to_monitor)
        observer = Observer()
        observer.schedule(event_handler, folder_to_monitor, recursive=False)

        observer_thread = threading.Thread(target=observer.start)
        observer_thread.daemon = True
        observer_thread.start()

        # Create system tray icon with tooltip
        icon_image = create_image()
        icon_menu = Menu(MenuItem('Quit', lambda icon, item: quit_action(icon, item, observer)))

        tray_icon = Icon(
            name="Screenshot Organizer",
            icon=icon_image,
            title="Screenshot Organizer",  # Tooltip text for system tray
            menu=icon_menu
        )
        tray_icon.run()


if __name__ == "__main__":
    main()
