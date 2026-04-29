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
        # Dosyayı oku
        df = pd.read_excel(FILE_PATH, engine='pyxlsb')
        # Sütun isimlerindeki boşlukları temizle
        df.columns = [str(c).strip() for c in df.columns]
        # Hatalı/Boş satırları temizle
        df = df.dropna(how='all')
        return df
    return None

df = veriyi_yukle()

if df is not None:
    st.sidebar.success("✅ Veri dosyası yüklendi.")
    
    st.sidebar.header("Filtre Ayarları")
    min_basari = st.sidebar.slider("Minimum Başarı Oranı (%)", 70, 100, 85)
    min_mac = st.sidebar.slider("Minimum Maç Sayısı", 5, 100, 20)
    
    cols = df.columns.tolist()
    # Skor sütununu seç
    skor_col = st.sidebar.selectbox("Skor Sütunu Hangisi?", cols)
    # Analiz edilecek oranları seç
    market_cols = st.sidebar.multiselect("Analiz Edilecek Oranlar", cols)

    if st.sidebar.button("Analizi Başlat ve Kümele"):
        if not market_cols:
            st.error("Lütfen en az bir oran marketi seçin!")
        else:
            with st.spinner("DNA Kalıpları analiz ediliyor..."):
                temp_df = df.copy()
                
                # HATA ÖNLEYİCİ: Tüm oranları metne çevir ve boşları 'Yok' yap
                for m in market_cols:
                    temp_df[m] = temp_df[m].fillna('0.00').astype(str)
                    temp_df[f'{m}_KOD'] = m + "_" + temp_df[m]
                
                kod_sutunlari = [f'{m}_KOD' for m in market_cols]
                
                # Güvenli birleştirme yöntemi
                temp_df['DNA'] = temp_df[kod_sutunlari].agg('-'.join, axis=1)
                
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
                            "Toplam Maç": len(dna_maclari),
                            "Başarı %": round(oran, 2)
                        })
                
                if sonuclar:
                    res_df = pd.DataFrame(sonuclar).sort_values(by="Başarı %", ascending=False)
                    st.write(f"### 🏆 Bulunan En Keskin {len(res_df)} Filtre")
                    st.dataframe(res_df, use_container_width=True)
                    st.balloons()
                else:
                    st.warning("Bu kriterlerde keskin bir kalıp bulunamadı. Ayarları esnetmeyi deneyin.")
else:
    st.error("Dosya bulunamadı! Lütfen dosya adını kontrol edin.")
