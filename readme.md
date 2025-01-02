# Screenshot Organizer

Screenshot Organizer is a Python application that monitors a specified folder for new screenshots and organizes them into subfolders based on the active window's title when the screenshot was taken. The application runs in the background with a system tray icon and can be set to start with Windows.

## Features
- Monitors a specified folder for new screenshots
- Organizes screenshots into subfolders based on the active window's title
- Runs in the background with a system tray icon
- Option to start with Windows

## Requirements
- Python 3.6+
- Windows OS

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/saleh-c4/Screenshot-Organizer.git
    cd Screenshot-Organizer
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Compile the script to an executable (optional):
    ```bash
    pyinstaller --noconfirm --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --name "Screenshot-Organizer" main.py
    ```

## Usage
1. Run the script:
    ```bash
    python main.py
    ```

2. The application will start monitoring the `Screenshots` folder in your `Pictures` directory.

3. Use the system tray icon to access options:
    - **Go to GitHub**: Opens the GitHub repository in your default web browser.
    - **Start with PC**: Toggles whether the application starts with Windows.
    - **Quit**: Exits the application.

## Adding to Startup
The application can be set to start with Windows by using the "Start with PC" option in the system tray menu. This creates a batch file in the Windows startup folder to launch the application on startup.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.