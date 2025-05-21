<p align="center">
  <img src="image.png" alt="iso2god-Watchdog GUI Screenshot" width="600"/>
</p>

# �� iso2god-Watchdog

A friendly GUI watchdog for [iso2god-rs](https://github.com/iliazeus/iso2god-rs) that automatically monitors folders and converts Xbox 360 ISOs to Games on Demand (GOD) format! Never manually convert ISOs again - just drop them in a folder and let Watchdog handle the rest.

## ✨ Features

- **iso2god version selection**: Different versions of iso2god-rs perform differently for different users. Easily test to find what works best for you!

For example using 12 threads on my AMD Ryzen 9 6900HS 1.6.0 converts a game in 15 minutes or less, while versions 1.7.0 - 1.8.0 can take 45 - 180 minutes!

- 🔍 **Automatic Folder Watching**: Just point it to a folder and it'll detect new ISOs automatically
- 🎯 **Smart Queue System**: Handles multiple ISOs in sequence with retry capability
- ⚙️ **Configurable Settings**:
  - Watch & output directory paths
  - Number of processing threads
  - Scan delay for new files
  - Process timeout limits
  - Option to trim unused space
  - Auto-delete ISOs after conversion
- 💾 **Persistent Settings**: Your preferences are saved between sessions
- 📊 **Real-time Progress**: See conversion progress as it happens
- 🎨 **User-Friendly Interface**: Clean and simple design with status updates

## 🚀 Getting Started

### Prerequisites
- Make sure you have Python 3.8 or higher installed
- Windows, Linux, or MacOS system

### Installation
1. Get the code:
   - **Option 1**: Clone the repository
     ```bash
     git clone https://github.com/YOUR_USERNAME/iso2god-Watchdog.git
     cd iso2god-Watchdog
     run watcher.py
     ```
   - **Option 2**: Download as ZIP
     - Click the green "Code" button above
     - Select "Download ZIP"
     - Extract the ZIP file to your preferred location
     - run watcher.py

### Running the Application
1. Navigate to the extracted/cloned folder
2. **LINUX ONLY**: Give the the `iso2god` executables (ex. `linux-1.8.0`) execution permissions using `chmod +x [program name]` 
3. Run the GUI using the provided script for your platform:
   - **Windows**: Double click `run_GUI.bat` or run it from a terminal
   - **Linux/MacOS**: Run `./run_GUI.sh` from a terminal
4. On first run, the required packages will be automatically installed

### Setting Up
1. When the GUI opens:
   - Select your watch folder (where you'll put your ISOs)
   - Select your output folder (where GOD files will be created)
   - Adjust any settings as needed (threads, scan delay, etc.)
2. Click "Start Watching"
3. Drop your ISO files into the watch folder - they'll be converted automatically!

## ⚙️ Configuration Options

- **Watch Directory**: Where to look for new ISO files
- **Output Directory**: Where to save converted GOD files
- **Threads**: Number of processing threads (default: 4)
- **Scan Delay**: Seconds to wait before processing new files (default: 2)
- **Process Timeout**: Maximum minutes for conversion (0 = no limit)
- **Trim Unused Space**: Option to reduce file size
- **Delete ISO**: Automatically remove source ISO after successful conversion

## 🔄 Managing iso2god Versions

The GUI supports multiple versions of the `iso2god` binary for different platforms and versions. To add or update available versions:

1. **Locate the `iso2god` folder**: Inside the project directory, there is a folder named `iso2god`.
2. **Add new binaries**: Place your new `iso2god` binaries in this folder. The filename should follow the pattern:
   - `windows-<version>.exe` (e.g., `windows-1.8.0.exe`)
   - `linux-<version>` (e.g., `linux-1.8.0`)
   - `mac-<version>` (e.g., `mac-1.8.0`)
3. **Remove old versions**: Simply delete the old binary files from the `iso2god` folder if you no longer need them.
4. **Restart the GUI**: The application will automatically detect all valid binaries in the `iso2god` folder and list them in the version dropdown.

> **Tip:** You can keep multiple versions for different platforms and switch between them in the GUI as needed.

## 📝 Notes

- This is a GUI wrapper around [iso2god-rs](https://github.com/iliazeus/iso2god-rs) by iliazeus
- Required packages will be automatically installed on first run
- Settings are stored in `watcher_config.json` next to the script

## 🐛 Troubleshooting

**Fixing `ModuleNotFoundError: No module named 'tkinter'`**
1. Try running the GUI script for your Operating System as:
   - **Windows**: Administrator (`Run as Administrator` in the right click menu)
   - **Linux/MacOS**: sudo/root (running it in the terminal as sudo/root)
2. Try (re)installing tkinter:
     - **Windows**: Make sure that `tkinter` is installed by selecting `Modify` on the installer. ![image](https://github.com/user-attachments/assets/611f117d-6ae6-44ae-89e6-de3bbeb482ac)
     
     If you have confirmed it is installed and running the batch file as Admin doesn't fix the issue, reinstall python.

     
    - **Linux**: Install `tkinter` for your distro:
    
        **Ubuntu/Debian**: `sudo apt-get install python3-tk`

        **Fedora**: `sudo dnf install python3-tkinter`
        
        **Arch**: `sudo pacman -S tk`
        
        **REHL/CentOS6/CentOS7**: `sudo yum install -y python3-tkinter`
        
        **OpenSUSE**: `sudo zypper in -y python-tk`


   - **MacOS**: Install `tkinter` using brew:
        `brew install python-tk`


**Fixing `File access error: [Errno 13] Permission denied: [location of executable]. Retrying in 120 seconds... (Attempt */3)`**

  1. Run the GUI script as sudo/root
     
  2. Make sure that the `iso2god` executables (ex. `linux-1.8.0`) have execution permissions using `chmod +x [program name]`


      
If you encounter other issues:
1. Check the status messages in the main window
2. Make sure you have write permissions in both directories
3. Try increasing the scan delay if files are skipped
4. Check that ISOs aren't in use by other programs

## 📜 Requirements

- Python 3.8 or higher
- watchdog==4.0.0
- pyinstaller==6.13.0 (for building executable)

## 🙏 Credits

- Original iso2god-rs tool by [iliazeus](https://github.com/iliazeus/iso2god-rs)
- GUI wrapper and watcher functionality by [StonedModder](https://x.com/StonedModder)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 
