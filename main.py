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
from PIL import Image
import webbrowser

# FIXED: fix win shift s (0 bytes)


class FolderMonitorHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.previous_files = set(os.listdir(folder_path))


    def on_any_event(self, event):
        current_files = set(os.listdir(self.folder_path))
        added_files = current_files - self.previous_files

        for file in added_files:
            if file.endswith(".png"):
                try:
                    window = gw.getActiveWindow()
                    app_name = "Unknown" # default app_name name
                    if window:
                        parts = window.title.split(' - ')
                        app_name = parts[-1].strip()

                    if json_data['group_in_screenshots']:
                        app_folder = os.path.join(self.folder_path, app_name)
                    else:
                        app_folder = os.path.join(self.folder_path, "..", app_name)

                    print(f"app_folder: {app_folder}")
                    os.makedirs(app_folder, exist_ok=True)

                    
                    new_filename = f"Screenshot{len(os.listdir(app_folder))+1}.png"

                    time.sleep(0.5)

                    src_path = os.path.join(self.folder_path, file)
                    dest_path = os.path.join(app_folder, new_filename)
                    shutil.move(src_path, dest_path)

                except Exception as e:
                    pass

        self.previous_files = current_files
def add_to_startup():
    """Add the application to Windows startup using a batch file."""
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "main.exe")

        startup_folder = os.path.join(
            os.environ.get('APPDATA'),
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )

        if not os.path.exists(startup_folder):
            os.makedirs(startup_folder)

        bat_file_path = os.path.join(startup_folder, 'screenshot_organizer.bat')

        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(f'@echo off\nstart "" "{exe_path}"')

        return True

    except Exception as e:
        print(f"Failed to add to startup: {str(e)}")
        return False

def create_icon():
    """Create tray icon image"""
    # Assuming icon.ico exists in same directory as script
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    return Image.open(icon_path)



def toggle_startup():
    if is_on_startup():
        os.remove(f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\screenshot_organizer.bat")
    else:
        add_to_startup()

def is_on_startup():
    if os.path.exists(f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\screenshot_organizer.bat"):
        return True
    
    return False

def toggle_subfolders():
    if json_data['group_in_screenshots'] == True:
        json_data['group_in_screenshots'] = False
    else:
        json_data['group_in_screenshots'] = True    
    
    with open(userjsonfile,'w') as f: 
        json.dump(json_data,f)

def quit_action(icon, item, observer):
    observer.stop()
    observer.join()
    icon.stop()
    os._exit(0)

if __name__ == "__main__":

    userjsonfile = 'user.json'
    json_data = {
        "group_in_screenshots": False
    }
    
    if not os.path.exists(userjsonfile):
        with open(userjsonfile,'w') as f: 
            json.dump(json_data,f)
    else:
        with open(userjsonfile,'r') as f: 
            json_data = json.load(f)

    
    folder_to_monitor = f"C:\\Users\\{os.getlogin()}\\Pictures\\Screenshots"

    os.makedirs(folder_to_monitor, exist_ok=True)

    if os.path.isdir(folder_to_monitor):
        event_handler = FolderMonitorHandler(folder_to_monitor)
        observer = Observer()
        observer.schedule(event_handler, folder_to_monitor, recursive=False)

        observer_thread = threading.Thread(target=observer.start)
        observer_thread.daemon = True
        observer_thread.start()
        

        # Create Icon
        icon_image = create_icon()
        icon_menu = Menu(MenuItem('Go to GitHub', lambda:webbrowser.open("https://github.com/saleh-c4/Screenshot-Organizer")),
            MenuItem('Group in screnshots', toggle_subfolders, checked=lambda item:json_data['group_in_screenshots']),
            MenuItem('start with pc', toggle_startup, checked=lambda item:is_on_startup()),
            Menu.SEPARATOR,
            MenuItem('Quit', lambda icon, item: quit_action(icon, item, observer)))

        tray_icon = Icon(
            name="Screenshot Organizer",
            icon=icon_image,
            title="Screenshot Organizer",
            menu=icon_menu
        )
        tray_icon.run()













