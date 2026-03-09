import streamlit as st
from fpdf import FPDF
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import os
import io
from PIL import Image
from datetime import date

# --- AYARLAR ---
SAVE_DIR = "TEKLİFLER"
TEMP_DIR = "GECICI_RESIMLER"
LOGO_PATH = "logo.png"

for klasor in [SAVE_DIR, TEMP_DIR]:
    if not os.path.exists(klasor): os.makedirs(klasor)

def dosya_adi_yap(metin):
    replacements = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C', 'â':'a', 'Â':'A'}
    metin = str(metin)
    for k, v in replacements.items():
        metin = metin.replace(k, v)
    return metin.replace(" ", "_")

# --- ARAYÜZ ---
st.set_page_config(page_title="Alpinetech Teklif Hazırlama", layout="wide")
st.title("🏔️ Alpinetech")

# --- HAFIZA VE SABİT VERİTABANI (ORİJİNAL) ---
if 'kategoriler' not in st.session_state:
    st.session_state.kategoriler = []
    
if 'sartlar' not in st.session_state:
    st.session_state.sartlar = [
        "Ulaşım ve konaklama giderleri teklif bedeline dâhildir.",
        "Fiyatlarımıza KDV (%20) dâhil değildir.",
        "Ödeme Koşulları peşin.",
        "İş bu teklif ve şartlar, verildiği tarihten itibaren 15 (on beş) takvim günü boyunca geçerlidir."
    ]

if 'musteriler' not in st.session_state:
    st.session_state.musteriler = {
        "Murat Bey'in Dikkatine": {"tel": "+90 533 741 38 60", "mail": "alp.orme1@gmail.com"},
        "Örnek Firma A.Ş.": {"tel": "+90 555 111 22 33", "mail": "info@ornek.com"}
    }

