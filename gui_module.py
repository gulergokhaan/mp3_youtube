# -*- coding: utf-8 -*-
"""
YouTube MP3 İndirici - Modern GUI Modülü v2.0 - Enhanced UI
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from download_module import download_and_convert, convert_existing_files, stop_download
from history_utils import load_history, save_history

# Debug fonksiyonu için basit tanım
def debug_print(message, level="INFO"):
    """Basit debug print fonksiyonu"""
    print(f"[{level}] {message}")

# Gelişmiş Modern Temalar
THEMES = {
    "dark": {
        "bg": "#1a1a1a",
        "fg": "#ffffff",
        "button_bg": "#404040",
        "button_fg": "#ffffff",
        "entry_bg": "#2d2d2d",
        "entry_fg": "#ffffff",
        "accent": "#0078d4",
        "success": "#27ae60",
        "error": "#e74c3c",
        "secondary": "#34495e",
        "hover": "#555555",
        "gradient_start": "#2c3e50",
        "gradient_end": "#34495e"
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#2c3e50",
        "button_bg": "#ecf0f1",
        "button_fg": "#2c3e50",
        "entry_bg": "#ffffff",
        "entry_fg": "#2c3e50",
        "accent": "#3498db",
        "success": "#27ae60",
        "error": "#e74c3c",
        "secondary": "#bdc3c7",
        "hover": "#d5dbdb",
        "gradient_start": "#f8f9fa",
        "gradient_end": "#e9ecef"
    },
    "ocean": {
        "bg": "#0f3460",
        "fg": "#ffffff",
        "button_bg": "#16537e",
        "button_fg": "#ffffff",
        "entry_bg": "#1e3a8a",
        "entry_fg": "#ffffff",
        "accent": "#00bcd4",
        "success": "#4caf50",
        "error": "#f44336",
        "secondary": "#37474f",
        "hover": "#1976d2",
        "gradient_start": "#0f3460",
        "gradient_end": "#16537e"
    },
    "purple": {
        "bg": "#2d1b69",
        "fg": "#ffffff",
        "button_bg": "#5b2c87",
        "button_fg": "#ffffff",
        "entry_bg": "#44337a",
        "entry_fg": "#ffffff",
        "accent": "#9c27b0",
        "success": "#4caf50",
        "error": "#f44336",
        "secondary": "#6a4c93",
        "hover": "#7b1fa2",
        "gradient_start": "#2d1b69",
        "gradient_end": "#5b2c87"
    }
}

class ModernGUI:
    def __init__(self):
        """Modern GUI başlat"""
        self.root = tk.Tk()
        self.root.title("🎵 YouTube MP3 Converter Pro v2.0")
        self.root.geometry("750x850")
        self.root.minsize(650, 750)
        self.root.configure(bg="#1a1a1a")
        
        # Pencere ikonunu ayarla (varsa)
        self.setup_window_icon()
        
        # Modern font tanımları
        self.fonts = {
            "title": ("Segoe UI", 18, "bold"),
            "subtitle": ("Segoe UI", 12, "italic"),
            "button": ("Segoe UI", 11, "bold"),
            "button_small": ("Segoe UI", 9, "bold"),
            "text": ("Segoe UI", 10, "normal"),
            "text_italic": ("Segoe UI", 10, "italic"),
            "small": ("Segoe UI", 8, "normal"),
            "history": ("Segoe UI", 9, "italic")
        }
        
        # Tema ayarları
        self.current_theme = "dark"
        self.theme_names = list(THEMES.keys())
        
        # Widget referansları
        self.widgets = {}
        
        # Ana layout oluştur
        self.create_layout()
        self.apply_theme()
        self.load_history_display()
        
        # Pencereyi ortala
        self.center_window()

    def setup_window_icon(self):
        """Pencere ikonunu ayarla"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Mevcut icon dosyalarını kontrol et
            icon_files = [
                "converted_icon.ico",
                "icon.ico", 
                "app_icon.ico",
                "music_icon.ico"
            ]
            
            icon_path = None
            for icon_file in icon_files:
                test_path = os.path.join(script_dir, icon_file)
                if os.path.exists(test_path):
                    icon_path = test_path
                    debug_print(f"🎨 Icon found: {icon_file}", "SUCCESS")
                    break
            
            if icon_path:
                self.root.iconbitmap(icon_path)
                debug_print(f"✅ Icon loaded successfully!", "SUCCESS")
            else:
                debug_print("⚠️ No icon file found, using default", "WARNING")
                
        except Exception as e:
            debug_print(f"❌ Icon loading failed: {e}", "ERROR")

    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_layout(self):
        """Ana layout'u oluştur"""
        # Ana çerçeve
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header()
        
        # Tema seçici
        self.create_theme_selector()
        
        # URL giriş bölümü
        self.create_url_section()
        
        # Format seçimi
        self.create_format_section()
        
        # Butonlar
        self.create_buttons()
        
        # Progress bölümü
        self.create_progress_section()
        
        # Tarihçe bölümü
        self.create_history_section()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Header bölümü"""
        header_frame = tk.Frame(self.main_frame, height=100)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        header_frame.pack_propagate(False)
        
        # Ana başlık
        title_label = tk.Label(header_frame, 
                             text="🎵 YouTube MP3 Converter *Pro*",
                             font=self.fonts["title"])
        title_label.pack(pady=(15, 5))
        
        # Alt başlık
        subtitle_label = tk.Label(header_frame, 
                                text="✨ *High-Quality Audio Downloads & Conversion* ✨",
                                font=self.fonts["subtitle"])
        subtitle_label.pack()
        
        # Dekoratif çizgi
        separator = tk.Frame(header_frame, height=3, relief=tk.RIDGE, bd=1)
        separator.pack(fill=tk.X, pady=(15, 0))
        
        self.widgets['header_frame'] = header_frame
        self.widgets['title_label'] = title_label
        self.widgets['subtitle_label'] = subtitle_label
        self.widgets['separator'] = separator

    def create_theme_selector(self):
        """Tema seçici bölümü"""
        theme_frame = tk.Frame(self.main_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        theme_label = tk.Label(theme_frame, 
                             text="🎨 Theme:",
                             font=self.fonts["text"])
        theme_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.current_theme.title())
        
        theme_menu = ttk.Combobox(theme_frame, 
                                textvariable=self.theme_var,
                                values=[name.title() for name in self.theme_names],
                                state="readonly", 
                                width=12,
                                font=self.fonts["text"])
        theme_menu.pack(side=tk.LEFT)
        theme_menu.bind('<<ComboboxSelected>>', 
                       lambda e: self.change_theme(self.theme_var.get().lower()))
        
        self.widgets['theme_frame'] = theme_frame
        self.widgets['theme_label'] = theme_label
        self.widgets['theme_menu'] = theme_menu

    def create_url_section(self):
        """URL giriş bölümü"""
        url_frame = tk.LabelFrame(self.main_frame, 
                                text="📹 Video URL",
                                font=self.fonts["subtitle"],
                                padx=15, pady=15)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        # URL giriş alanı
        url_input_frame = tk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X)
        
        self.url_entry = tk.Entry(url_input_frame, 
                                font=self.fonts["text"],
                                relief=tk.FLAT,
                                bd=1)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        # Yapıştır butonu
        paste_button = tk.Button(url_input_frame, 
                               text="📋",
                               font=self.fonts["button"],
                               width=3,
                               command=self.paste_url,
                               relief=tk.FLAT,
                               bd=1)
        paste_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Placeholder text
        self.url_entry.insert(0, "Enter YouTube URL here...")
        self.url_entry.bind('<FocusIn>', self.clear_placeholder)
        self.url_entry.bind('<FocusOut>', self.restore_placeholder)
        
        self.widgets['url_frame'] = url_frame
        self.widgets['url_entry'] = self.url_entry
        self.widgets['paste_button'] = paste_button

    def paste_url(self):
        """Panodan URL yapıştır"""
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text and ('youtube.com' in clipboard_text or 'youtu.be' in clipboard_text):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
            else:
                messagebox.showwarning("⚠️ Warning", "No valid YouTube URL found in clipboard!")
        except:
            messagebox.showerror("❌ Error", "Could not access clipboard!")

    def clear_placeholder(self, event):
        """Placeholder text'i temizle"""
        if self.url_entry.get() == "Enter YouTube URL here...":
            self.url_entry.delete(0, tk.END)

    def restore_placeholder(self, event):
        """Placeholder text'i geri yükle"""
        if not self.url_entry.get():
            self.url_entry.insert(0, "Enter YouTube URL here...")

    def create_format_section(self):
        """Format seçimi bölümü"""
        format_frame = tk.LabelFrame(self.main_frame, 
                                   text="🎼 Audio Format & Quality",
                                   font=self.fonts["subtitle"],
                                   padx=15, pady=15)
        format_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Format seçenekleri
        self.format_var = tk.StringVar(value="MP3 (128k) - Car Compatible")
        
        formats = [
            ("🚗 MP3 (128k) - Car Compatible", "MP3 (128k) - Car Compatible"),
            ("🎵 MP3 (192k) - Good Quality", "MP3 (192k) - Good Quality"),
            ("🎼 MP3 (320k) - High Quality", "MP3 (320k) - High Quality"),
            ("🔊 WAV - Lossless", "WAV - Lossless"),
            ("📱 M4A - Mobile", "M4A - Mobile")
        ]
        
        # Grid layout için
        for i, (text, value) in enumerate(formats):
            row = i // 2
            col = i % 2
            
            radio = tk.Radiobutton(format_frame, 
                                 text=text,
                                 variable=self.format_var,
                                 value=value,
                                 font=self.fonts["text"],
                                 anchor="w")
            radio.grid(row=row, column=col, sticky="w", padx=(10, 20), pady=5)
        
        self.widgets['format_frame'] = format_frame
        self.widgets['format_var'] = self.format_var

    def create_buttons(self):
        """Buton bölümü - Modern tasarım"""
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Ana butonlar
        main_buttons_frame = tk.Frame(button_frame)
        main_buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Download butonu - Büyük ve çekici
        self.download_button = tk.Button(main_buttons_frame, 
                                       text="🚀 *Download & Convert*",
                                       font=self.fonts["button"],
                                       command=self.download_audio,
                                       relief=tk.RAISED,
                                       bd=3,
                                       height=3,
                                       cursor="hand2",
                                       padx=20,
                                       pady=10)
        self.download_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Stop butonu - Kırmızı tonlarda
        self.stop_button = tk.Button(main_buttons_frame, 
                                   text="⛔ *Stop*",
                                   font=self.fonts["button"],
                                   command=self.stop_download,
                                   state='disabled',
                                   relief=tk.RAISED,
                                   bd=3,
                                   height=3,
                                   cursor="hand2",
                                   padx=20,
                                   pady=10)
        self.stop_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Utility butonlar - Küçük ve şık
        util_buttons_frame = tk.Frame(button_frame)
        util_buttons_frame.pack(fill=tk.X)
        
        # Convert existing files butonu
        convert_button = tk.Button(util_buttons_frame, 
                                 text="🔄 *Convert Existing*",
                                 font=self.fonts["button_small"],
                                 command=self.convert_files,
                                 relief=tk.RAISED,
                                 bd=2,
                                 height=2,
                                 cursor="hand2",
                                 padx=15,
                                 pady=5)
        convert_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Open Music folder butonu
        folder_button = tk.Button(util_buttons_frame, 
                                text="📁 *Music Folder*",
                                font=self.fonts["button_small"],
                                command=self.open_music_folder,
                                relief=tk.RAISED,
                                bd=2,
                                height=2,
                                cursor="hand2",
                                padx=15,
                                pady=5)
        folder_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.widgets['button_frame'] = button_frame
        self.widgets['download_button'] = self.download_button
        self.widgets['stop_button'] = self.stop_button
        self.widgets['convert_button'] = convert_button
        self.widgets['folder_button'] = folder_button

    def create_progress_section(self):
        """Progress bölümü - Gelişmiş progress tracking"""
        progress_frame = tk.LabelFrame(self.main_frame,
                                     text="📊 *Download Progress & Status*",
                                     font=self.fonts["subtitle"],
                                     padx=15, pady=15)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Üst durum bilgisi
        status_info_frame = tk.Frame(progress_frame)
        status_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ana durum label
        self.status_label = tk.Label(status_info_frame, 
                                   text="🟢 Ready to download",
                                   font=self.fonts["text"])
        self.status_label.pack(side=tk.LEFT)
        
        # Hız ve zaman bilgisi
        self.speed_label = tk.Label(status_info_frame, 
                                  text="",
                                  font=self.fonts["small"])
        self.speed_label.pack(side=tk.RIGHT)
        
        # Progress bar frame
        progress_bar_frame = tk.Frame(progress_frame)
        progress_bar_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Progress bar
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", 
                       troughcolor='#404040',
                       background='#0078d4',
                       lightcolor='#0078d4',
                       darkcolor='#005a9e',
                       borderwidth=1,
                       relief='raised')
        
        self.progress_bar = ttk.Progressbar(progress_bar_frame, 
                                          style="Custom.Horizontal.TProgressbar",
                                          length=500, 
                                          mode='determinate',
                                          maximum=100)
        # Progress bar başlangıçta gizli
        
        # Progress yüzdesi label
        self.progress_label = tk.Label(progress_bar_frame, 
                                     text="0%",
                                     font=self.fonts["text"])
        # Başlangıçta gizli
        
        # Alt detay bilgisi
        self.detail_label = tk.Label(progress_frame, 
                                   text="💡 *Tip: Choose 128k for car compatibility*",
                                   font=self.fonts["small"])
        self.detail_label.pack(pady=(5, 0))
        
        self.widgets['progress_frame'] = progress_frame
        self.widgets['status_label'] = self.status_label
        self.widgets['speed_label'] = self.speed_label
        self.widgets['progress_bar'] = self.progress_bar
        self.widgets['progress_label'] = self.progress_label
        self.widgets['detail_label'] = self.detail_label

    def create_history_section(self):
        """Geçmiş bölümü - Müzik isimleri ile"""
        history_frame = tk.LabelFrame(self.main_frame, 
                                    text="🎼 *Downloaded Music History*",
                                    font=self.fonts["subtitle"],
                                    padx=15, pady=15)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Müzik sayısı gösterici
        self.music_count_label = tk.Label(history_frame, 
                                         text="🎵 Total Music: 0",
                                         font=self.fonts["text_italic"])
        self.music_count_label.pack(pady=(0, 10))
        
        # History controls
        hist_controls = tk.Frame(history_frame)
        hist_controls.pack(fill=tk.X, pady=(0, 10))
        
        # Mevcut müzikleri tara butonu
        scan_button = tk.Button(hist_controls, 
                              text="🔍 *Scan Existing Music*",
                              font=self.fonts["button_small"],
                              command=self.scan_existing_music,
                              relief=tk.RAISED,
                              bd=2,
                              cursor="hand2",
                              padx=8,
                              pady=3)
        scan_button.pack(side=tk.LEFT)
        
        clear_button = tk.Button(hist_controls, 
                               text="🗑️ *Clear History*",
                               font=self.fonts["button_small"],
                               command=self.clear_history,
                               relief=tk.RAISED,
                               bd=2,
                               cursor="hand2",
                               padx=10,
                               pady=3)
        clear_button.pack(side=tk.RIGHT)
        
        # History listbox with scrollbar
        hist_scroll_frame = tk.Frame(history_frame)
        hist_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(hist_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox - İtalik font ile müzik isimleri
        self.history_listbox = tk.Listbox(hist_scroll_frame, 
                                        font=self.fonts["history"],
                                        yscrollcommand=scrollbar.set,
                                        height=10,
                                        relief=tk.SUNKEN,
                                        bd=2)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        self.widgets['history_frame'] = history_frame
        self.widgets['history_listbox'] = self.history_listbox
        self.widgets['clear_button'] = clear_button
        self.widgets['music_count_label'] = self.music_count_label

    def create_footer(self):
        """Footer bölümü - Sayılar sağ alt köşede"""
        footer_frame = tk.Frame(self.main_frame, height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Dekoratif çizgi
        separator = tk.Frame(footer_frame, height=2, relief=tk.SUNKEN, bd=1)
        separator.pack(fill=tk.X, pady=(0, 8))
        
        # Ana bilgi çerçevesi
        info_container = tk.Frame(footer_frame)
        info_container.pack(fill=tk.X)
        
        # Sol taraf - Tip bilgisi
        tip_label = tk.Label(info_container, 
                           text="💡 *Tip: Choose 128k MP3 for best car compatibility*",
                           font=self.fonts["text_italic"])
        tip_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Sağ taraf - Müzik sayıları (sağ alt köşe)
        right_info = tk.Frame(info_container)
        right_info.pack(side=tk.RIGHT, padx=(0, 10))
        
        # History'deki sayı
        self.history_count_label = tk.Label(right_info, 
                                          text="� Downloaded: 0",
                                          font=self.fonts["small"])
        self.history_count_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Toplam müzik sayısı  
        self.total_music_label = tk.Label(right_info, 
                                        text="� Files: 0",
                                        font=self.fonts["small"])
        self.total_music_label.pack(side=tk.RIGHT)
        
        self.widgets['footer_frame'] = footer_frame
        self.widgets['total_music_label'] = self.total_music_label
        self.widgets['history_count_label'] = self.history_count_label
        self.widgets['tip_label'] = tip_label
        
        # İlk yüklemede sayıları güncelle
        self.update_music_counts()

    def change_theme(self, theme_name):
        """Temayı değiştir"""
        self.current_theme = theme_name
        self.apply_theme()
        
    def apply_theme(self):
        """Seçili temayı uygula"""
        theme = THEMES[self.current_theme]
        
        # Ana pencere
        self.root.configure(bg=theme["bg"])
        
        # Tüm widget'ları güncelle
        self.update_widget_colors(self.main_frame, theme)
        
    def update_widget_colors(self, widget, theme):
        """Widget'ların renklerini güncelle - Geliştirilmiş"""
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == "Frame":
                widget.configure(bg=theme["bg"])
            elif widget_class == "Label":
                widget.configure(bg=theme["bg"], fg=theme["fg"])
                # Müzik sayısı label'ı için özel renk
                try:
                    label_text = widget.cget("text")
                    if "Total Music:" in label_text:
                        widget.configure(fg=theme["accent"])
                except:
                    pass
            elif widget_class == "Button":
                # Özel buton renkleri
                button_text = widget.cget("text")
                if "Download" in button_text:
                    # Ana download butonu - Yeşil tonları
                    widget.configure(bg=theme["success"], fg="#ffffff",
                                   activebackground=theme["accent"],
                                   activeforeground="#ffffff")
                elif "Stop" in button_text:
                    # Stop butonu - Kırmızı tonları
                    widget.configure(bg=theme["error"], fg="#ffffff",
                                   activebackground="#c0392b",
                                   activeforeground="#ffffff")
                else:
                    # Diğer butonlar
                    widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                                   activebackground=theme["hover"],
                                   activeforeground=theme["fg"])
            elif widget_class == "Entry":
                widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                               insertbackground=theme["fg"])
            elif widget_class == "Listbox":
                widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                               selectbackground=theme["accent"])
            elif widget_class == "Labelframe":
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif widget_class == "Radiobutton":
                widget.configure(bg=theme["bg"], fg=theme["fg"],
                               activebackground=theme["bg"],
                               selectcolor=theme["accent"])
                
            # Alt widget'ları da güncelle
            for child in widget.winfo_children():
                self.update_widget_colors(child, theme)
                
        except tk.TclError:
            pass  # Bazı widget'lar belirli özellikleri desteklemeyebilir
            
    def download_audio(self):
        """İndirme işlemini başlat"""
        url = self.url_entry.get().strip()
        
        # Placeholder kontrolü
        if url == "Enter YouTube URL here..." or not url:
            messagebox.showwarning("⚠️ Warning", "Please enter a valid YouTube URL!")
            return
            
        # Progress bar'ı göster
        self.show_progress_bar()
        
        # Download modülünü çağır - widgets dictionary ile
        download_and_convert(url, self.format_var, self.url_entry,
                           self.download_button, self.stop_button,
                           self.widgets['status_label'], self.widgets['progress_bar'], 
                           self.root, gui_instance=self)
                           
    def stop_download(self):
        """İndirmeyi durdur"""
        stop_download()
        self.reset_ui()
        
    def reset_ui(self):
        """UI'yi sıfırla"""
        self.download_button.config(state='normal', text="🚀 *Download & Convert*")
        self.stop_button.config(state='disabled')
        self.reset_progress()
        self.update_music_counts()
        
    def convert_files(self):
        """Mevcut dosyaları dönüştür"""
        convert_existing_files(self.status_label, self.download_button, self.stop_button)
        
    def open_music_folder(self):
        """Music klasörünü aç"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_folder = os.path.join(script_dir, "Music")
        
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
            
        if sys.platform.startswith('win'):
            os.startfile(music_folder)
        elif sys.platform.startswith('darwin'):
            os.system(f'open "{music_folder}"')
        else:
            os.system(f'xdg-open "{music_folder}"')
            
    def clear_history(self):
        """Geçmişi temizle"""
        result = messagebox.askyesno("🗑️ Confirm", "Are you sure you want to clear the *music history*?")
        if result:
            history = {"urls": [], "real_urls": [], "music_titles": []}
            save_history(history)
            self.load_history_display()
            messagebox.showinfo("✨ Success", "*History cleared successfully!*")

    def update_music_counts(self):
        """Müzik sayılarını güncelle"""
        try:
            # History'den indirilen müzik sayısı
            history = load_history()
            downloaded_count = len(history.get('music_titles', []))
            
            # Klasördeki müzik dosyalarını say
            music_folder = "Music_Files"
            existing_count = 0
            if os.path.exists(music_folder):
                music_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
                for file in os.listdir(music_folder):
                    if any(file.lower().endswith(ext) for ext in music_extensions):
                        existing_count += 1
            
            # Sağ alttaki bilgileri güncelle
            if 'total_music_label' in self.widgets:
                self.widgets['total_music_label'].config(text=f"📁 Files: {existing_count}")
            
            if 'history_count_label' in self.widgets:
                self.widgets['history_count_label'].config(text=f"📥 Downloaded: {downloaded_count}")
            
            # Logo alanındaki sayıyı güncelle (eğer varsa)
            if hasattr(self, 'music_count_label'):
                self.music_count_label.config(text=f"🎵 {existing_count}")
                
        except Exception as e:
            debug_print(f"❌ Müzik sayısı güncelleme hatası: {e}", "ERROR")

    def show_progress_bar(self):
        """Progress bar'ı göster"""
        try:
            self.widgets['progress_bar'].pack(pady=(5, 5))
            self.widgets['progress_label'].pack(pady=(0, 5))
            self.update_progress(0, "🚀 *Starting download...*")
        except Exception as e:
            debug_print(f"❌ Progress bar gösterme hatası: {e}", "ERROR")

    def hide_progress_bar(self):
        """Progress bar'ı gizle"""
        try:
            self.widgets['progress_bar'].pack_forget()
            self.widgets['progress_label'].pack_forget()
        except Exception as e:
            debug_print(f"❌ Progress bar gizleme hatası: {e}", "ERROR")

    def update_progress(self, percent, status_text="", speed_text="", detail_text=""):
        """Progress bar ve durumu güncelle"""
        try:
            # Progress bar güncelle
            self.widgets['progress_bar']['value'] = percent
            
            # Progress yüzdesi güncelle
            self.widgets['progress_label'].config(text=f"{percent:.1f}%")
            
            # Ana durum güncelle
            if status_text:
                self.widgets['status_label'].config(text=status_text)
            
            # Hız bilgisi güncelle
            if speed_text:
                self.widgets['speed_label'].config(text=speed_text)
            
            # Detay bilgisi güncelle
            if detail_text:
                self.widgets['detail_label'].config(text=detail_text)
            
            # GUI güncelle
            self.root.update_idletasks()
            
        except Exception as e:
            debug_print(f"❌ Progress güncelleme hatası: {e}", "ERROR")

    def reset_progress(self):
        """Progress'i sıfırla"""
        try:
            self.update_progress(0, "🟢 Ready to download", "", "💡 *Tip: Choose 128k for car compatibility*")
            self.hide_progress_bar()
        except Exception as e:
            debug_print(f"❌ Progress sıfırlama hatası: {e}", "ERROR")

    def scan_existing_music(self):
        """Mevcut müzik dosyalarını tarayıp history'ye ekle"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_folder = os.path.join(script_dir, "Music")
        
        if not os.path.exists(music_folder):
            messagebox.showwarning("⚠️ Warning", "Music folder not found!")
            return
        
        # Desteklenen ses dosyası formatları
        audio_extensions = {'.mp3', '.m4a', '.wav', '.flac', '.ogg', '.wma', '.aac'}
        
        found_music = []
        try:
            for file in os.listdir(music_folder):
                file_path = os.path.join(music_folder, file)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in audio_extensions:
                        # Dosya isminden müzik ismini çıkar
                        music_title = os.path.splitext(file)[0]
                        
                        # Çok uzun isimleri kısalt
                        if len(music_title) > 60:
                            music_title = music_title[:57] + "..."
                        
                        found_music.append(music_title)
            
            if found_music:
                # Mevcut history'yi yükle
                history = load_history()
                if "music_titles" not in history:
                    history["music_titles"] = []
                
                # Yeni müzikleri ekle (duplikat kontrolü ile)
                new_count = 0
                for title in found_music:
                    if title not in history["music_titles"]:
                        history["music_titles"].append(title)
                        new_count += 1
                
                # History'yi kaydet ve güncelle
                save_history(history)
                self.load_history_display()
                
                messagebox.showinfo("🎵 Scan Complete", 
                                  f"*Scan completed!*\n\n"
                                  f"📁 Found: {len(found_music)} music files\n"
                                  f"➕ Added: {new_count} new entries\n"
                                  f"🔄 Duplicates skipped: {len(found_music) - new_count}")
            else:
                messagebox.showinfo("🎭 No Music", 
                                  "*No music files found!*\n\n"
                                  f"📂 Searched in: Music folder\n"
                                  f"🎵 Supported formats: MP3, M4A, WAV, FLAC, OGG, WMA, AAC")
                
        except Exception as e:
            messagebox.showerror("❌ Scan Error", f"Error scanning music folder:\n{str(e)}")
            
    def load_history_display(self):
        """Geçmişi görüntüle - Numaralandırılmış müzik isimleri ile"""
        self.history_listbox.delete(0, tk.END)
        history = load_history()
        
        if "music_titles" in history and history["music_titles"]:
            total_music = len(history["music_titles"])
            
            # Müzik sayısını güncelle
            self.music_count_label.config(text=f"🎵 *Total Music: {total_music}*")
            
            # TÜM müzikleri numaralandırarak göster
            for i, title in enumerate(history["music_titles"], 1):
                # Emoji ile süsleme
                music_emojis = ["🎵", "🎶", "🎼", "🎤", "🎸", "🎹", "🥁", "🎺", "🎻", "🪕"]
                emoji = music_emojis[(i-1) % len(music_emojis)]
                
                # Numaralandırılmış format: "01. 🎵 Song Name"
                number_str = f"{i:02d}."  # 01, 02, 03 formatında
                display_text = f"{number_str} {emoji} {title}"
                self.history_listbox.insert(tk.END, display_text)
        else:
            # Boş durumda
            self.music_count_label.config(text="🎵 *Total Music: 0*")
            self.history_listbox.insert(tk.END, "🎭 No music downloaded yet...")
            self.history_listbox.insert(tk.END, "🌟 Start downloading some awesome music!")
            self.history_listbox.insert(tk.END, "🔍 Or scan existing music files!")
            
    def finish_download_success(self, file_path):
        """İndirme başarılı"""
        self.reset_ui()
        self.load_history_display()
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, "Enter YouTube URL here...")
        
        file_name = os.path.basename(file_path)
        result = messagebox.askyesno("🎉 Download Complete!",
                                   f"✅ {file_name}\n\n"
                                   f"📁 File saved to Music folder.\n\n"
                                   f"Would you like to open the folder?")
        if result:
            self.open_music_folder()
            
    def finish_download_error(self, error_msg):
        """İndirme hatası"""
        self.reset_ui()
        messagebox.showerror("❌ Download Error", error_msg)
        
    def run(self):
        """GUI'yi başlat"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

