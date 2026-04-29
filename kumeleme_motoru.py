import pandas as pd
import os

# Gerekli kütüphaneleri yükleyelim
os.system("pip install pyxlsb")

# Dosya adını kontrol et
file_path = '8928a600b75d0ebc2951e6b344a5ed39.xlsb'

def kumeleme_ve_tersine_analiz():
    try:
        # 1. Veriyi Yükle
        print("Veri yükleniyor (120 bin satır işleniyor...)...")
        df = pd.read_excel(file_path, engine='pyxlsb')

        # 2. Sütun Eşleştirme (Burayı kendi sütun isimlerine göre güncelle!)
        # Örnek: MS1 sütununun adı Excel'de 'Maç Sonucu 1' ise onu yazmalısın.
        oran_marketleri = ['MS1', 'UST_25', 'KG_VAR'] 
        skor_sutunu = 'SKOR'

        # 3. Kodlama (A1, B2 Mantığı)
        # Her benzersiz oranı bir koda çeviriyoruz
        print("Oranlar parmak izine dönüştürülüyor...")
        for market in oran_marketleri:
            df[f'{market}_KOD'] = market + "_" + df[market].astype(str)

        # 4. Kümeleme: Skorlara göre maçları grupla
        print("Skor kümeleri analiz ediliyor...")
        skor_gruplari = df.groupby(skor_sutunu)

        altin_kurallar = []

        for skor, grup in skor_gruplari:
            if len(grup) < 50: continue  # Çok az maç olan skorları ele

            # Bu skor kümesinde en sık görülen oran kombinasyonunu bul
            # Kodlanmış sütunları birleştirip maçın 'DNA'sını çıkarıyoruz
            grup['DNA'] = grup[[f'{m}_KOD' for m in oran_marketleri]].apply(lambda x: '-'.join(x), axis=1)
            en_sik_dna = grup['DNA'].value_counts().idxmax()
            tekrar_sayisi = grup['DNA'].value_counts().max()
            
            # Bu DNA'nın tüm veri setindeki başarısını ölç
            toplam_bu_dna = df[[f'{m}_KOD' for m in oran_marketleri]].apply(lambda x: '-'.join(x), axis=1)
            dna_tum_maclar = df[toplam_bu_dna == en_sik_dna]
            basari_yuzdesi = (len(dna_tum_maclar[dna_tum_maclar[skor_sutunu] == skor]) / len(dna_tum_maclar)) * 100

            if basari_yuzdesi >= 85: # Sadece %85 ve üzeri başarıyı kaydet
                altin_kurallar.append({
                    'Skor_Kumesi': skor,
                    'Parmak_Izi': en_sik_dna,
                    'Gecmis_Mac': len(dna_tum_maclar),
                    'Basari_Orani': round(basari_yuzdesi, 2)
                })

        # 5. Sonuçları Raporla
        print("\n=== TESPİT EDİLEN ALTIN FİLTRE KALIPLARI ===")
        kurallar_df = pd.DataFrame(altin_kurallar)
        if not kurallar_df.empty:
            print(kurallar_df.sort_values(by='Basari_Orani', ascending=False))
            kurallar_df.to_csv('altin_kurallar.csv', index=False)
            print("\nFiltreler 'altin_kurallar.csv' olarak kaydedildi.")
        else:
            print("Kriterlere uygun (A1, B2...) kalıp bulunamadı. Market sayısını artırabilirsin.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    kumeleme_ve_tersine_analiz()
