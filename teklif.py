import streamlit as st
from fpdf import FPDF
from datetime import date
import os

# --- AYARLAR ---
SAVE_DIR = "TEKLİFLER"
TEMP_DIR = "GECICI_RESIMLER"
LOGO_PATH = "logo.png"

for klasor in [SAVE_DIR, TEMP_DIR]:
    if not os.path.exists(klasor): os.makedirs(klasor)

def dosya_adi_yap(metin):
    replacements = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C'}
    metin = str(metin)
    for k, v in replacements.items():
        metin = metin.replace(k, v)
    return "".join(c for c in metin if c.isalnum() or c in (" ", "_")).replace(" ", "_")

# --- ARAYÜZ ---
st.set_page_config(page_title="Alpinetech Teklif", layout="wide")
st.title("🏔️ Alpinetech Teklif Hazırlama")

if 'kategoriler' not in st.session_state:
    st.session_state.kategoriler = []

# --- 1. ÜST BİLGİLER ---
with st.expander("📄 Teklif ve Müşteri Ayarları", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        t_baslik1 = st.text_input("Başlık 1", "TEKNİK SERVİS TEKLİFİ")
        t_tarih = st.text_input("Tarih", date.today().strftime("%d.%m.%Y"))
        para_birimi = st.selectbox("Para Birimi", ["EUR", "TL", "USD"])
        kdv_ekle = st.checkbox("KDV Hesapla (%20)", value=True)
    with c2:
        m_ad = st.text_input("Müşteri Firma", "")
        m_tel = st.text_input("Müşteri Tel", "")
    with c3:
        v_ad = st.text_input("Teklifi Veren", "Kürşad Nuri Örme")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. ÇOKLU GÖRSEL DESTEKLİ İŞ KALEMLERİ ---
st.subheader("📋 İş Kalemleri")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([2, 1])
    with col_k1:
        kat_adi = st.text_input("İş/Ürün Adı")
        kat_aciklama = st.text_area("Açıklama / Teknik Detaylar")
        # ÇOKLU DOSYA YÜKLEME AKTİF
        yuklenen_dosyalar = st.file_uploader("Ürün Görselleri (Birden fazla seçebilirsiniz)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        ekle_btn = st.form_submit_button("➕ Listeye Ekle")
        
    if ekle_btn and kat_adi:
        kaydedilen_resimler = []
        if yuklenen_dosyalar:
            for idx, dosya in enumerate(yuklenen_dosyalar):
                dosya_yolu = os.path.join(TEMP_DIR, f"img_{len(st.session_state.kategoriler)}_{idx}.jpg")
                with open(dosya_yolu, "wb") as f:
                    f.write(dosya.getbuffer())
                kaydedilen_resimler.append(dosya_yolu)
        
        st.session_state.kategoriler.append({
            "baslik": kat_adi, 
            "aciklama": kat_aciklama, 
            "adet": kat_adet,
            "fiyat": kat_fiyat,
            "toplam": kat_adet * kat_fiyat,
            "resimler": kaydedilen_resimler
        })

# Önizleme Listesi
for i, k in enumerate(st.session_state.kategoriler):
    with st.container(border=True):
        c_p1, c_p2, c_p3 = st.columns([1, 4, 1])
        with c_p1:
            if k['resimler']:
                st.image(k['resimler'][0], width=100) # İlk resmi önizlemede göster
                st.caption(f"{len(k['resimler'])} Resim")
        with c_p2:
            st.write(f"**{k['baslik']}**")
            st.write(f"{k['adet']} Adet x {k['fiyat']:,.2f} = {k['toplam']:,.2f} {para_birimi}")
        with c_p3:
            if st.button("Sil", key=f"sil_{i}"):
                st.session_state.kategoriler.pop(i)
                st.rerun()

st.divider()

# --- 3. PDF OLUŞTURMA ---
dosya_adi = st.text_input("Dosya Adı", "Alpinetech_Teklif")

if st.button("🚀 TEKLİFİ OLUŞTUR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Önce iş kalemi eklemelisiniz!")
    else:
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # --- Header ---
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"ALPINETECH - {t_baslik1}", ln=1, align='C')
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, f"Tarih: {t_tarih}", ln=1, align='R')
            pdf.ln(10)

            # --- Kalemler ---
            for k in st.session_state.kategoriler:
                # Sayfada yer kalmadıysa yeni sayfa aç (Resimler için önemli)
                if pdf.get_y() > 220: pdf.add_page()
                
                pdf.set_font("Arial", 'B', 12)
                pdf.set_text_color(46, 116, 181)
                pdf.cell(0, 8, k['baslik'], ln=1)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", '', 10)
                pdf.ln(2)
                pdf.multi_cell(0, 5, k['aciklama'])
                
                # Çoklu Resim Yerleşimi
                if k['resimler']:
                    pdf.ln(2)
                    x_start = 10
                    y_start = pdf.get_y()
                    img_w = 45 # Her resim 4.5 cm
                    
                    for idx, r_yolu in enumerate(k['resimler']):
                        # Resimleri yan yana 4'lü dizebiliriz
                        col = idx % 4
                        row = idx // 4
                        pdf.image(r_yolu, x=x_start + (col * (img_w + 2)), y=y_start + (row * (img_w + 2)), w=img_w)
                        
                        # Eğer alt satıra geçtiyse Y koordinatını güncelle
                        if col == 3 or idx == len(k['resimler']) - 1:
                            pdf.set_y(y_start + ((row + 1) * (img_w + 5)))

                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 8, f"Tutar: {k['toplam']:,.2f} {para_birimi}", ln=1, align='R')
                pdf.ln(5)

            # --- Sonuç ---
            safe_name = dosya_adi_yap(dosya_adi) + ".pdf"
            out_path = os.path.join(SAVE_DIR, safe_name)
            pdf.output(out_path)
            
            st.success("PDF başarıyla oluşturuldu!")
            with open(out_path, "rb") as f:
                st.download_button("📩 PDF İndir", f, file_name=safe_name)
        
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
