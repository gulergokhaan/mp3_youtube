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

# İndirme geçmişi için dosya
HISTORY_FILE = "indirme_gecmisi.json"

def load_history():
    """İndirme geçmişini yükle ve klasördeki dosyalarla senkronize et"""
    history = {"urls": [], "files": []}
    
    # Script dizinini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, HISTORY_FILE)
    
    # Önce kayıtlı geçmişi yükle
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    # Müzikler klasöründeki dosyaları tara
    music_folder = os.path.join(script_dir, "Müzikler")
    if os.path.exists(music_folder):
        existing_files = set(history.get("files", []))
        
        for file in os.listdir(music_folder):
            if any(ext in file.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4']):
                if file not in existing_files:
                    # Yeni dosya bulundu, geçmişe ekle
                    history["files"].append(file)
        
        # Geçmişte olup da klasörde olmayan dosyaları kaldır
        history["files"] = [f for f in history["files"] if os.path.exists(os.path.join(music_folder, f))]
    
    return history

def save_history(history):
    """İndirme geçmişini kaydet ve klasörle senkronize et"""
    # Script dizinini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, HISTORY_FILE)
    
    # Önce klasör taraması yap
    music_folder = os.path.join(script_dir, "Müzikler")
    if os.path.exists(music_folder):
        # Geçmişte olup da klasörde olmayan dosyaları kaldır
        history["files"] = [f for f in history["files"] if os.path.exists(os.path.join(music_folder, f))]
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

def update_history_display():
    """Geçmiş görüntüsünü güncelle"""
    history = load_history()
    music_count = len(history["files"])
    
    # Alt kısımdaki sayaç labelını güncelle
    count_label.config(text=f"Toplam İndirilen Müzik: {music_count}")
    
    # Müzik listesini güncelle (gizli)
    history_text.delete(1.0, tk.END)
    if history["files"]:
        for i, file_name in enumerate(reversed(history["files"][-20:]), 1):  # Son 20 müzik
            history_text.insert(tk.END, f"{i}. {file_name}\n")

def toggle_history():
    """Müzik listesini göster/gizle"""
    if history_frame.winfo_viewable():
        history_frame.pack_forget()
        toggle_button.config(text="📂 Müzik Listesi")
    else:
        history_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        toggle_button.config(text="📂 Listeyi Gizle")

def download_and_convert():
    """
    Kullanıcının girdiği YouTube URL'sini indirir ve MP3'e dönüştürür.
    Threading ile arka planda çalışır.
    """
    url = url_entry.get()
    if not url:
        messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin.")
        return
    
    # URL'nin daha önce indirilip indirilmediğini kontrol et
    history = load_history()
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    if url_hash in history["urls"]:
        result = messagebox.askyesno("Uyarı", "Bu video daha önce indirilmiş!\n\nYine de indirmek istiyor musunuz?")
        if not result:
            return
    
    # İndirme butonunu devre dışı bırak
    download_button.config(state='disabled', text="⏳ İndiriliyor")
    status_label.config(text="Başlatılıyor...")
    
    # Arka planda çalıştır
    thread = threading.Thread(target=download_worker, args=(url, url_hash))
    thread.daemon = True
    thread.start()

def download_worker(url, url_hash):
    """Arka planda indirme işlemini yapar"""
    def progress_hook(d):
        """yt-dlp progress hook"""
        try:
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    root.after(0, lambda p=percent: update_progress(p, f"İndiriliyor... {p:.1f}%"))
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].replace('%', '')
                    try:
                        percent = float(percent_str)
                        root.after(0, lambda p=percent: update_progress(p, f"İndiriliyor... {p:.1f}%"))
                    except:
                        root.after(0, lambda: update_progress(50, "İndiriliyor..."))
                else:
                    root.after(0, lambda: update_progress(50, "İndiriliyor..."))
            elif d['status'] == 'finished':
                root.after(0, lambda: update_progress(100, "İşleniyor..."))
            elif d['status'] == 'error':
                root.after(0, lambda: update_progress(0, "Hata oluştu..."))
        except Exception:
            # Progress hook hatalarını sessizce geç
            pass
    
    try:
        # UI güncelleme - thread-safe
        root.after(0, lambda: status_label.config(text="Video bilgileri alınıyor..."))
        root.after(0, lambda: progress_bar.pack(pady=10, before=status_label))
        root.after(0, lambda: update_progress(0, "Hazırlanıyor..."))

        # Müzikler klasörü oluştur - program neredeyse orada
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_folder = os.path.join(script_dir, "Müzikler")
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)

        # yt-dlp ile en yüksek kalitede ses indirme (MP3 öncelikli - araba teypi uyumluluğu)
        ydl_opts = {
            'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f'{music_folder}/%(title)s.%(ext)s',
            'noplaylist': True,
            'concurrent_fragment_downloads': 4,
            'progress_hooks': [progress_hook],
            'retries': 3,
            'fragment_retries': 3,
            'ignoreerrors': False,
            # FFmpeg olmadan çalışsın
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            
            # UI güncelleme
            root.after(0, lambda: status_label.config(text=f"'{title}' indiriliyor..."))
            
            # Direkt ses dosyası olarak indir
            ydl.download([url])
            
            # İndirilen dosyayı bul - daha güçlü algoritma
            new_file = None
            
            # Önce klasördeki tüm ses dosyalarını listele (mp4 de dahil)
            all_audio_files = []
            for file in os.listdir(music_folder):
                if any(ext in file.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4']):
                    file_path = os.path.join(music_folder, file)
                    file_time = os.path.getctime(file_path)
                    all_audio_files.append((file, file_path, file_time))
            
            if all_audio_files:
                # En son oluşturulan dosyayı al
                all_audio_files.sort(key=lambda x: x[2], reverse=True)
                new_file = all_audio_files[0][1]
                
                # Eğer title ile eşleşen dosya varsa onu tercih et
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                for file, file_path, _ in all_audio_files:
                    if (safe_title.lower() in file.lower() or 
                        title.lower() in file.lower() or
                        any(word.lower() in file.lower() for word in title.split() if len(word) > 3)):
                        new_file = file_path
                        break
            
            if new_file and os.path.exists(new_file):
                # Eğer dosya .m4a veya .mp4 ise, .mp3 uzantısına çevir (araba teypi uyumluluğu için)
                if new_file.lower().endswith(('.m4a', '.mp4')):
                    mp3_file = new_file.rsplit('.', 1)[0] + '.mp3'
                    try:
                        os.rename(new_file, mp3_file)
                        new_file = mp3_file
                        root.after(0, lambda: update_progress(100, "MP3'e dönüştürüldü ✅"))
                    except Exception as rename_error:
                        # Rename başarısız olursa orijinal dosyayı kullan
                        root.after(0, lambda: update_progress(100, "İndirme tamamlandı ✅"))
                
                # Geçmişi güncelle
                history = load_history()
                history["urls"].append(url_hash)
                history["files"].append(os.path.basename(new_file))
                save_history(history)
                
                # UI güncellemelerini ana thread'de yap
                root.after(0, lambda: finish_download_success(new_file))
            else:
                # Debug: Klasördeki dosyaları listele
                debug_files = []
                if os.path.exists(music_folder):
                    debug_files = [f for f in os.listdir(music_folder) 
                                 if any(ext in f.lower() for ext in ['.m4a', '.mp3', '.webm', '.opus', '.wav', '.mp4'])]
                
                error_msg = f"İndirilen dosya bulunamadı!\n\nAranan başlık: {title}\nKlasördeki dosyalar: {len(debug_files)}\n"
                if debug_files:
                    error_msg += f"Son dosya: {debug_files[-1] if debug_files else 'Yok'}"
                
                root.after(0, lambda: finish_download_error(error_msg))

    except Exception as e:
        error_msg = f"Bir hata oluştu:\n{str(e)}"
        root.after(0, lambda: finish_download_error(error_msg))

def update_progress(percent, text):
    """Progress bar'ı güncelle"""
    try:
        progress_bar['value'] = percent
        status_label.config(text=text)
        root.update_idletasks()
    except:
        pass

def show_success_popup(file_name, file_path):
    """Özel başarı pop-up penceresi"""
    popup = tk.Toplevel(root)
    popup.title("✅ Başarılı!")
    popup.geometry("550x350")
    popup.configure(bg='#000000')
    popup.resizable(False, False)
    
    # Pencereyi ortalama
    popup.transient(root)
    popup.grab_set()
    
    # Ana pencereye göre ortala
    popup.geometry("+{}+{}".format(
        root.winfo_rootx() + 25,
        root.winfo_rooty() + 25
    ))
    
    # Başlık
    title_label = tk.Label(popup, text="🎵 İndirme Tamamlandı!", 
                          font=("Segoe UI", 16, "bold"), 
                          fg="#00FF00", bg='#000000')
    title_label.pack(pady=15)
    
    # Dosya adı
    name_label = tk.Label(popup, text=f"Dosya Adı:", 
                         font=("Segoe UI", 11, "bold"), 
                         fg="#FFFFFF", bg='#000000')
    name_label.pack(pady=(10, 5))
    
    file_name_label = tk.Label(popup, text=file_name, 
                              font=("Consolas", 10), 
                              fg="#CCCCCC", bg='#000000', 
                              wraplength=500)
    file_name_label.pack(pady=(0, 10))
    
    # Kayıt yeri
    location_label = tk.Label(popup, text=f"Kayıt Yeri:", 
                             font=("Segoe UI", 11, "bold"), 
                             fg="#FFFFFF", bg='#000000')
    location_label.pack(pady=(10, 5))
    
    path_label = tk.Label(popup, text=file_path, 
                         font=("Consolas", 9, "italic", "bold"), 
                         fg="#4080FF", bg='#000000', 
                         wraplength=500)
    path_label.pack(pady=(0, 20))
    
    # Butonlar frame
    button_frame = tk.Frame(popup, bg='#000000')
    button_frame.pack(pady=15, side=tk.BOTTOM)
    
    # Klasörü aç butonu
    def open_folder():
        import subprocess
        subprocess.Popen(f'explorer /select,"{os.path.abspath(os.path.join(file_path, file_name))}"')
        popup.destroy()
    
    open_button = tk.Button(button_frame, text="📁 Klasörü Aç", 
                           command=open_folder,
                           bg="#000080", fg="white", 
                           font=("Segoe UI", 10, "bold"),
                           relief=tk.FLAT, bd=0, width=14, height=2,
                           activebackground="#0000A0", activeforeground="white",
                           cursor="hand2")
    open_button.pack(side=tk.LEFT, padx=15)
    
    # Tamam butonu
    ok_button = tk.Button(button_frame, text="✅ Tamam", 
                         command=popup.destroy,
                         bg="#000080", fg="white", 
                         font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, bd=0, width=14, height=2,
                         activebackground="#0000A0", activeforeground="white",
                         cursor="hand2")
    ok_button.pack(side=tk.LEFT, padx=15)
    
    # ESC ile kapatma
    popup.bind('<Escape>', lambda e: popup.destroy())
    popup.focus_set()

def finish_download_success(new_file):
    """İndirme başarılı olduğunda UI'yi güncelle"""
    update_history_display()
    full_path = os.path.abspath(new_file)
    status_label.config(text=f"✅ Başarılı! {os.path.basename(new_file)}")
    
    # Progress bar'ı gizle ve butonu tekrar etkinleştir
    progress_bar.pack_forget()
    download_button.config(state='normal', text="🎵 Dönüştür ve İndir")
    
    # Özel pop-up göster
    show_success_popup(os.path.basename(new_file), os.path.dirname(full_path))
    url_entry.delete(0, tk.END)

def finish_download_error(error_msg):
    """İndirme hatası olduğunda UI'yi güncelle"""
    status_label.config(text="❌ Hata oluştu.")
    progress_bar.pack_forget()
    download_button.config(state='normal', text="🎵 Dönüştür ve İndir")
    messagebox.showerror("Hata", error_msg)

# --- Arayüz Kısmı (Tkinter) ---
root = tk.Tk()
root.title("YouTube MP3 Converter")
root.geometry("700x500")
root.resizable(True, True)
root.configure(bg='#000000')  # Düz siyah arka plan

# Progress bar stilini ayarla
style = ttk.Style()
style.theme_use('clam')
style.configure('Custom.Horizontal.TProgressbar',
                background='#000080',
                troughcolor='#333333',
                borderwidth=0,
                lightcolor='#000080',
                darkcolor='#000080')

# URL girişi bölümü - direkt root üzerine
url_label = tk.Label(root, text="🎵 YouTube Video URL'si:", 
                    font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg='#000000')
url_label.pack(pady=(50, 10))

url_entry = tk.Entry(root, width=65, font=("Consolas", 11), bg='#F0F0F0', fg='#000000',
                    relief=tk.FLAT, bd=2, highlightbackground='#CCCCCC', highlightthickness=1,
                    insertbackground='#000000', selectbackground='#4080FF', selectforeground='#FFFFFF')
url_entry.pack(pady=10, ipady=8)

# Butonlar bölümü - yan yana ve eşit boyutlu
button_frame = tk.Frame(root, bg='#000000')
button_frame.pack(pady=15)

# Ana indirme butonu - kompakt
download_button = tk.Button(button_frame, text="🎵 Dönüştür ve İndir", command=download_and_convert, 
                           bg="#000080", fg="white", font=("Segoe UI", 10, "bold"), 
                           relief=tk.FLAT, bd=0, width=16, height=2,
                           activebackground="#0000A0", activeforeground="white",
                           cursor="hand2")
download_button.pack(side=tk.LEFT, padx=5)

# Müzik listesi toggle butonu - kompakt
toggle_button = tk.Button(button_frame, text="📂 Müzik Listesi", command=toggle_history,
                         bg="#000080", fg="white", font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, bd=0, width=16, height=2,
                         activebackground="#0000A0", activeforeground="white",
                         cursor="hand2")
toggle_button.pack(side=tk.LEFT, padx=5)

def refresh_history():
    """Klasörü tarayarak geçmişi yenile"""
    history = load_history()
    save_history(history)
    update_history_display()
    status_label.config(text="📂 Klasör tarandı!")
    root.after(2000, lambda: status_label.config(text="Hazır ✨"))

refresh_button = tk.Button(button_frame, text="🔄 Yenile", command=refresh_history,
                          bg="#000080", fg="white", font=("Segoe UI", 10, "bold"),
                          relief=tk.FLAT, bd=0, width=12, height=2,
                          activebackground="#0000A0", activeforeground="white",
                          cursor="hand2")
refresh_button.pack(side=tk.LEFT, padx=5)

# Progress bar - başlangıçta gizli
progress_bar = ttk.Progressbar(root, length=450, mode='determinate', 
                              style='Custom.Horizontal.TProgressbar')

# Durum yazısı
status_label = tk.Label(root, text="Hazır ✨", font=("Segoe UI", 11), fg="#FFFFFF", bg='#000000')
status_label.pack(pady=10)

# Müzik listesi frame
history_frame = tk.Frame(root, bg='#000000')

history_text = scrolledtext.ScrolledText(history_frame, width=70, height=8, font=("Consolas", 9),
                                       bg="#000000", fg="#FFFFFF", relief=tk.FLAT, bd=1,
                                       selectbackground="#000080", selectforeground="white")
history_text.pack(pady=12, padx=15)

# Alt kısım - her zaman en altta kalsın
bottom_frame = tk.Frame(root, bg='#000000')
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15, padx=15)

# Sol alt köşe - Created by GG
created_label = tk.Label(bottom_frame, text="✨ Created by GG", 
                        font=("Segoe UI", 9, "italic"), fg="#888888", bg='#000000')
created_label.pack(side=tk.LEFT)

# Sağ alt köşe - Sayaç
count_label = tk.Label(bottom_frame, text="🎵 Toplam İndirilen: 0", 
                      font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg='#000000')
count_label.pack(side=tk.RIGHT)

# Başlangıçta geçmişi yükle
update_history_display()

root.mainloop()