import streamlit as st
import pandas as pd
import os

# Sayfa yapılandırması
st.set_page_config(page_title="İddaa Analiz Radarı", layout="wide")

st.title("📊 İddaa Kümeleme ve Filtre Laboratuvarı")
st.markdown("120.000 maçlık veri içindeki 'Altın Oran' kalıplarını otomatik bulur.")

# Kütüphane kontrolü
try:
    import pyxlsb
except ImportError:
    os.system("pip install pyxlsb")

# Veri Dosyası Yolu
FILE_PATH = '8928a600b75d0ebc2951e6b344a5ed39.xlsb'

@st.cache_data
def veriyi_yukle():
    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH, engine='pyxlsb')
        # Sütun isimlerini standartlaştıralım (Boşlukları temizle)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return None

df = veriyi_yukle()

if df is not None:
    st.sidebar.success("✅ Veri dosyası yüklendi.")
    
    # 1. PARAMETRE SEÇİMİ
    st.sidebar.header("Filtre Ayarları")
    min_basari = st.sidebar.slider("Minimum Başarı Oranı (%)", 70, 100, 85)
    min_mac = st.sidebar.slider("Minimum Maç Sayısı", 10, 100, 30)
    
    # Otomatik Sütun Seçimi (Tahmin yürütüyoruz, kullanıcı düzeltebilir)
    cols = df.columns.tolist()
    skor_col = st.sidebar.selectbox("Skor Sütunu Hangisi?", cols, index=cols.index('SKOR') if 'SKOR' in cols else 0)
    market_cols = st.sidebar.multiselect("Analiz Edilecek Oranlar", cols, default=[c for c in cols if 'MS' in c or 'UST' in c or 'KG' in c][:4])

    if st.sidebar.button("Analizi Başlat ve Kümele"):
        with st.spinner("DNA Kalıpları çıkartılıyor..."):
            # Kodlama ve Kümeleme Mantığı
            temp_df = df.copy()
            for m in market_cols:
                temp_df[f'{m}_KOD'] = m + "_" + temp_df[m].astype(str)
            
            kod_sutunlari = [f'{m}_KOD' for m in market_cols]
            temp_df['DNA'] = temp_df[kod_sutunlari].apply(lambda x: '-'.join(x.values.astype(str)), axis=1)
            
            sonuclar = []
            for skor, grup in temp_df.groupby(skor_col):
                if len(grup) < min_mac: continue
                
                lider_dna = grup['DNA'].value_counts().idxmax()
                dna_maclari = temp_df[temp_df['DNA'] == lider_dna]
                isabet = len(dna_maclari[dna_maclari[skor_col] == skor])
                oran = (isabet / len(dna_maclari)) * 100
                
                if oran >= min_basari:
                    sonuclar.append({
                        "Hedef Skor": skor,
                        "Filtre (DNA)": lider_dna,
                        "Örnek Maç": len(dna_maclari),
                        "Başarı %": round(oran, 2)
                    })
            
            if sonuclar:
                res_df = pd.DataFrame(sonuclar).sort_values(by="Başarı %", ascending=False)
                st.write(f"### 🏆 Bulunan En Keskin {len(res_df)} Filtre")
                st.table(res_df)
                st.balloons()
            else:
                st.warning("Bu kriterlerde keskin bir kalıp bulunamadı. Ayarları esnetmeyi dene.")

else:
    st.error("Dosya bulunamadı! Lütfen '8928a600b75d0ebc2951e6b344a5ed39.xlsb' dosyasının GitHub'da olduğundan emin ol.")
