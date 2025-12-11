#!/bin/bash

# Dosyanın bulunduğu klasöre git (Burası çok önemli, yoksa dosyaları bulamaz)
cd "$(dirname "$0")"

# Kullanıcıya bilgi ver
echo "The library image generator is starting... / Kütüphane görsel oluşturucu başlatılıyor..."

# Python kodunu çalıştır (Mac'te genellikle python3 komutu kullanılır)
python3 LibSketch.py

# İşlem bitince pencere hemen kapanmasın diye beklet
echo "The process is complete. Press a key to exit... / İşlem tamamlandı. Çıkmak için bir tuşa basın..."
read -n 1 -s