import os
import sys
import time
import json
import queue
import threading
import subprocess
from pathlib import Path
import re

# Check if pip is installed
def check_pip():
    try:
        import pip
    except ImportError:
        print("ERROR: pip is not installed.")
        sys.exit()   

check_pip()

def install_requirements():
    try:
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        requirements_path = os.path.join(script_dir, "requirements.txt")
        
        if os.path.exists(requirements_path):
            print("Installing requirements...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            print("Requirements installed successfully!")
        else:
            print("requirements.txt not found!")
    except Exception as e:
        print(f"Error installing requirements: {str(e)}")
        sys.exit(1)

# Install requirements before importing them
install_requirements()

import tkinter as tk
from tkinter import ttk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from tkinter import filedialog, messagebox

# Get the directory containing the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ISO2GOD_DIR = os.path.join(SCRIPT_DIR, "iso2god")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "watcher_config.json")

DEFAULT_CONFIG = {
    "watch_dir": "",
    "output_dir": "",
    "trim_unused": False,
    "thread_count": "4",
    "scan_delay": "2",  # Default 2 second scan delay
    "delete_iso": True,  # Default to deleting ISOs after conversion
    "process_timeout": "0",  # 0 means no timeout, otherwise in minutes
    "iso2god_binary": ""
}

class IsoHandler(FileSystemEventHandler):
    def __init__(self, queue, extensions=('.iso',)):
        super().__init__()
        self.queue = queue
        self.extensions = extensions
        self.processing = set()
        self.last_event_time = {}
        self.scan_delay = 2.0  # Default delay
        self._stop_event = threading.Event()

    def set_scan_delay(self, delay):
        try:
            self.scan_delay = float(delay)
        except ValueError:
            self.scan_delay = 2.0

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(self.extensions):
            current_time = time.time()
            
            # Check if we've seen this file before and if enough time has passed
            if event.src_path in self.last_event_time:
                if current_time - self.last_event_time[event.src_path] < self.scan_delay:
                    return  # Not enough time has passed
            
            self.last_event_time[event.src_path] = current_time
            
            if event.src_path not in self.processing:
                self.queue.put(event.src_path)
                self.processing.add(event.src_path)

class DirectoryWatcher(threading.Thread):
    def __init__(self, path, handler):
        super().__init__(daemon=True)
        self.path = path
        self.handler = handler
        self._stop_event = threading.Event()
        self._last_check = {}

    def stop(self):
        self._stop_event.set()

    def check_directory(self):
        try:
            current_files = set()
            for file in os.listdir(self.path):
                if file.lower().endswith('.iso'):
                    filepath = os.path.join(self.path, file)
                    current_files.add(filepath)
                    
                    # Check if this is a new file or if enough time has passed since last check
                    current_time = time.time()
                    if filepath not in self._last_check:
                        self._last_check[filepath] = current_time
                        # Simulate a file creation event
                        event = FileCreatedEvent(filepath)
                        self.handler.on_created(event)
            
            # Clean up old files from last_check
            for filepath in list(self._last_check.keys()):
                if filepath not in current_files:
                    del self._last_check[filepath]
                    
        except Exception as e:
            print(f"Error checking directory: {e}")

    def run(self):
        while not self._stop_event.is_set():
            self.check_directory()
            time.sleep(1)  # Check every second

class Iso2GodGUI:
    def __init__(self):
        self.app = tk.Tk()
        # Set window icon to icon.ico if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        try:
            if os.path.exists(icon_path):
                self.app.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
        self.app.title("ISO2GOD-rs GUI")
        self.app.geometry("800x600")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', padding=5)
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        
        # Queue for ISO files
        self.iso_queue = queue.Queue()
        
        # Processing flag
        self.is_processing = False
        self.watcher = None
        self.handler = None
        
        # Load saved settings
        self.config = self.load_config()
        
        # Find iso2god binaries
        self.iso2god_binaries = self.find_iso2god_binaries()
        self.selected_iso2god = tk.StringVar()
        # Set default selection from config or first found
        if self.config.get("iso2god_binary") and self.config["iso2god_binary"] in self.iso2god_binaries:
            self.selected_iso2god.set(self.config["iso2god_binary"])
        elif self.iso2god_binaries:
            self.selected_iso2god.set(self.iso2god_binaries[0])
        else:
            self.selected_iso2god.set("")
        
        # Create GUI elements
        self.create_widgets()
        
        # Start the processing thread
        self.process_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.process_thread.start()

        # Add periodic check for GUI responsiveness
        self.check_gui_responsive()

        # Show warning about missing iso2god binaries after all widgets are created
        if not self.iso2god_binaries:
            self.update_status("Warning: No iso2god binaries found in ./iso2god folder!", "error")

    def check_gui_responsive(self):
        """Periodic check to keep GUI responsive"""
        self.app.after(100, self.check_gui_responsive)

    def find_iso2god_binaries(self):
        """Scan iso2god directory for binaries named <os>-<version>[.ext]"""
        binaries = []
        if not os.path.exists(ISO2GOD_DIR):
            return binaries
        # Accept patterns like windows-1.6.0, mac-1.6.0, linux-1.6.0, with or without .exe/.bin/.sh
        pattern = re.compile(r'^(windows|mac|linux)-[\d.]+(\.[a-zA-Z0-9]+)?$')
        for fname in os.listdir(ISO2GOD_DIR):
            fpath = os.path.join(ISO2GOD_DIR, fname)
            if os.path.isfile(fpath):
                if pattern.match(fname):
                    binaries.append(fname)
        return sorted(binaries)

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    config = DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
        except Exception as e:
            self.update_status(f"Error loading config: {e}", "error")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        config = {
            "watch_dir": self.watch_path.get(),
            "output_dir": self.output_path.get(),
            "trim_unused": self.trim_var.get(),
            "thread_count": self.thread_count.get(),
            "scan_delay": self.scan_delay.get(),
            "delete_iso": self.delete_iso_var.get(),
            "process_timeout": self.process_timeout.get(),
            "iso2god_binary": self.selected_iso2god.get()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.update_status(f"Error saving config: {e}", "error")

    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.app)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Watch Directory Frame
        watch_frame = ttk.Frame(main_container)
        watch_frame.pack(fill="x", pady=5)
        
        ttk.Label(watch_frame, text="Watch Directory:").pack(side="left")
        self.watch_path = ttk.Entry(watch_frame)
        self.watch_path.pack(side="left", fill="x", expand=True, padx=5)
        self.watch_path.insert(0, self.config.get("watch_dir", ""))
        
        browse_btn = ttk.Button(watch_frame, text="Browse", command=self.browse_watch_dir)
        browse_btn.pack(side="right")

        # Output Directory Frame
        output_frame = ttk.Frame(main_container)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(side="left")
        self.output_path = ttk.Entry(output_frame)
        self.output_path.pack(side="left", fill="x", expand=True, padx=5)
        self.output_path.insert(0, self.config.get("output_dir", ""))
        
        browse_output_btn = ttk.Button(output_frame, text="Browse", command=self.browse_output_dir)
        browse_output_btn.pack(side="right")

        # Iso2God Binary Selection Frame
        iso2god_frame = ttk.Frame(main_container)
        iso2god_frame.pack(fill="x", pady=5)
        ttk.Label(iso2god_frame, text="iso2god Version:").pack(side="left")
        self.iso2god_dropdown = ttk.Combobox(iso2god_frame, textvariable=self.selected_iso2god, values=self.iso2god_binaries, state="readonly", width=40)
        self.iso2god_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        self.iso2god_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_config())

        # Settings Frame
        settings_frame = ttk.Frame(main_container)
        settings_frame.pack(fill="x", pady=5)

        # Left side settings
        left_settings = ttk.Frame(settings_frame)
        left_settings.pack(side="left", fill="x", expand=True)

        # Thread Count Option
        thread_frame = ttk.Frame(left_settings)
        thread_frame.pack(side="left", padx=5)
        ttk.Label(thread_frame, text="Threads:").pack(side="left")
        self.thread_count = ttk.Entry(thread_frame, width=5)
        self.thread_count.insert(0, self.config.get("thread_count", "4"))
        self.thread_count.pack(side="left", padx=2)

        # Scan Delay Option
        delay_frame = ttk.Frame(left_settings)
        delay_frame.pack(side="left", padx=5)
        ttk.Label(delay_frame, text="Scan Delay (sec):").pack(side="left")
        self.scan_delay = ttk.Entry(delay_frame, width=5)
        self.scan_delay.insert(0, self.config.get("scan_delay", "2"))
        self.scan_delay.pack(side="left", padx=2)

        # Process Timeout Option
        timeout_frame = ttk.Frame(left_settings)
        timeout_frame.pack(side="left", padx=5)
        ttk.Label(timeout_frame, text="Process Timeout (min):").pack(side="left")
        self.process_timeout = ttk.Entry(timeout_frame, width=5)
        self.process_timeout.insert(0, self.config.get("process_timeout", "0"))
        self.process_timeout.pack(side="left", padx=2)
        ttk.Label(timeout_frame, text="(0 = no timeout)").pack(side="left", padx=2)

        # Checkboxes Frame
        checkbox_frame = ttk.Frame(main_container)
        checkbox_frame.pack(fill="x", pady=5)

        # Trim Option
        self.trim_var = tk.BooleanVar(value=self.config.get("trim_unused", False))
        trim_check = ttk.Checkbutton(checkbox_frame, text="Trim unused space", variable=self.trim_var)
        trim_check.pack(side="left", padx=5)

        # Delete ISO Option
        self.delete_iso_var = tk.BooleanVar(value=self.config.get("delete_iso", True))
        delete_check = ttk.Checkbutton(checkbox_frame, text="Delete ISO after conversion", variable=self.delete_iso_var)
        delete_check.pack(side="left", padx=5)

        # Current Game Title Display (Read-only)
        game_frame = ttk.Frame(main_container)
        game_frame.pack(fill="x", pady=5)
        ttk.Label(game_frame, text="Current Game:").pack(side="left")
        self.game_title_var = tk.StringVar(value="None")
        self.game_title_display = ttk.Entry(game_frame, textvariable=self.game_title_var, state="readonly")
        self.game_title_display.pack(side="left", fill="x", expand=True, padx=5)

        # Control Buttons Frame
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill="x", pady=5)

        self.start_btn = ttk.Button(control_frame, text="Start Conversion", command=self.toggle_watching)
        self.start_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(control_frame, text="Clear Queue", command=self.clear_queue)
        self.clear_btn.pack(side="left", padx=5)

        # Status Bar
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Status: Idle", font=("TkDefaultFont", 10, "bold"))
        self.status_label.pack(side="left", fill="x", expand=True)

        # Status and Queue Display with better visibility
        self.status_text = tk.Text(main_container, height=20, font=("Consolas", 10))
        self.status_text.pack(fill="both", expand=True, pady=5)
        self.status_text.tag_configure("found", foreground="blue", font=("Consolas", 10, "bold"))
        self.status_text.tag_configure("success", foreground="green", font=("Consolas", 10, "bold"))
        self.status_text.tag_configure("error", foreground="red", font=("Consolas", 10, "bold"))
        self.status_text.configure(state="disabled")

    def browse_watch_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.watch_path.delete(0, "end")
            self.watch_path.insert(0, directory)
            self.save_config()

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.delete(0, "end")
            self.output_path.insert(0, directory)
            self.save_config()

    def update_status(self, message, status_type=None, current_index=None, total_count=None):
        """Update both the status bar and the status text area, with optional queue info"""
        self.status_text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")

        # Add queue info to the message if provided
        queue_info = ""
        if current_index is not None and total_count is not None:
            queue_info = f" (Processing {current_index} of {total_count})"

        # Update status label
        if status_type == "found":
            self.status_label.configure(text=f"Status: ISO Found - {os.path.basename(message)}{queue_info}")
        elif status_type == "success":
            self.status_label.configure(text=f"Status: Conversion Complete{queue_info}")
        elif status_type == "error":
            self.status_label.configure(text=f"Status: Error Occurred{queue_info}")
        elif status_type == "watching":
            self.status_label.configure(text=f"Status: Watching - {message}{queue_info}")
        else:
            self.status_label.configure(text=f"Status: {message}{queue_info}")

        # Add message to text area with appropriate tag
        if status_type:
            self.status_text.insert("end", f"{timestamp} - ", "")
            self.status_text.insert("end", f"{message}{queue_info}\n", status_type)
        else:
            self.status_text.insert("end", f"{timestamp} - {message}{queue_info}\n")

        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def toggle_watching(self):
        if not self.watcher:
            try:
                watch_dir = self.watch_path.get()
                output_dir = self.output_path.get()
                
                if not watch_dir or not output_dir:
                    messagebox.showerror("Error", "Please select both watch and output directories")
                    return
                    
                if not os.path.exists(watch_dir) or not os.path.exists(output_dir):
                    messagebox.showerror("Error", "One or both directories do not exist")
                    return

                # Save current settings
                self.save_config()

                self.handler = IsoHandler(self.iso_queue)
                
                # Update scan delay from UI
                try:
                    scan_delay = float(self.scan_delay.get())
                    self.handler.set_scan_delay(scan_delay)
                except ValueError:
                    messagebox.showwarning("Warning", "Invalid scan delay value. Using default (2 seconds)")
                    self.scan_delay.delete(0, "end")
                    self.scan_delay.insert(0, "2")
                    self.handler.set_scan_delay(2.0)

                self.watcher = DirectoryWatcher(watch_dir, self.handler)
                self.watcher.start()
                
                self.start_btn.configure(text="Stop Watching")
                self.update_status(watch_dir, "watching")
                self.is_processing = True
                
            except Exception as e:
                self.update_status(f"Error starting watcher: {str(e)}", "error")
                if self.watcher:
                    try:
                        self.watcher.stop()
                    except:
                        pass
                self.watcher = None
                messagebox.showerror("Error", f"Failed to start converting: {str(e)}")
        else:
            self.stop_watching()

    def stop_watching(self):
        if self.watcher:
            try:
                self.watcher.stop()
                self.watcher = None
                self.start_btn.configure(text="Start Conversion")
                self.update_status("Stopped watching")
                self.is_processing = False
            except Exception as e:
                self.update_status(f"Error stopping watcher: {str(e)}", "error")
                messagebox.showerror("Error", f"Error stopping watcher: {str(e)}")

    def clear_queue(self):
        while not self.iso_queue.empty():
            try:
                self.iso_queue.get_nowait()
            except queue.Empty:
                break
        self.update_status("Queue cleared")

    def process_queue(self):
        while True:
            if self.is_processing:
                try:
                    total_count = self.iso_queue.qsize()
                    if total_count == 0:
                        time.sleep(0.1)
                        continue
                    # Calculate the current index (1-based)
                    current_index = total_count - self.iso_queue.qsize() + 1
                    iso_path = self.iso_queue.get(timeout=1)
                    self.process_iso(iso_path, current_index=current_index, total_count=total_count)
                except queue.Empty:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    def process_iso(self, iso_path, current_index=None, total_count=None):
        max_retries = 3  # Maximum number of retry attempts
        retry_delay = 120  # Delay between retries in seconds
        current_try = 0
        last_progress_time = 0  # Track last progress update
        progress_update_interval = 10  # Update every 10 seconds
        # --- v1.6.0 and below edge case support ---
        def is_legacy_version(binary_name):
            import re
            m = re.search(r'-(\d+\.\d+\.\d+)', binary_name)
            if m:
                version = m.group(1)
                # Compare as tuple of ints
                version_tuple = tuple(map(int, version.split('.')))
                return version_tuple <= (1, 6, 0)
            return False
        # --- end legacy support ---
        try:
            # Update the current game title display
            filename = os.path.basename(iso_path)
            game_title = os.path.splitext(filename)[0]
            self.game_title_var.set(game_title)
            self.update_status(f"Found new ISO: {filename}", "found", current_index=current_index, total_count=total_count)
            # Get the path to iso2god binary from selection
            iso2god_binary = self.selected_iso2god.get()
            if not iso2god_binary:
                self.update_status("No iso2god binary selected!", "error")
                return
            iso2god_path = os.path.join(ISO2GOD_DIR, iso2god_binary)
            if not os.path.exists(iso2god_path):
                self.update_status(f"iso2god binary not found: {iso2god_path}", "error")
                return
            legacy_mode = is_legacy_version(iso2god_binary)
            while current_try < max_retries:
                try:
                    # Check if file is accessible before attempting conversion
                    try:
                        with open(iso_path, 'rb') as test_file:
                            pass
                    except PermissionError:
                        if current_try < max_retries - 1:
                            self.update_status(f"File {filename} is locked. Retrying in {retry_delay} seconds... (Attempt {current_try + 1}/{max_retries})", "error", current_index=current_index, total_count=total_count)
                            time.sleep(retry_delay)
                            current_try += 1
                            continue
                        else:
                            self.update_status(f"Skipping {filename} - File remained locked after {max_retries} attempts", "error", current_index=current_index, total_count=total_count)
                            return
                    cmd = [iso2god_path, iso_path, self.output_path.get()]
                    # Add optional arguments
                    if self.trim_var.get():
                        cmd.append("--trim")
                    thread_count = self.thread_count.get()
                    # Only add -j if not legacy
                    add_j = thread_count.isdigit() and not legacy_mode
                    if add_j:
                        cmd.extend(["-j", thread_count])
                    # Get timeout value in minutes (0 means no timeout)
                    try:
                        timeout_minutes = float(self.process_timeout.get())
                        timeout_seconds = timeout_minutes * 60 if timeout_minutes > 0 else None
                    except ValueError:
                        timeout_seconds = None
                        self.update_status("Invalid timeout value, proceeding without timeout", "error")
                    self.update_status(f"Starting conversion of {filename}...", current_index=current_index, total_count=total_count)
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1  # Line buffered
                    )
                    # Store the last output line for progress updates
                    last_output = ""
                    conversion_start_time = time.time()
                    # Use separate thread for reading output to prevent blocking
                    error_detected = {"unexpected_j": False}
                    def read_output(pipe, is_error=False):
                        nonlocal last_output
                        while True:
                            line = pipe.readline()
                            if not line:
                                break
                            line = line.strip()
                            if line:
                                # --- legacy error detection ---
                                if is_error and legacy_mode and "unexpected argument '-j' found" in line:
                                    error_detected["unexpected_j"] = True
                                # --- end legacy error detection ---
                                # Check for file access errors in the output
                                if is_error and ("process cannot access the file" in line or 
                                               "being used by another process" in line):
                                    raise PermissionError(line)
                                # Update progress immediately for part file updates
                                if "writing part files:" in line:
                                    self.status_label.configure(text=f"Status: {line}")
                                    self.app.update_idletasks()
                                self.update_status(line, "error" if is_error else None)
                                if not is_error:
                                    last_output = line
                                # Keep GUI responsive
                                self.app.update_idletasks()
                    # Start output reader threads
                    stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
                    stderr_thread = threading.Thread(target=read_output, args=(process.stderr, True))
                    stdout_thread.daemon = True
                    stderr_thread.daemon = True
                    stdout_thread.start()
                    stderr_thread.start()
                    # Wait for process with optional timeout and progress updates
                    while process.poll() is None:
                        current_time = time.time()
                        # Check for timeout
                        if timeout_seconds and current_time - conversion_start_time > timeout_seconds:
                            process.terminate()
                            time.sleep(1)
                            if process.poll() is None:
                                process.kill()
                            self.update_status(f"Skipping {filename} - Process timed out after {timeout_minutes} minutes", "error", current_index=current_index, total_count=total_count)
                            return
                        # Only show elapsed time if we haven't seen a progress update recently
                        if current_time - last_progress_time >= progress_update_interval and not "writing part files:" in last_output:
                            elapsed_minutes = (current_time - conversion_start_time) / 60
                            self.update_status(
                                f"Converting {filename} - "
                                f"Time elapsed: {int(elapsed_minutes)} minutes - "
                                f"Last status: {last_output}", current_index=current_index, total_count=total_count
                            )
                            last_progress_time = current_time
                        # Keep GUI responsive without consuming CPU
                        self.app.update()
                        time.sleep(0.1)  # Small sleep to prevent CPU spinning
                    # Get final return code
                    return_code = process.poll()
                    # Wait for output threads to finish
                    stdout_thread.join(1)
                    stderr_thread.join(1)
                    # --- legacy retry logic ---
                    if legacy_mode and error_detected["unexpected_j"] and add_j:
                        self.update_status("Detected '-j' error for legacy iso2god. Retrying without '-j'...", "error", current_index=current_index, total_count=total_count)
                        legacy_mode = True  # Ensure legacy mode stays True
                        current_try += 1
                        continue  # Retry without -j
                    # --- end legacy retry logic ---
                    if return_code == 0:
                        elapsed_minutes = (time.time() - conversion_start_time) / 60
                        self.update_status(
                            f"Successfully converted: {filename} "
                            f"(Total time: {int(elapsed_minutes)} minutes)", 
                            "success", current_index=current_index, total_count=total_count
                        )
                        # Delete the original ISO if option is enabled and still processing
                        if self.delete_iso_var.get() and self.is_processing:
                            try:
                                os.remove(iso_path)
                                self.update_status(f"Deleted original ISO: {filename}", "success", current_index=current_index, total_count=total_count)
                            except Exception as e:
                                self.update_status(f"Error deleting ISO {filename}: {str(e)}", "error", current_index=current_index, total_count=total_count)
                        elif self.delete_iso_var.get() and not self.is_processing:
                            self.update_status(f"ISO not deleted because processing was stopped: {filename}", current_index=current_index, total_count=total_count)
                        else:
                            self.update_status(f"ISO kept (delete option disabled): {filename}", current_index=current_index, total_count=total_count)
                        return  # Success - exit retry loop
                    else:
                        error_msg = f"Error converting {filename}: Process returned {return_code}"
                        if current_try < max_retries - 1:
                            self.update_status(f"{error_msg}. Retrying in {retry_delay} seconds... (Attempt {current_try + 1}/{max_retries})", "error", current_index=current_index, total_count=total_count)
                            time.sleep(retry_delay)
                            current_try += 1
                        else:
                            self.update_status(f"Skipping {filename} - {error_msg} after {max_retries} attempts", "error", current_index=current_index, total_count=total_count)
                            return
                except PermissionError as e:
                    if current_try < max_retries - 1:
                        self.update_status(f"File access error: {str(e)}. Retrying in {retry_delay} seconds... (Attempt {current_try + 1}/{max_retries})", "error", current_index=current_index, total_count=total_count)
                        time.sleep(retry_delay)
                        current_try += 1
                    else:
                        self.update_status(f"Skipping {filename} - File access error after {max_retries} attempts: {str(e)}", "error", current_index=current_index, total_count=total_count)
                        return
                except Exception as e:
                    self.update_status(f"Skipping {filename} - Unexpected error: {str(e)}", "error", current_index=current_index, total_count=total_count)
                    return
        finally:
            # Always clean up, regardless of success or failure
            self.game_title_var.set("None")  # Reset the game title display
            if iso_path in self.handler.processing:
                self.handler.processing.remove(iso_path)
            self.iso_queue.task_done()
            self.update_status("Ready for next file in queue", current_index=current_index, total_count=total_count)

    def run(self):
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    def on_closing(self):
        try:
            self.save_config()
            if self.watcher:
                self.stop_watching()
            self.app.quit()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            self.app.destroy()

if __name__ == "__main__":
    app = Iso2GodGUI()
    app.run() 