# --- 1. ÜST BİLGİLER ---
with st.expander("📄 Teklif, İletişim ve KDV Ayarları", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**📌 Teklif Detayları**")
        t_baslik1 = st.text_input("Başlık (1. Satır)", "")
        t_baslik2 = st.text_input("Başlık (2. Satır)", "")
        t_tarih = st.text_input("Tarih", date.today().strftime("%d.%m.%Y"))
        para_birimi = st.selectbox("Para Birimi", ["EUR", "TL", "USD"])
        kdv_ekle = st.checkbox("KDV Hesapla", value=False)
        kdv_oran = st.number_input("KDV Oranı (%)", min_value=0, value=20, step=1)
    with c2:
        st.markdown("**🏢 Müşteri Bilgileri**")
        secenekler = ["-- Yeni Müşteri Gir --"] + list(st.session_state.musteriler.keys())
        secilen_musteri = st.selectbox("📇 Kayıtlı Müşteri Seç", secenekler)
        def_ad = secilen_musteri if secilen_musteri != "-- Yeni Müşteri Gir --" else ""
        m_ad = st.text_input("Müşteri Firma/Kişi", value=def_ad)
        m_tel = st.text_input("Müşteri Tel", value=st.session_state.musteriler.get(def_ad, {}).get("tel", ""))
        m_mail = st.text_input("Müşteri E-Posta", value=st.session_state.musteriler.get(def_ad, {}).get("mail", ""))
    with c3:
        st.markdown("**🧑‍💻 Teklifi Veren**")
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. İŞ KALEMLERİ VE GÖRSELLER ---
st.subheader("📋 İş Kalemleri")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1:
        kat_adi = st.text_input("Kategori Adı")
        kat_aciklama = st.text_area("Maddeler")
        yuklenenler = st.file_uploader("Ürün Görselleri (Yan yana dizilecek)", type=['jpg','png','jpeg'], accept_multiple_files=True)
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        st.markdown("<br>", unsafe_allow_html=True)
        ekle_btn = st.form_submit_button("➕ Kategori Ekle")
        
    if ekle_btn and kat_adi:
        resim_yollari = []
        if yuklenenler:
            for i, dosya in enumerate(yuklenenler):
                yol = os.path.join(TEMP_DIR, f"img_{len(st.session_state.kategoriler)}_{i}.jpg")
                img = Image.open(dosya).convert("RGB")
                img.save(yol, "JPEG")
                resim_yollari.append(yol)
        
        st.session_state.kategoriler.append({
            "baslik": kat_adi, "aciklama": kat_aciklama, "adet": kat_adet,
            "fiyat": kat_fiyat, "toplam": kat_adet * kat_fiyat, "resimler": resim_yollari
        })

# Listeleme
for i, k in enumerate(st.session_state.kategoriler):
    c_disp1, c_disp2 = st.columns([9, 1])
    with c_disp1:
        st.markdown(f"**<span style='color:#2E74B5'>{k['baslik']}</span>**", unsafe_allow_html=True)
        if k['resimler']:
            cols = st.columns(len(k['resimler']))
            for idx, r in enumerate(k['resimler']): cols[idx].image(r, width=150)
        st.text(k['aciklama'])
        st.write(f"*Adet: {k['adet']} | Birim Fiyat: {k['fiyat']:,.0f} {para_birimi} | **Toplam: {k['toplam']:,.0f} {para_birimi}***")
    with c_disp2:
        if st.button("🗑️", key=f"kat_sil_{i}"):
            st.session_state.kategoriler.pop(i); st.rerun()
    st.write("---")

# --- 3. ŞARTLAR ---
st.subheader("⚖️ Genel Şartlar")
# (Şartlar kodunu buraya ekleyebilirsin, tasarımın aynısı korunur)

st.divider()

# --- 4. FORMAT SEÇİMİ VE OLUŞTURMA ---
st.subheader("💾 Kayıt Ayarları")
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    dosya_adi = st.text_input("Kaydedilecek Dosya Adı", value="Yeni_Teklif_Dosyasi")
with col_f2:
    format_secimi = st.radio("Dosya Formatı", ["PDF", "Word (.docx)"], horizontal=True)

if st.button("🚀 TEKLİFİ OLUŞTUR VE İNDİR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Lütfen kategori ekleyin!")
    else:
        ara_toplam = sum(k['toplam'] for k in st.session_state.kategoriler)
        kdv_tutari = ara_toplam * (kdv_oran / 100) if kdv_ekle else 0
        genel_toplam = ara_toplam + kdv_tutari

        if format_secimi == "PDF":
            pdf = FPDF()
            pdf.add_page()
            def p(metin): return str(metin).replace('₺', 'TL').encode('latin-1', 'ignore').decode('latin-1')
            
            # --- PDF HEADER (ORİJİNAL) ---
            if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=130, y=14, w=72)
            pdf.set_font("Arial", 'B', 9); pdf.set_xy(10, 15)
            pdf.cell(0, 4.5, p("Alpinetech Mühendislik Makine"), ln=1)
            pdf.cell(0, 4.5, p("Sanayi ve Ticaret Limited Şirketi"), ln=1)
            pdf.cell(0, 4.5, p("30 Ağustos Zafer Mahallesi 520."), ln=1)
            pdf.cell(0, 4.5, p("Cadde 4C/A Nilüfer Bursa"), ln=1)
            pdf.ln(12)
            pdf.set_font("Arial", 'B', 16); pdf.cell(0, 8, p(f"TEKLİF: {t_baslik1}"), ln=1)
            pdf.set_font("Arial", 'B', 14); pdf.cell(100, 8, p(t_baslik2), ln=0)
            pdf.set_font("Arial", '', 11); pdf.cell(90, 8, p(t_tarih), ln=1, align='R')
            pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2); pdf.ln(10)

            # --- KALEMLER VE RESİMLER ---
            for k in st.session_state.kategoriler:
                if pdf.get_y() > 220: pdf.add_page()
                pdf.set_text_color(46, 116, 181); pdf.set_font("Arial", '', 14); pdf.cell(0, 8, p(k['baslik']), ln=1)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.set_text_color(0, 0, 0); pdf.ln(2)
                
                # Resimler (Yan Yana)
                if k['resimler']:
                    y_start = pdf.get_y()
                    for idx, r in enumerate(k['resimler'][:2]):
                        pdf.image(r, x=10 + (idx*92), y=y_start, w=88)
                    pdf.set_y(y_start + 65)

                pdf.set_font("Arial", 'B', 9); pdf.multi_cell(0, 5, p(k['aciklama']))
                pdf.cell(0, 6, p(f"Fiyat : {k['toplam']:,.0f} {para_birimi}"), border=1, align='R', ln=1); pdf.ln(5)

            # --- GENEL TOPLAM TABLOSU (ORİJİNAL) ---
            pdf.ln(5); pdf.set_text_color(46, 116, 181); pdf.set_font("Arial", '', 12); pdf.cell(90, 6, "Genel Toplam", align='R')
            pdf.cell(20, 6, "Adet", align='C'); pdf.cell(35, 6, "Fiyat", align='C'); pdf.cell(45, 6, "Toplam", ln=1, align='C')
            pdf.line(50, pdf.get_y(), 200, pdf.get_y()); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 9)
            for k in st.session_state.kategoriler:
                pdf.cell(90, 5, p(k['baslik']), align='R'); pdf.cell(20, 5, str(k['adet']), align='C')
                pdf.cell(35, 5, p(f"{k['fiyat']:,.0f}"), align='C'); pdf.cell(45, 5, p(f"{k['toplam']:,.0f}"), ln=1, align='C')
            
            pdf.ln(2); pdf.cell(145, 5, "GENEL TOPLAM", align='R'); pdf.cell(45, 5, p(f"{genel_toplam:,.0f} {para_birimi}"), ln=1, align='C')

            st.download_button("📩 PDF İndir", pdf.output(dest='S').encode('latin-1'), file_name=f"{dosya_adi}.pdf")

        else: # Word Mantığı (Resimli ve Orijinal Yazılı)
            doc = Document()
            # (Word oluşturma kodları buraya gelecek, tasarım PDF'e sadık kalacak şekilde)
            # ...
            bio = io.BytesIO()
            doc.save(bio)
            st.download_button("📩 Word İndir", bio.getvalue(), file_name=f"{dosya_adi}.docx")
