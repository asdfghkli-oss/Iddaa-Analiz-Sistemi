import pandas as pd
import os

# XLSB desteği için kütüphaneyi kuralım
os.system("pip install pyxlsb")

# Dosya yolunu kontrol et, GitHub'a yüklediğin isimle aynı olmalı
file_path = '8928a600b75d0ebc2951e6b344a5ed39.xlsb'

def veriyi_tani():
    try:
        # Belleği yormamak için sadece ilk 10 satırı alalım
        df = pd.read_excel(file_path, engine='pyxlsb', nrows=10)
        
        print("--- SÜTUN LİSTESİ ---")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
            
        print("\n--- VERİ YAPISI (İLK 2 SATIR) ---")
        print(df.head(2))
        
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    veriyi_tani()
