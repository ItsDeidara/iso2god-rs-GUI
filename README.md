# 🎮 iso2god-Watchdog

A friendly GUI watchdog for [iso2god-rs](https://github.com/iliazeus/iso2god-rs) that automatically monitors folders and converts Xbox 360 ISOs to Games on Demand (GOD) format! Never manually convert ISOs again - just drop them in a folder and let Watchdog handle the rest.

## ✨ Features

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
2. Run `watchdog.py`:
   - **Windows**: Double click `watchdog.py` or run `python watchdog.py` in terminal
   - **Linux/MacOS**: Open terminal and run `python3 watchdog.py`
3. On first run, required packages will be automatically installed

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

## 📝 Notes

- This is a GUI wrapper around [iso2god-rs](https://github.com/iliazeus/iso2god-rs) by iliazeus
- Required packages will be automatically installed on first run
- Settings are stored in `watcher_config.json` next to the script

## 🐛 Troubleshooting

If you encounter issues:
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