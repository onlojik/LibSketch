import sys
import subprocess
import os

# --- OTOMATİK KÜTÜPHANE KONTROLÜ VE YÜKLEME ---
def paketleri_kontrol_et_ve_yukle():
    gerekli_paketler = {
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "openpyxl": "openpyxl"
    }
    
    for modul_adi, paket_adi in gerekli_paketler.items():
        try:
            __import__(modul_adi)
        except ImportError:
            print(f"'{modul_adi}' bulunamadı, otomatik yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", paket_adi])
            print(f"'{modul_adi}' başarıyla yüklendi!")

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap
import random
import pandas as pd
import math

# --- AYARLAR ---
DOSYA_ADI = "BookList.xlsx"
CIKTI_ADI = "bookshelf.png"

# A4 Boyutları (İnç)
FIG_WIDTH = 8.27
FIG_HEIGHT = 11.69

BG_COLOR = "#FFFFFF"     # Arka plan rengi
SHELF_COLOR = "#888888"  # Raf rengi
BOOK_EDGE_COLOR = "#444444" # Kitap kenar çizgisi rengi

MAX_KITAP = 100

# --- RENK PALETİ (Sarı Tonları) ---
RENK_PALETI = [
    "#FFD700", # Altın Sarısı
    "#FFEC99", # Açık Sarı
    "#FFC300", # Koyu Sarı
    "#F4D03F", # Güneş Sarısı
    "#F7DC6F", # Krem Sarı
]

def veri_oku():
    if not os.path.exists(DOSYA_ADI):
        print(f"HATA: '{DOSYA_ADI}' dosyası bulunamadı!")
        sys.exit()

    try:
        df = pd.read_excel(DOSYA_ADI, dtype=str)
        df.columns = [c.strip() for c in df.columns]
        
        if "Book Name" not in df.columns or "Author" not in df.columns:
             df = df.iloc[:, 0:2]
             df.columns = ["Book Name", "Author"]
        
        df = df.dropna(subset=["Book Name", "Author"])
        
        kitap_listesi = []
        for index, row in df.iterrows():
            ad = str(row["Book Name"]).strip()
            yazar = str(row["Author"]).strip()
            if ad.lower() != "nan" and yazar.lower() != "nan":
                kitap_listesi.append((ad, yazar))
        
        if len(kitap_listesi) > MAX_KITAP:
            kitap_listesi = kitap_listesi[:MAX_KITAP]
        return kitap_listesi
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit()

def format_author_name(full_name):
    # Yazarları mümkün olduğunca 2-3 satıra bölmeye çalış
    parts = full_name.split()
    if len(parts) >= 3:
        # Örn: "Gabriel Garcia Marquez" -> "Gabriel Garcia\nMarquez"
        mid = len(parts) // 2
        return f"{' '.join(parts[:mid])}\n{' '.join(parts[mid:])}"
    elif len(parts) == 2:
        return f"{parts[0]}\n{parts[1]}"
    return full_name

