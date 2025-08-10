import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
import yt_dlp
import os
import sys
import json
import hashlib
import threading
print(sys.executable)

# File for download history
HISTORY_FILE = "download_history.json"

def load_history():
    """Loads download history and syncs it with files in the folder"""
    history = {"urls": [], "files": []}
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, HISTORY_FILE)
    
    # First, load the saved history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    # Scan the files in the Music folder
    music_folder = os.path.join(script_dir, "Music")
    if os.path.exists(music_folder):
        existing_files = set(history.get("files", []))
        
        for file in os.listdir(music_folder):
            if any(ext in file.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4']):
                if file not in existing_files:
                    # New file found, add to history
                    history["files"].append(file)
        
        # Remove files from history that are no longer in the folder
        history["files"] = [f for f in history["files"] if os.path.exists(os.path.join(music_folder, f))]
    
    return history

def save_history(history):
    """Saves the download history and syncs it with the folder"""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, HISTORY_FILE)
    
    # First, scan the folder
    music_folder = os.path.join(script_dir, "Music")
    if os.path.exists(music_folder):
        # Remove files from history that are no longer in the folder
        history["files"] = [f for f in history["files"] if os.path.exists(os.path.join(music_folder, f))]
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

def update_history_display():
    """Updates the history display"""
    history = load_history()
    music_count = len(history["files"])
    
    # Update the counter label at the bottom
    count_label.config(text=f"Total Music Downloaded: {music_count}")
    
    # Update the music list (hidden)
    history_text.delete(1.0, tk.END)
    if history["files"]:
        for i, file_name in enumerate(reversed(history["files"][-20:]), 1):  # Last 20 songs
            history_text.insert(tk.END, f"{i}. {file_name}\n")

def toggle_history():
    """Shows/hides the music list"""
    if history_frame.winfo_viewable():
        history_frame.pack_forget()
        toggle_button.config(text="📂 Music List")
    else:
        history_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        toggle_button.config(text="📂 Hide List")

def download_and_convert():
    """
    Downloads the YouTube URL entered by the user and converts it to MP3.
    Runs in the background using threading.
    """
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return
    
    # Check if the URL has been downloaded before
    history = load_history()
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    if url_hash in history["urls"]:
        result = messagebox.askyesno("Warning", "This video has been downloaded before!\n\nDo you still want to download it?")
        if not result:
            return
    
    # Disable the download button
    download_button.config(state='disabled', text="⏳ Downloading")
    status_label.config(text="Starting...")
    
    # Run in the background
    thread = threading.Thread(target=download_worker, args=(url, url_hash))
    thread.daemon = True
    thread.start()

