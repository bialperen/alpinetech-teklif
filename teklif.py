import streamlit as st
from fpdf import FPDF
from datetime import date
import os
from PIL import Image # Görsel boyutlarını kontrol etmek için

# --- AYARLAR ---
SAVE_DIR = "TEKLİFLER"
TEMP_DIR = "GECICI_RESIMLER" # Resimlerin PDF'e işlenene kadar duracağı yer
LOGO_PATH = "logo.png"

if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)

def dosya_adi_yap(metin):
    replacements = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C', 'â':'a', 'Â':'A'}
    metin = str(metin)
    for k, v in replacements.items():
        metin = metin.replace(k, v)
    return metin.replace(" ", "_")

# --- ARAYÜZ ---
st.set_page_config(page_title="Alpinetech Teklif Hazırlama", layout="wide")
st.title("🏔️ Alpinetech")

if 'kategoriler' not in st.session_state:
    st.session_state.kategoriler = []

# --- 1. ÜST BİLGİLER (Müşteri vb.) ---
# (Buradaki mevcut kodunuzu aynen koruyun, yer kaplamaması için özet geçiyorum)
with st.expander("📄 Teklif, İletişim ve KDV Ayarları", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        t_baslik1 = st.text_input("Başlık (1. Satır)", "TEKNİK SERVİS TEKLİFİ")
        t_baslik2 = st.text_input("Başlık (2. Satır)", "")
        t_tarih = st.text_input("Tarih", date.today().strftime("%d.%m.%Y"))
        para_birimi = st.selectbox("Para Birimi", ["EUR", "TL", "USD"])
        kdv_ekle = st.checkbox("KDV Hesapla", value=False)
        kdv_oran = st.number_input("KDV Oranı (%)", min_value=0, value=20)
    with c2:
        m_ad = st.text_input("Müşteri Firma/Kişi", "")
        m_tel = st.text_input("Müşteri Tel", "")
        m_mail = st.text_input("Müşteri E-Posta", "")
    with c3:
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. GÖRSEL DESTEKLİ İŞ KALEMLERİ ---
st.subheader("📋 İş Kalemleri ve Görseller")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([2, 1])
    with col_k1:
        kat_adi = st.text_input("Kategori Adı (Örn: Siemens S7-1200 Bakımı)")
        kat_aciklama = st.text_area("Maddeler / Teknik Detaylar")
        yuklenen_dosya = st.file_uploader("Ürün Görseli Ekle (Opsiyonel)", type=['jpg', 'jpeg', 'png'])
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        st.markdown("<br>"*4, unsafe_allow_html=True)
        ekle_btn = st.form_submit_button("➕ Kategori ve Görsel Ekle")
        
    if ekle_btn and kat_adi:
        resim_yolu = None
        if yuklenen_dosya is not None:
            # Resmi geçici klasöre kaydet
            resim_yolu = os.path.join(TEMP_DIR, f"temp_{len(st.session_state.kategoriler)}_{yuklenen_dosya.name}")
            with open(resim_yolu, "wb") as f:
                f.write(yuklenen_dosya.getbuffer())
        
        st.session_state.kategoriler.append({
            "baslik": kat_adi, 
            "aciklama": kat_aciklama, 
            "adet": kat_adet,
            "fiyat": kat_fiyat,
            "toplam": kat_adet * kat_fiyat,
            "resim": resim_yolu
        })

# Listeleme Alanı
if st.session_state.kategoriler:
    for i, k in enumerate(st.session_state.kategoriler):
        c_disp1, c_disp2, c_disp3 = st.columns([2, 5, 1])
        with c_disp1:
            if k['resim']:
                st.image(k['resim'], width=150)
            else:
                st.info("Görsel yok")
        with c_disp2:
            st.markdown(f"**{k['baslik']}**")
            st.caption(k['aciklama'])
            st.write(f"{k['adet']} Adet x {k['fiyat']:,.2f} {para_birimi}")
        with c_disp3:
            if st.button("🗑️", key=f"kat_sil_{i}"):
                if k['resim'] and os.path.exists(k['resim']):
                    os.remove(k['resim']) # Dosyayı sil
                st.session_state.kategoriler.pop(i)
                st.rerun()
        st.write("---")

# (Şartlar bölümü mevcut kodunuzdaki gibi devam eder...)
# --- PDF OLUŞTURMA BÖLÜMÜNDEKİ DEĞİŞİKLİKLER ---
# PDF oluşturma butonunun içine şu mantığı ekleyeceğiz:

if st.button("🚀 TEKLİFİ OLUŞTUR VE İNDİR", type="primary"):
    # ... (PDF Başlangıç ayarları, Fontlar, Logo vb. mevcut kodunuzdaki kısımlar)
    
    pdf = FPDF()
    pdf.add_page()
    # (Mevcut PDF header ve müşteri bilgileri kodları buraya gelecek...)

    for k in st.session_state.kategoriler:
        # Başlık ve Çizgi
        pdf.set_text_color(46, 116, 181)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, k['baslik'], ln=1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)

        # Görsel Kontrolü ve Yerleşimi
        current_y = pdf.get_y()
        if k['resim']:
            # Resmi sola koyalım (40mm genişlik), açıklamayı yanına yazalım
            pdf.image(k['resim'], x=10, y=current_y, w=40)
            pdf.set_xy(55, current_y) # Yazıyı resmin sağına kaydır
            pdf.set_font("Arial", '', 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(145, 5, k['aciklama'])
            # Resim veya yazıdan hangisi daha uzunsa y koordinatını ona göre ayarla
            new_y = max(current_y + 35, pdf.get_y() + 5) 
            pdf.set_y(new_y)
        else:
            pdf.set_font("Arial", '', 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, k['aciklama'])

        # Fiyat kutusu
        pdf.ln(1)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, f"Toplam: {k['toplam']:,.2f} {para_birimi}", border=1, align='R', ln=1)
        pdf.ln(5)

    # ... (Alt toplamlar ve Şartlar bölümleri...)
    # Son olarak geçici resimleri temizle (isteğe bağlı)
    # for k in st.session_state.kategoriler:
    #     if k['resim'] and os.path.exists(k['resim']): os.remove(k['resim'])
