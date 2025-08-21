# -*- coding: utf-8 -*-
"""
YouTube MP3 Dönüştürücü - Ana Uygulama
Modern Modüler Sürüm
"""

def main():
    """Ana uygulama fonksiyonu"""
    try:
        # GUI modülünü import et
        from gui_module import ModernGUI
        
        # Ana uygulamayı oluştur ve çalıştır
        print("🚀 YouTube MP3 Converter başlatılıyor...")
        app = ModernGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Modül import hatası: {e}")
        print("Gerekli modüllerin yüklü olduğundan emin olun.")
        input("Çıkmak için Enter'a basın...")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        input("Çıkmak için Enter'a basın...")

if __name__ == "__main__":
    main()
