import os
import sys
import json
import threading
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygetwindow as gw
from pystray import Icon, Menu, MenuItem
from PIL import Image
import webbrowser

CONFIG_FILE = "user_info.json"


def get_user_config():
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
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_sizes = {}  # Track sizes of files to detect changes

    def get_next_filename(self, app_folder):
        existing_files = os.listdir(app_folder)
        screenshot_files = [f for f in existing_files if f.startswith("screenshot") and f.endswith(".png")]

        max_num = 0
        for file in screenshot_files:
            try:
                num = int(file[10:-4])
                max_num = max(max_num, num)
            except ValueError:
                continue

        return f"screenshot{max_num + 1}.png"

    def move_file(self, file):
        try:
            window = gw.getActiveWindow()
            app_name = "Unknown"
            if window:
                parts = window.title.split(' - ')
                app_name = parts[-1].strip() or "Unknown"

            app_folder = os.path.join(self.folder_path, "..", app_name)
            os.makedirs(app_folder, exist_ok=True)

            new_filename = self.get_next_filename(app_folder)

            src_path = os.path.join(self.folder_path, file)
            dest_path = os.path.join(app_folder, new_filename)
            shutil.move(src_path, dest_path)

            if file in self.file_sizes:
                del self.file_sizes[file]

        except Exception as e:
            print(f"Error moving file: {e}")

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".png"):
            filename = os.path.basename(event.src_path)
            self.file_sizes[filename] = 0  # Start tracking

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".png"):
            filename = os.path.basename(event.src_path)
            full_path = os.path.join(self.folder_path, filename)

            try:
                current_size = os.path.getsize(full_path)
                prev_size = self.file_sizes.get(filename, 0)

                if current_size > 0 and current_size != prev_size:
                    self.file_sizes[filename] = current_size
                    self.move_file(filename)
            except FileNotFoundError:
                pass  # Sometimes file might be gone before we can read it


def quit_action(icon, item, observer):
    observer.stop()
    observer.join()
    icon.stop()
    os._exit(0)


def create_image():
    if hasattr(sys, '_MEIPASS'):
        script_dir = sys._MEIPASS
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(script_dir, "screen_shot_org.ico")
    return Image.open(icon_path)



def is_startup_enabled():
    user_config = get_user_config()
    startup_folder = os.path.join(
        user_config["username"],
        "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    startup_app_path = os.path.join(startup_folder, "main.exe")
    return os.path.exists(startup_app_path)


def toggle_startup():
    user_config = get_user_config()
    startup_folder = os.path.join(
        user_config["user_profile"],
        "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    app_exe_name = "main.exe"
    original_app_path = sys.executable
    startup_app_path = os.path.join(startup_folder, app_exe_name)

    if not os.path.exists(startup_app_path):
        shutil.copy(original_app_path, startup_app_path)
    else:
        os.remove(startup_app_path)


def open_github():
    webbrowser.open("https://github.com/saleh-c4/Screenshot-Organizer")


def main():
    user_config = get_user_config()
    folder_to_monitor = user_config["screenshots_folder"]

    if os.path.isdir(folder_to_monitor):
        event_handler = FolderMonitorHandler(folder_to_monitor)
        observer = Observer()
        observer.schedule(event_handler, folder_to_monitor, recursive=False)

        observer_thread = threading.Thread(target=observer.start)
        observer_thread.daemon = True
        observer_thread.start()

        icon_image = create_image()
        icon_menu = Menu(
            MenuItem('Go to GitHub', open_github),
            MenuItem('start with pc', toggle_startup, checked=lambda item: is_startup_enabled()),
            Menu.SEPARATOR,
            MenuItem('Quit', lambda icon, item: quit_action(icon, item, observer))
        )

        tray_icon = Icon(
            name="Screenshot Organizer",
            icon=icon_image,
            title="Screenshot Organizer",
            menu=icon_menu
        )
        tray_icon.run()


if __name__ == "__main__":
    main()