# Global fonksiyonlar (eski sistem uyumluluğu için)
def reset_ui(download_button, stop_button, progress_bar, status_label):
    """UI sıfırlama fonksiyonu"""
    download_button.config(state='normal', text="🚀 *Download & Convert*")
    stop_button.config(state='disabled')
    progress_bar.pack_forget()
    status_label.config(text="Ready ✨")

def finish_download_success(file_path, url_entry, download_button, stop_button, progress_bar, status_label, root):
    """İndirme başarılı callback"""
    reset_ui(download_button, stop_button, progress_bar, status_label)
    
    # Ana GUI nesnesini bul ve güncelle
    for widget in root.winfo_children():
        if hasattr(widget, 'load_history_display'):
            widget.load_history_display()
            break
    
    url_entry.delete(0, tk.END)
    url_entry.insert(0, "Enter YouTube URL here...")
    
    file_name = os.path.basename(file_path)
    result = messagebox.askyesno("🎉 Download Complete!",
                               f"✅ {file_name}\n\n"
                               f"📁 File saved to Music folder.\n\n"
                               f"Would you like to open the folder?")
    if result:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_folder = os.path.join(script_dir, "Music")
        if sys.platform.startswith('win'):
            os.startfile(music_folder)

def finish_download_error(error_msg, download_button, stop_button, progress_bar, status_label):
    """İndirme hatası callback"""
    reset_ui(download_button, stop_button, progress_bar, status_label)
    messagebox.showerror("❌ Download Error", error_msg)

# Ana uygulama
if __name__ == "__main__":
    app = ModernGUI()
    app.run()
