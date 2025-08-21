# -*- coding: utf-8 -*-
"""
YouTube İndirme ve Dönüştürme Modülü - Enhanced Debug v2.0
"""
import yt_dlp
import os
import threading
import hashlib
import warnings
import subprocess
import time
import sys
from datetime import datetime
from tkinter import messagebox
from history_utils import load_history, save_history

# Global variables
stop_requested = False
current_thread = None

def debug_print(message, level="INFO"):
    """Terminal çıktısı için debug yazdırma fonksiyonu"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    level_colors = {
        "INFO": "\033[36m",      # Cyan
        "SUCCESS": "\033[32m",   # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "DEBUG": "\033[35m"      # Magenta
    }
    
    reset_color = "\033[0m"
    color = level_colors.get(level, "\033[36m")
    
    print(f"{color}[{timestamp}] [{level}] {message}{reset_color}")
    sys.stdout.flush()

def download_and_convert(url, format_var, url_entry, download_button, stop_button, status_label, progress_bar, root, gui_instance=None):
    """
    Downloads the YouTube URL entered by the user and converts it to MP3.
    Runs in the background using threading.
    """
    debug_print("🎵 YouTube MP3 Converter Started", "INFO")
    debug_print(f"Target URL: {url}", "DEBUG")
    
    if not url:
        debug_print("❌ No URL provided", "ERROR")
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return
    
    # Check if the URL has been downloaded before
    history = load_history()
    url_hash = hashlib.md5(url.encode()).hexdigest()
    debug_print(f"URL Hash: {url_hash[:8]}...", "DEBUG")
    
    # URL hash kontrolü için eski sistem (uyumluluk)
    if url_hash in history["urls"]:
        debug_print("⚠️ Duplicate URL detected (hash match)", "WARNING")
        result = messagebox.askyesno("Warning", "This video has been downloaded before!\n\nDo you still want to download it?")
        if not result:
            debug_print("❌ Download cancelled by user", "INFO")
            if gui_instance:
                gui_instance.reset_progress()
            return
    
    # Yeni sistem: gerçek URL'leri de kaydet
    if "real_urls" not in history:
        history["real_urls"] = []
    
    # Disable the download button and enable stop button
    download_button.config(state='disabled', text="⏳ Downloading...")
    stop_button.config(state='normal')
    
    # GUI instance varsa progress güncelle
    if gui_instance:
        gui_instance.update_progress(5, "🔍 *Analyzing video...*", "", "⏳ *Getting video information...*")
    else:
        status_label.config(text="🔍 Analyzing...")
    
    debug_print("🔄 UI prepared for download", "INFO")
    
    # Reset stop flag
    global stop_requested, current_thread
    stop_requested = False
    
    # Run in the background
    current_thread = threading.Thread(target=download_worker, 
                                    args=(url, url_hash, format_var, url_entry, download_button, 
                                         stop_button, status_label, progress_bar, root, gui_instance))
    current_thread.daemon = True
    current_thread.start()
    debug_print("🚀 Download thread started", "SUCCESS")

def update_progress(percent, text, progress_bar, status_label, root):
    """Updates the progress bar"""
    try:
        progress_bar['value'] = percent
        status_label.config(text=text)
        root.update_idletasks()
    except:
        pass

def download_worker(url, url_hash, format_var, url_entry, download_button, stop_button, status_label, progress_bar, root, gui_instance=None):
    """Performs the download in the background with enhanced debugging"""
    debug_print("🔧 Download worker started", "INFO")
    
    def progress_hook(d):
        """yt-dlp progress hook with debugging"""
        try:
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 50  # İndirme %50'ye kadar
                    speed = d.get('speed', 0)
                    if speed:
                        speed_text = f"⚡ {speed/1024/1024:.1f} MB/s"
                    else:
                        speed_text = ""
                    
                    if percent % 5 == 0:  # Her %5'te bir debug
                        debug_print(f"📥 Download progress: {percent:.1f}%", "INFO")
                    
                    if gui_instance:
                        gui_instance.update_progress(percent, f"📥 *Downloading...* {percent:.1f}%", 
                                                   speed_text, f"⏳ *Getting audio data...*")
                    else:
                        root.after(0, lambda p=percent: update_progress(p, f"Downloading... {p:.1f}%", progress_bar, status_label, root))
                        
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].replace('%', '')
                    try:
                        percent = float(percent_str) * 0.5  # İndirme kısmı %50
                        if gui_instance:
                            gui_instance.update_progress(percent, f"📥 *Downloading...* {percent:.1f}%", 
                                                       "", f"⏳ *Getting audio data...*")
                        else:
                            root.after(0, lambda p=percent: update_progress(p, f"Downloading... {p:.1f}%", progress_bar, status_label, root))
                    except:
                        root.after(0, lambda: update_progress(50, "Downloading...", progress_bar, status_label, root))
                else:
                    root.after(0, lambda: update_progress(50, "Downloading...", progress_bar, status_label, root))
            elif d['status'] == 'finished':
                debug_print("✅ Download finished, starting processing", "SUCCESS")
                root.after(0, lambda: update_progress(100, "Processing...", progress_bar, status_label, root))
            elif d['status'] == 'error':
                debug_print(f"❌ Download error: {d.get('error', 'Unknown error')}", "ERROR")
                root.after(0, lambda: update_progress(0, "An error occurred...", progress_bar, status_label, root))
        except Exception as e:
            debug_print(f"⚠️ Progress hook error: {e}", "WARNING")
    
    try:
        # Check for stop request
        if stop_requested:
            debug_print("🛑 Download stop requested", "WARNING")
            from gui_module import reset_ui
            root.after(0, lambda: reset_ui(download_button, stop_button, progress_bar, status_label))
            return
            
        # Check if already downloaded (duplicate detection)
        history = load_history()
        if url_hash in history.get("urls", []) or url in history.get("real_urls", []):
            debug_print("🔍 Duplicate URL detected, asking user", "WARNING")
            def show_duplicate_warning():
                choice = messagebox.askyesno(
                    " Already Downloaded", 
                    f"This video seems to be already downloaded!\n\n"
                    f"URL: {url}\n\n"
                    f"Do you want to download it again?"
                )
                if choice:
                    debug_print("👤 User chose to re-download", "INFO")
                    # User wants to download again, continue
                    start_download_process(url, url_hash, format_var, url_entry, download_button, stop_button, status_label, progress_bar, root, gui_instance)
                else:
                    debug_print("👤 User cancelled re-download", "INFO")
                    # User cancelled, reset UI
                    from gui_module import reset_ui
                    reset_ui(download_button, stop_button, progress_bar, status_label)
            
            root.after(0, show_duplicate_warning)
            return
        
        debug_print("🎯 Starting fresh download process", "INFO")
        # Start download process
        start_download_process(url, url_hash, format_var, url_entry, download_button, stop_button, status_label, progress_bar, root, gui_instance)
        
    except Exception as e:
        debug_print(f"💥 Critical error in download worker: {e}", "ERROR")
        error_msg = f"An error occurred:\n{str(e)}"
        from gui_module import finish_download_error
        root.after(0, lambda: finish_download_error(error_msg, download_button, stop_button, progress_bar, status_label))

def start_download_process(url, url_hash, format_var, url_entry, download_button, stop_button, status_label, progress_bar, root, gui_instance=None):
    """Starts the actual download process with enhanced debugging"""
    debug_print("🚀 Starting download process", "INFO")
    
    def progress_hook(d):
        """yt-dlp progress hook with debugging"""
        try:
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    root.after(0, lambda p=percent: update_progress(p, f"Downloading... {p:.1f}%", progress_bar, status_label, root))
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].replace('%', '')
                    try:
                        percent = float(percent_str)
                        root.after(0, lambda p=percent: update_progress(p, f"Downloading... {p:.1f}%", progress_bar, status_label, root))
                    except:
                        root.after(0, lambda: update_progress(50, "Downloading...", progress_bar, status_label, root))
                else:
                    root.after(0, lambda: update_progress(50, "Downloading...", progress_bar, status_label, root))
            elif d['status'] == 'finished':
                debug_print("✅ Video download completed", "SUCCESS")
                root.after(0, lambda: update_progress(100, "Processing...", progress_bar, status_label, root))
            elif d['status'] == 'error':
                debug_print(f"❌ Download error in process: {d.get('error', 'Unknown')}", "ERROR")
                root.after(0, lambda: update_progress(0, "An error occurred...", progress_bar, status_label, root))
        except Exception as e:
            debug_print(f"⚠️ Progress hook error in process: {e}", "WARNING")
    
    try:
        # UI update - thread-safe
        debug_print("📱 Updating UI for download start", "DEBUG")
        
        # GUI instance varsa progress entegrasyonu kullan
        if gui_instance:
            def ui_update():
                gui_instance.update_progress(10, "🔍 *Getting video information...*", "", "⏳ *Analyzing YouTube URL...*")
            root.after(0, ui_update)
        else:
            # Fallback traditional method
            root.after(0, lambda: status_label.config(text="Getting video information..."))
            root.after(0, lambda: update_progress(0, "Preparing...", progress_bar, status_label, root))

        # Create the Music folder - where the program is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_folder = os.path.join(script_dir, "Music")
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
            debug_print(f"📁 Created Music folder: {music_folder}", "INFO")
        else:
            debug_print(f"📁 Using existing Music folder: {music_folder}", "DEBUG")

        # Get selected format and set quality/codec accordingly
        selected_format = format_var.get()
        debug_print(f"🎵 Selected format: {selected_format}", "INFO")
        
        if "128k" in selected_format:
            codec, quality = 'mp3', '128'
        elif "192k" in selected_format:
            codec, quality = 'mp3', '192'
        elif "320k" in selected_format:
            codec, quality = 'mp3', '320'
        elif "WAV" in selected_format:
            codec, quality = 'wav', 'best'
        elif "M4A" in selected_format:
            codec, quality = 'm4a', '192'
        else:
            codec, quality = 'mp3', '128'  # Default car-friendly

        # Download best quality audio with yt-dlp
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'outtmpl': f'{music_folder}/%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'retries': 3,
            'ignoreerrors': True,
            'no_warnings': True,
            'ffmpeg_location': r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                }
            }
        }
        
        # Fallback options
        fallback_opts = {
            'format': 'worst',
            'outtmpl': f'{music_folder}/%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'retries': 1,
            'ignoreerrors': True,
            'no_warnings': True,
            'ffmpeg_location': r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
        }
        
        # Add postprocessor
        if codec != 'wav':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': quality,
            }]
            
            if codec == 'mp3':
                ydl_opts['postprocessor_args'] = [
                    '-ar', '44100',
                    '-ac', '2',
                    '-id3v2_version', '3',
                    '-write_id3v1', '1',
                    '-c:a', 'libmp3lame',
                    '-b:a', f'{quality}k'
                ]
        else:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }]
        
        # Try primary download
        download_success = False
        error_message = ""
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                root.after(0, lambda: status_label.config(text=f"Downloading '{title}'..."))
                ydl.download([url])
                download_success = True
                
        except Exception as e:
            error_message = str(e)
            print(f"\n Primary format failed, trying alternative format...")
            
            try:
                root.after(0, lambda: status_label.config(text="Trying alternative format..."))
                root.after(0, lambda: update_progress(50, "Downloading with fallback format...", progress_bar, status_label, root))
                with yt_dlp.YoutubeDL(fallback_opts) as ydl_fallback:
                    info = ydl_fallback.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    ydl_fallback.download([url])
                    download_success = True
                    print(f"\n Fallback download successful!")
                    root.after(0, lambda: update_progress(90, "Download completed ", progress_bar, status_label, root))
                    
            except Exception as fallback_e:
                print(f"\n Both formats failed")
                error_message = f"Primary error: {error_message}\nFallback error: {fallback_e}"
        
        if not download_success:
            messagebox.showerror("Download Error", f"Could not download video.\n\n{error_message}")
            from gui_module import reset_ui
            root.after(0, lambda: reset_ui(download_button, stop_button, progress_bar, status_label))
            return
            
        # Find downloaded file
        print(f" Looking for downloaded file...")
        new_file = None
        
        all_audio_files = []
        for file in os.listdir(music_folder):
            if any(ext in file.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4']):
                file_path = os.path.join(music_folder, file)
                file_time = os.path.getctime(file_path)
                all_audio_files.append((file, file_path, file_time))
        
        if all_audio_files:
            all_audio_files.sort(key=lambda x: x[2], reverse=True)
            new_file = all_audio_files[0][1]
            
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            for file, file_path, _ in all_audio_files:
                if (safe_title.lower() in file.lower() or 
                    title.lower() in file.lower() or
                    any(word.lower() in file.lower() for word in title.split() if len(word) > 3)):
                    new_file = file_path
                    break
            
        if new_file and os.path.exists(new_file):
            if new_file.lower().endswith(('.m4a', '.mp4')):
                mp3_file = new_file.rsplit('.', 1)[0] + '.mp3'
                try:
                    os.rename(new_file, mp3_file)
                    new_file = mp3_file
                    root.after(0, lambda: update_progress(100, "Converted to MP3 ", progress_bar, status_label, root))
                except Exception:
                    root.after(0, lambda: update_progress(100, "Download complete ", progress_bar, status_label, root))
            
            # Update history with music title
            history = load_history()
            history["urls"].append(url_hash)
            
            if "real_urls" not in history:
                history["real_urls"] = []
            history["real_urls"].append(url)
            
            # Müzik ismini de kaydet
            if "music_titles" not in history:
                history["music_titles"] = []
            
            # Dosya isminden müzik ismini çıkar (uzantıyı kaldır)
            music_title = os.path.splitext(os.path.basename(new_file))[0]
            
            # Çok uzun isimleri kısalt
            if len(music_title) > 60:
                music_title = music_title[:57] + "..."
            
            history["music_titles"].append(music_title)
            debug_print(f"🎵 Music title saved: {music_title}", "SUCCESS")
            
            save_history(history)
            
            from gui_module import finish_download_success
            root.after(0, lambda: finish_download_success(new_file, url_entry, download_button, stop_button, progress_bar, status_label, root))
        else:
            error_msg = f"Downloaded file not found!\n\nSearched title: {title}"
            from gui_module import finish_download_error
            root.after(0, lambda: finish_download_error(error_msg, download_button, stop_button, progress_bar, status_label))

    except Exception as e:
        error_msg = f"An error occurred:\n{str(e)}"
        from gui_module import finish_download_error
        root.after(0, lambda: finish_download_error(error_msg, download_button, stop_button, progress_bar, status_label))

def convert_existing_files(status_label, download_button, stop_button):
    """Eski dosyaları 128kbps MP3'e dönüştürür - Detaylı Debug"""
    print("\n Convert Existing Files başlatılıyor...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    music_folder = os.path.join(script_dir, "Music")
    
    print(f" Klasör kontrol ediliyor: {music_folder}")
    
    # Klasör kontrolü
    if not os.path.exists(music_folder):
        print(f" Music klasörü bulunamadı!")
        messagebox.showwarning("Uyarı", f"Music klasörü bulunamadı!\nAranan yol: {music_folder}")
        return
    
    # Mevcut müzik dosyalarını bul
    audio_files = []
    supported_extensions = ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4', '.aac', '.ogg']
    
    try:
        all_files = os.listdir(music_folder)
        print(f" Klasörde {len(all_files)} dosya bulundu")
        
        for file in all_files:
            if any(ext in file.lower() for ext in supported_extensions):
                audio_files.append(file)
                print(f" Ses dosyası bulundu: {file}")
                
    except Exception as e:
        print(f" Klasör okuma hatası: {e}")
        messagebox.showerror("Hata", f"Klasör okunamıyor: {str(e)}")
        return
    
    print(f" Toplam {len(audio_files)} ses dosyası tespit edildi")
    
    if not audio_files:
        print(" Hiç ses dosyası bulunamadı")
        messagebox.showinfo("Bilgi", "Music klasöründe ses dosyası bulunamadı!")
        return
    
    # Kullanıcıdan onay al
    print(" Kullanıcıdan onay bekleniyor...")
    result = messagebox.askyesno(" Araba Uyumlu Dönüştürme", 
                                f"{len(audio_files)} dosya bulundu:\n\n"
                                f"{chr(10).join(audio_files[:5])}\n"
                                f"{'...' if len(audio_files) > 5 else ''}\n\n"
                                f"Bunları 128kbps MP3 olarak aynı klasöre dönüştür?\n\n"
                                f" Not: Orijinal dosyalar silinecek ve\n"
                                f"128kbps MP3 formatına dönüştürülecek!")
    if not result:
        print(" Kullanıcı işlemi iptal etti")
        return
    
    print(" Kullanıcı onayladı, dönüştürme başlıyor...")
    
    def convert_process():
        try:
            global stop_requested, current_thread
            stop_requested = False
            
            print(" UI kilitleniyor...")
            # UI'yi kilitle
            download_button.config(state='disabled')
            stop_button.config(state='normal')
            
            success_count = 0
            failed_count = 0
            
            # FFmpeg kontrol et
            ffmpeg_path = r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe'
            if not os.path.exists(ffmpeg_path):
                print(f" FFmpeg bulunamadı: {ffmpeg_path}")
                messagebox.showerror("Hata", f"FFmpeg bulunamadı!\nBeklenen konum: {ffmpeg_path}")
                return
            
            print(f" FFmpeg bulundu: {ffmpeg_path}")
            
            for i, file in enumerate(audio_files):
                if stop_requested:
                    print(" Kullanıcı tarafından durduruldu")
                    break
                
                print(f"\n--- Dosya {i+1}/{len(audio_files)}: {file} ---")
                
                try:
                    status_label.config(text=f" Converting: {file} ({i+1}/{len(audio_files)})")
                    
                    input_path = os.path.join(music_folder, file)
                    file_name, file_ext = os.path.splitext(file)
                    
                    print(f" Giriş dosyası: {input_path}")
                    print(f" Dosya adı: {file_name}, Uzantı: {file_ext}")
                    
                    # Eğer zaten MP3 ise ve boyutu küçükse skip et
                    if file_ext.lower() == '.mp3':
                        file_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
                        print(f" MP3 dosya boyutu: {file_size:.2f} MB")
                        
                        if file_size < 5:  # 5MB'dan küçükse muhtemelen zaten 128kbps
                            print(" Zaten küçük MP3, atlanıyor...")
                            success_count += 1
                            continue
                    
                    # Temp dosya oluştur
                    temp_output = os.path.join(music_folder, f"{file_name}_TEMP_128k.mp3")
                    print(f" Temp dosya: {temp_output}")
                    
                    # FFmpeg komutu
                    ffmpeg_cmd = [
                        ffmpeg_path,
                        '-i', input_path,
                        '-c:a', 'libmp3lame',
                        '-b:a', '128k',
                        '-ar', '44100',
                        '-ac', '2',
                        '-id3v2_version', '3',
                        '-write_id3v1', '1',
                        '-y', temp_output
                    ]
                    
                    print(f" FFmpeg komutu çalıştırılıyor...")
                    print(f"   Command: {' '.join(ffmpeg_cmd[:3])} ... {ffmpeg_cmd[-1]}")
                    
                    start_time = time.time()
                    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                          timeout=300)  # 5 dakika timeout
                    end_time = time.time()
                    
                    print(f" Dönüştürme süresi: {end_time - start_time:.2f} saniye")
                    print(f" Return code: {result.returncode}")
                    
                    if result.returncode == 0 and os.path.exists(temp_output):
                        # Dosya boyutlarını karşılaştır
                        original_size = os.path.getsize(input_path) / (1024 * 1024)
                        new_size = os.path.getsize(temp_output) / (1024 * 1024)
                        print(f" Orijinal: {original_size:.2f} MB  Yeni: {new_size:.2f} MB")
                        
                        # Orijinal dosyayı sil ve yenisiyle değiştir
                        final_output = os.path.join(music_folder, f"{file_name}.mp3")
                        print(f" Orijinal dosya siliniyor: {input_path}")
                        os.remove(input_path)
                        
                        print(f" Yeni dosya adlandırılıyor: {temp_output}  {final_output}")
                        os.rename(temp_output, final_output)
                        
                        success_count += 1
                        print(f" Başarılı: {file}  128kbps MP3 ({new_size:.2f} MB)")
                    else:
                        # Temp dosyayı temizle
                        if os.path.exists(temp_output):
                            print(f" Temp dosya temizleniyor: {temp_output}")
                            os.remove(temp_output)
                        
                        failed_count += 1
                        print(f" Başarısız: {file}")
                        if result.stderr:
                            print(f"   Hata: {result.stderr[:200]}...")
                
                except subprocess.TimeoutExpired:
                    print(f" Timeout: {file} - 5 dakikada tamamlanamadı")
                    failed_count += 1
                except Exception as e:
                    print(f" Beklenmedik hata {file}: {e}")
                    failed_count += 1
                    continue
            
            print(f"\n Dönüştürme tamamlandı!")
            print(f" Başarılı: {success_count}")
            print(f" Başarısız: {failed_count}")
            
            # UI'yi serbest bırak
            download_button.config(state='normal')
            stop_button.config(state='disabled')
            
            # Sonuç mesajı
            if success_count > 0:
                status_label.config(text=" Conversion completed!")
                messagebox.showinfo(" Başarılı", 
                                  f" {success_count} dosya 128kbps MP3'e dönüştürüldü!\n"
                                  f" {failed_count} dosya başarısız\n\n"
                                  f" Dosyalar artık araba uyumlu formatında.\n"
                                  f" Konum: Music klasörü")
            else:
                status_label.config(text=" Conversion failed!")
                messagebox.showwarning("Uyarı", f"Hiçbir dosya dönüştürülemedi!\n\n"
                                               f" Başarısız: {failed_count} dosya")
                
        except Exception as e:
            print(f" Genel hata: {e}")
            download_button.config(state='normal')
            stop_button.config(state='disabled')
            status_label.config(text=" Error occurred!")
            messagebox.showerror("Hata", f"Dönüştürme sırasında hata: {str(e)}")
        finally:
            print(" UI sıfırlanıyor...")
            status_label.config(text="Ready ")
    
    # Dönüştürmeyi thread'de çalıştır
    print(" Thread başlatılıyor...")
    global current_thread
    current_thread = threading.Thread(target=convert_process, daemon=True)
    current_thread.start()

def stop_download():
    """Stops the current download operation"""
    global stop_requested, current_thread
    stop_requested = True
    if current_thread and current_thread.is_alive():
        current_thread.join(timeout=3.0)
