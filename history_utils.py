# -*- coding: utf-8 -*-
"""
History ve Utility fonksiyonları
"""
import os
import json

HISTORY_FILE = "download_history.json"

def load_history():
    """Loads download history - only for URL tracking"""
    history = {"urls": [], "files": []}
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, HISTORY_FILE)
    
    # Load the saved history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    # Ensure files list exists but don't modify it here
    if "files" not in history:
        history["files"] = []
    
    return history

def save_history(history):
    """Saves the download history and syncs it with the folder"""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, HISTORY_FILE)
    
    # First, scan the folder
    music_folder = os.path.join(script_dir, "Music")
    if os.path.exists(music_folder):
        # Remove duplicates and files that are no longer in the folder
        history["files"] = list(dict.fromkeys(history["files"]))  # Remove duplicates
        history["files"] = [f for f in history["files"] if os.path.exists(os.path.join(music_folder, f))]
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass
