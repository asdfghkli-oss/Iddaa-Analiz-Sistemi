import pandas as pd
import os

# Gerekli kütüphaneyi yükle
os.system("pip install pyxlsb")

file_path = '8928a600b75d0ebc2951e6b344a5ed39.xlsb'

def sutunlari_getir():
    try:
        # Verinin sadece ilk 5 satırını başlıkları görmek için oku
        df = pd.read_excel(file_path, engine='pyxlsb', nrows=5)
        print("--- DOSYADAKİ SÜTUN BAŞLIKLARI ---")
        print(df.columns.tolist())
        print("\n--- ÖRNEK VERİ (İLK 3 SATIR) ---")
        print(df.head(3))
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    sutunlari_getir()