def chunks_distributed(lst, n):
    if n < 1: n = 1
    k, m = divmod(len(lst), n)
    return [lst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

def get_optimized_font_size(text, box_width, box_height, max_allowed_w):
    """
    OPTİMİZE EDİLMİŞ VERSİYON:
    Büyük kitaplarda (book_height/width büyükse) daha cesur fontlar kullanır.
    """
    if not text: return 1
    
    lines = text.split('\n')
    num_lines = len(lines)
    max_line_len = max([len(line) for line in lines])
    if max_line_len < 1: max_line_len = 1
    
    # --- 1. KISIT: KİTAP KALINLIĞI (Spine Width) ---
    # Eğer kitap çok kalınsa (max_allowed_w > 5 gibi), katsayıyı artır
    # Normalde 2.0, kalın kitapta 2.3
    width_multiplier = 2.0
    if max_allowed_w > 4: 
        width_multiplier = 2.4
        
    font_limit_spine = (max_allowed_w * width_multiplier) / (num_lines * 0.6 + 0.4)
    
    # --- 2. KISIT: KİTAP UZUNLUĞU (Zone Height) ---
    # Yazı uzunluğuna göre font
    # Katsayıyı 1.8 -> 2.2'ye çıkardık, alanı daha agresif doldursun.
    font_limit_zone = (box_width / max_line_len) * 2.2
    
    final_font = min(font_limit_spine, font_limit_zone)
    
    # --- LİMİTLER ---
    # Üst limiti 110'a çıkardık (Devasa kitaplar için)
    if final_font > 110: final_font = 110
    if final_font < 5: final_font = 5 
    
    return final_font

def create_final_bookshelf(book_list, filename=CIKTI_ADI):
    print("Kitaplık Görseli Oluşturuluyor... / Creating a bookshelf image...")
    
    target_per_shelf = 16.7
    needed_shelves = math.ceil(len(book_list) / target_per_shelf)
    if needed_shelves < 1: needed_shelves = 1
    
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    ax.axis('off')
    
    X_LIMIT = 100
    Y_LIMIT = 145 
    ax.set_xlim(0, X_LIMIT)
    ax.set_ylim(0, Y_LIMIT)

    # --- RAF ÇİZİMİ ---
    top_margin = 140
    bottom_margin = 10
    available_height = top_margin - bottom_margin
    step = available_height / needed_shelves
    shelves_y = [bottom_margin + (i * step) for i in range(needed_shelves)]
    
    shelf_thickness = 1.0
    shelf_width_visual = 92 
    shelf_visual_start = (X_LIMIT - shelf_width_visual) / 2
    
    for y in shelves_y:
        rect = patches.Rectangle((shelf_visual_start, y), shelf_width_visual, shelf_thickness, 
                                 linewidth=0, facecolor=SHELF_COLOR)
        ax.add_patch(rect)

    books_per_shelf = chunks_distributed(book_list, needed_shelves)
    books_per_shelf.reverse() 

    shelf_height_gap = step 
    max_book_height = shelf_height_gap * 0.88 
    gap = 0.0 

    for i, shelf_books in enumerate(books_per_shelf):
        shelf_y = shelves_y[i]
        count = len(shelf_books)
        if count == 0: continue

        total_gap_space = (count - 1) * gap
        available_width = shelf_width_visual - total_gap_space
        
        # Ağırlık hesabı 
        weights = []
        for t, a in shelf_books:
            w_score = len(t) + len(a)
            if w_score < 8: w_score = 8 
            weights.append(w_score)
        total_weight = sum(weights)
        
        current_x = shelf_visual_start
        
        for idx, (title, author) in enumerate(shelf_books):
            share = weights[idx] / total_weight
            w = available_width * share
            h = max_book_height * random.uniform(0.90, 0.98) 
            
            # Kitap çiz
            secilen_renk = random.choice(RENK_PALETI)
            rect = patches.Rectangle((current_x, shelf_y + shelf_thickness), 
                                     w, h, 
                                     linewidth=0.8, 
                                     edgecolor=BOOK_EDGE_COLOR, 
                                     facecolor=secilen_renk)
            ax.add_patch(rect)
            center_x = current_x + w / 2

            # ============================================================
            # --- BÖLGE 1: YAZAR (%25) ---
            # ============================================================
            author_zone_ratio = 0.25
            author_zone_height = h * author_zone_ratio
            author_center_y = (shelf_y + shelf_thickness) + (author_zone_height / 2)
            
            author_formatted = format_author_name(author)
            
            a_font_size = get_optimized_font_size(
                text=author_formatted,
                box_width=author_zone_height * 0.92, 
                box_height=w,
                max_allowed_w=w
            )

            ax.text(center_x, author_center_y, 
                    author_formatted, 
                    rotation=90, 
                    va='center', ha='center',
                    multialignment='center',
                    fontsize=a_font_size, 
                    color="#444444", 
                    fontstyle='italic')

            # ============================================================
            # --- BÖLGE 2: BAŞLIK (%75) ---
            # ============================================================
            title_zone_ratio = 0.75
            title_zone_height = h * title_zone_ratio
            title_center_y = (shelf_y + shelf_thickness) + author_zone_height + (title_zone_height / 2)
            
            # --- GELİŞMİŞ WRAP MANTIĞI ---
            # Kitap çok uzun olsa bile tek satırda 22 karakteri geçmesine izin verme.
            # Bu, metni alt satıra atarak fontun büyümesini sağlar (Blok etkisi).
            
            max_chars_per_line = 22
            # Eğer kitap çok inceyse (w < 2), mecburen daha az karakter sığar
            if w < 2.0: 
                max_chars_per_line = 40 # İnce kitapta satır bölmek fontu öldürür, o yüzden bölme (akışına bırak)
            else:
                # Kalın kitapta böl ki büyüsün
                max_chars_per_line = 22

            # Hedef genişlik: Alanın %35'i veya max limit
            calc_wrap = int(title_zone_height * 0.35)
            target_wrap = min(calc_wrap, max_chars_per_line)
            if target_wrap < 8: target_wrap = 8
            
            wrapper = textwrap.TextWrapper(width=target_wrap, break_long_words=False)
            wrapped_list = wrapper.wrap(title)
            
            # Retry logic
            retry = 0
            while len(wrapped_list) > 3 and retry < 5:
                target_wrap += 4
                wrapper = textwrap.TextWrapper(width=target_wrap, break_long_words=False)
                wrapped_list = wrapper.wrap(title)
                retry += 1
                
            wrapped_title = "\n".join(wrapped_list)
            
            t_font_size = get_optimized_font_size(
                text=wrapped_title,
                box_width=title_zone_height * 0.96, # Biraz daha pay ver
                box_height=w,
                max_allowed_w=w
            )
            
            ax.text(center_x, title_center_y, 
                    wrapped_title, 
                    rotation=90, 
                    va='center', ha='center',
                    multialignment='center',
                    fontsize=t_font_size, 
                    fontweight='bold',
                    color="#000000",
                    linespacing=0.95)

            current_x += w 

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor=BG_COLOR)
    print(f"Final görsel oluşturuldu: '{filename}'")

if __name__ == "__main__":
    veriler = veri_oku()
    if veriler:
        create_final_bookshelf(veriler)
    else:
        print("Veri yok.")