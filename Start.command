#!/bin/bash

# Dosyanın bulunduğu klasöre git (Burası çok önemli, yoksa dosyaları bulamaz)
cd "$(dirname "$0")"

# Kullanıcıya bilgi ver
echo "Kütüphane oluşturucu başlatılıyor..."

# Python kodunu çalıştır (Mac'te genellikle python3 komutu kullanılır)
python3 LibSketch.py

# İşlem bitince pencere hemen kapanmasın diye beklet
echo "İşlem tamamlandı. Çıkmak için bir tuşa basın..."
read -n 1 -s