def download_worker(url, url_hash):
    """Performs the download in the background"""
    def progress_hook(d):
        """yt-dlp progress hook"""
        try:
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    root.after(0, lambda p=percent: update_progress(p, f"Downloading... {p:.1f}%"))
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].replace('%', '')
                    try:
                        percent = float(percent_str)
                        root.after(0, lambda p=percent: update_progress(p, f"Downloading... {p:.1f}%"))
                    except:
                        root.after(0, lambda: update_progress(50, "Downloading..."))
                else:
                    root.after(0, lambda: update_progress(50, "Downloading..."))
            elif d['status'] == 'finished':
                root.after(0, lambda: update_progress(100, "Processing..."))
            elif d['status'] == 'error':
                root.after(0, lambda: update_progress(0, "An error occurred..."))
        except Exception:
            # Silently pass progress hook errors
            pass
    
    try:
        # UI update - thread-safe
        root.after(0, lambda: status_label.config(text="Getting video information..."))
        root.after(0, lambda: progress_bar.pack(pady=10, before=status_label))
        root.after(0, lambda: update_progress(0, "Preparing..."))

        # Create the Music folder - where the program is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_folder = os.path.join(script_dir, "Music")
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)

        # Download best quality audio with yt-dlp (MP3 first for car player compatibility)
        ydl_opts = {
            'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f'{music_folder}/%(title)s.%(ext)s',
            'noplaylist': True,
            'concurrent_fragment_downloads': 4,
            'progress_hooks': [progress_hook],
            'retries': 3,
            'fragment_retries': 3,
            'ignoreerrors': False,
            # Works without FFmpeg
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            
            # UI update
            root.after(0, lambda: status_label.config(text=f"Downloading '{title}'..."))
            
            # Download as an audio file directly
            ydl.download([url])
            
            # Find the downloaded file - more robust algorithm
            new_file = None
            
            # First, list all audio files in the folder (including mp4)
            all_audio_files = []
            for file in os.listdir(music_folder):
                if any(ext in file.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4']):
                    file_path = os.path.join(music_folder, file)
                    file_time = os.path.getctime(file_path)
                    all_audio_files.append((file, file_path, file_time))
            
            if all_audio_files:
                # Get the most recently created file
                all_audio_files.sort(key=lambda x: x[2], reverse=True)
                new_file = all_audio_files[0][1]
                
                # If a file matching the title exists, prefer it
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                for file, file_path, _ in all_audio_files:
                    if (safe_title.lower() in file.lower() or 
                        title.lower() in file.lower() or
                        any(word.lower() in file.lower() for word in title.split() if len(word) > 3)):
                        new_file = file_path
                        break
            
            if new_file and os.path.exists(new_file):
                # If the file is .m4a or .mp4, convert it to .mp3 (for car player compatibility)
                if new_file.lower().endswith(('.m4a', '.mp4')):
                    mp3_file = new_file.rsplit('.', 1)[0] + '.mp3'
                    try:
                        os.rename(new_file, mp3_file)
                        new_file = mp3_file
                        root.after(0, lambda: update_progress(100, "Converted to MP3 ✅"))
                    except Exception as rename_error:
                        # If rename fails, use the original file
                        root.after(0, lambda: update_progress(100, "Download complete ✅"))
                
                # Update history
                history = load_history()
                history["urls"].append(url_hash)
                history["files"].append(os.path.basename(new_file))
                save_history(history)
                
                # Make UI updates on the main thread
                root.after(0, lambda: finish_download_success(new_file))
            else:
                # Debug: List files in the folder
                debug_files = []
                if os.path.exists(music_folder):
                    debug_files = [f for f in os.listdir(music_folder) 
                                 if any(ext in f.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4'])]
                
                error_msg = f"Downloaded file not found!\n\nSearched title: {title}\nFiles in folder: {len(debug_files)}\n"
                if debug_files:
                    error_msg += f"Last file: {debug_files[-1] if debug_files else 'None'}"
                
                root.after(0, lambda: finish_download_error(error_msg))

    except Exception as e:
        error_msg = f"An error occurred:\n{str(e)}"
        root.after(0, lambda: finish_download_error(error_msg))

def update_progress(percent, text):
    """Updates the progress bar"""
    try:
        progress_bar['value'] = percent
        status_label.config(text=text)
        root.update_idletasks()
    except:
        pass

def show_success_popup(file_name, file_path):
    """Custom success pop-up window"""
    popup = tk.Toplevel(root)
    popup.title("✅ Success!")
    popup.geometry("550x350")
    popup.configure(bg='#000000')
    popup.resizable(False, False)
    
    # Center the window
    popup.transient(root)
    popup.grab_set()
    
    # Center relative to the main window
    popup.geometry("+{}+{}".format(
        root.winfo_rootx() + 25,
        root.winfo_rooty() + 25
    ))
    
    # Title
    title_label = tk.Label(popup, text="🎵 Download Complete!", 
                          font=("Segoe UI", 16, "bold"), 
                          fg="#00FF00", bg='#000000')
    title_label.pack(pady=15)
    
    # File name
    name_label = tk.Label(popup, text=f"File Name:", 
                         font=("Segoe UI", 11, "bold"), 
                         fg="#FFFFFF", bg='#000000')
    name_label.pack(pady=(10, 5))
    
    file_name_label = tk.Label(popup, text=file_name, 
                              font=("Consolas", 10), 
                              fg="#CCCCCC", bg='#000000', 
                              wraplength=500)
    file_name_label.pack(pady=(0, 10))
    
    # Location
    location_label = tk.Label(popup, text=f"Location:", 
                             font=("Segoe UI", 11, "bold"), 
                             fg="#FFFFFF", bg='#000000')
    location_label.pack(pady=(10, 5))
    
    path_label = tk.Label(popup, text=file_path, 
                         font=("Consolas", 9, "italic", "bold"), 
                         fg="#4080FF", bg='#000000', 
                         wraplength=500)
    path_label.pack(pady=(0, 20))
    
    # Buttons frame
    button_frame = tk.Frame(popup, bg='#000000')
    button_frame.pack(pady=15, side=tk.BOTTOM)
    
    # Open folder button
    def open_folder():
        import subprocess
        subprocess.Popen(f'explorer /select,"{os.path.abspath(os.path.join(file_path, file_name))}"')
        popup.destroy()
    
    open_button = tk.Button(button_frame, text="📁 Open Folder", 
                           command=open_folder,
                           bg="#000080", fg="white", 
                           font=("Segoe UI", 10, "bold"),
                           relief=tk.FLAT, bd=0, width=14, height=2,
                           activebackground="#0000A0", activeforeground="white",
                           cursor="hand2")
    open_button.pack(side=tk.LEFT, padx=15)
    
    # OK button
    ok_button = tk.Button(button_frame, text="✅ OK", 
                         command=popup.destroy,
                         bg="#000080", fg="white", 
                         font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, bd=0, width=14, height=2,
                         activebackground="#0000A0", activeforeground="white",
                         cursor="hand2")
    ok_button.pack(side=tk.LEFT, padx=15)
    
    # Close with ESC
    popup.bind('<Escape>', lambda e: popup.destroy())
    popup.focus_set()

def finish_download_success(new_file):
    """Updates the UI when the download is successful"""
    update_history_display()
    full_path = os.path.abspath(new_file)
    status_label.config(text=f"✅ Success! {os.path.basename(new_file)}")
    
    # Hide the progress bar and re-enable the button
    progress_bar.pack_forget()
    download_button.config(state='normal', text="🎵 Convert and Download")
    
    # Show the custom pop-up
    show_success_popup(os.path.basename(new_file), os.path.dirname(full_path))
    url_entry.delete(0, tk.END)

def finish_download_error(error_msg):
    """Updates the UI when a download error occurs"""
    status_label.config(text="❌ An error occurred.")
    progress_bar.pack_forget()
    download_button.config(state='normal', text="🎵 Convert and Download")
    messagebox.showerror("Error", error_msg)

# --- Interface Section (Tkinter) ---
root = tk.Tk()
root.title("YouTube MP3 Converter")
root.geometry("700x500")
root.resizable(True, True)
root.configure(bg='#000000')  # Solid black background

# Set progress bar style
style = ttk.Style()
style.theme_use('clam')
style.configure('Custom.Horizontal.TProgressbar',
                background='#000080',
                troughcolor='#333333',
                borderwidth=0,
                lightcolor='#000080',
                darkcolor='#000080')

# URL input section - directly on root
url_label = tk.Label(root, text="🎵 YouTube Video URL:", 
                    font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg='#000000')
url_label.pack(pady=(50, 10))

url_entry = tk.Entry(root, width=65, font=("Consolas", 11), bg='#F0F0F0', fg='#000000',
                    relief=tk.FLAT, bd=2, highlightbackground='#CCCCCC', highlightthickness=1,
                    insertbackground='#000000', selectbackground='#4080FF', selectforeground='#FFFFFF')
url_entry.pack(pady=10, ipady=8)

# Buttons section - side by side and equal size
button_frame = tk.Frame(root, bg='#000000')
button_frame.pack(pady=15)

# Main download button - compact
download_button = tk.Button(button_frame, text="🎵 Convert and Download", command=download_and_convert, 
                           bg="#000080", fg="white", font=("Segoe UI", 10, "bold"), 
                           relief=tk.FLAT, bd=0, width=16, height=2,
                           activebackground="#0000A0", activeforeground="white",
                           cursor="hand2")
download_button.pack(side=tk.LEFT, padx=5)

# Music list toggle button - compact
toggle_button = tk.Button(button_frame, text="📂 Music List", command=toggle_history,
                         bg="#000080", fg="white", font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, bd=0, width=16, height=2,
                         activebackground="#0000A0", activeforeground="white",
                         cursor="hand2")
toggle_button.pack(side=tk.LEFT, padx=5)

def refresh_history():
    """Refreshes history by scanning the folder"""
    history = load_history()
    save_history(history)
    update_history_display()
    status_label.config(text="📂 Folder scanned!")
    root.after(2000, lambda: status_label.config(text="Ready ✨"))

refresh_button = tk.Button(button_frame, text="🔄 Refresh", command=refresh_history,
                          bg="#000080", fg="white", font=("Segoe UI", 10, "bold"),
                          relief=tk.FLAT, bd=0, width=12, height=2,
                          activebackground="#0000A0", activeforeground="white",
                          cursor="hand2")
refresh_button.pack(side=tk.LEFT, padx=5)

# Progress bar - initially hidden
progress_bar = ttk.Progressbar(root, length=450, mode='determinate', 
                              style='Custom.Horizontal.TProgressbar')

# Status text
status_label = tk.Label(root, text="Ready ✨", font=("Segoe UI", 11), fg="#FFFFFF", bg='#000000')
status_label.pack(pady=10)

# Music list frame
history_frame = tk.Frame(root, bg='#000000')

history_text = scrolledtext.ScrolledText(history_frame, width=70, height=8, font=("Consolas", 9),
                                       bg="#000000", fg="#FFFFFF", relief=tk.FLAT, bd=1,
                                       selectbackground="#000080", selectforeground="white")
history_text.pack(pady=12, padx=15)

# Bottom section - always at the bottom
bottom_frame = tk.Frame(root, bg='#000000')
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15, padx=15)

# Bottom left corner - Created by GG
created_label = tk.Label(bottom_frame, text="✨ Created by GG", 
                        font=("Segoe UI", 9, "italic"), fg="#888888", bg='#000000')
created_label.pack(side=tk.LEFT)

# Bottom right corner - Counter
count_label = tk.Label(bottom_frame, text="🎵 Total Downloaded: 0", 
                      font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg='#000000')
count_label.pack(side=tk.RIGHT)

# Load history at startup
update_history_display()

root.mainloop()
