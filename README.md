# YouTube MP3 Dönüştürücü Bot

Bu Python botu, YouTube videolarını kolayca MP3 formatına indirmenizi ve dönüştürmenizi sağlayan basit bir grafik arayüz (GUI) uygulamasıdır.

## Özellikler

* **YouTube Video İndirme:** Verdiğiniz bir YouTube URL'sindeki videonun sesini indirir.

* **Otomatik MP3 Dönüştürme:** İndirilen dosyayı otomatik olarak MP3 formatına dönüştürür.

* **İndirme Geçmişi:** İndirilen şarkıların bir listesini tutar ve dosya klasörünüzle senkronize eder.

* **Kullanıcı Dostu Arayüz:** İndirme sürecini takip etmek için bir ilerleme çubuğu ve durum mesajları bulunur.

* **Klasör Yönetimi:** İndirilen tüm müzikleri `Müzikler` adlı bir klasörde saklar.

## Gereksinimler

Bu botun çalışması için aşağıdaki Python kütüphanelerinin yüklü olması gerekmektedir:

* `yt-dlp`

* `tkinter` (genellikle Python ile birlikte gelir)

## Kurulum

1. Öncelikle, sisteminizde Python'un kurulu olduğundan emin olun.

2. Gerekli kütüphaneyi yüklemek için terminali veya komut istemini açın ve aşağıdaki komutu çalıştırın:

   ```bash
   pip install yt-dlp
   ```

## Nasıl Kullanılır

1. `bot.py` dosyasını çalıştırın.

2. Açılan arayüze indirmek istediğiniz YouTube videosunun URL'sini yapıştırın.

3. `Dönüştür ve İndir` butonuna tıklayın.

4. Bot, indirme ve dönüştürme işlemini tamamladığında, size bir bildirim penceresi gösterecektir. Tüm dosyalarınız `Müzikler` klasörüne kaydedilecektir.

## Not

Bu program, FFMPEG kurulu olmasa bile çalışacak şekilde yapılandırılmıştır. Ancak, dönüştürme ve indirme işlemleri için `yt-dlp` kütüphanesini kullanır.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# YouTube MP3 Converter Bot

This Python bot is a simple graphical user interface (GUI) application that allows you to easily download and convert YouTube videos to MP3 format.

## Features

* **YouTube Video Downloading:** Downloads the audio from a YouTube URL you provide.

* **Automatic MP3 Conversion:** Automatically converts the downloaded file to MP3 format.

* **Download History:** Keeps a list of downloaded songs and syncs with your file folder.

* **User-Friendly Interface:** Includes a progress bar and status messages to track the download process.

* **Folder Management:** Stores all downloaded music in a folder named `Music`.

## Requirements

The following Python libraries are required for this bot to work:

* `yt-dlp`

* `tkinter` (usually comes with Python)

## Installation

1. First, make sure you have Python installed on your system.

2. To install the necessary library, open your terminal or command prompt and run the following command:

   ```bash
   pip install yt-dlp
   ```

## How to Use

1. Run the `bot.py` file.

2. Paste the URL of the YouTube video you want to download into the interface that opens.

3. Click the `Convert and Download` button.

4. When the bot completes the download and conversion, it will show you a notification window. All your files will be saved in the `Music` folder.

## Note

This program is configured to work even if FFMPEG is not installed. However, it uses the `yt-dlp` library for downloading and conversion.
