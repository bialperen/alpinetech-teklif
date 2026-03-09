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

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Alpinetech Teklif", layout="wide")
st.title("🏔️ Alpinetech Teklif Sistemi")

# --- SESSION STATE (GERİ GETİRİLENLER) ---
if 'kategoriler' not in st.session_state:
    st.session_state.kategoriler = []

if 'sartlar' not in st.session_state:
    st.session_state.sartlar = [
        "Ulaşım ve konaklama giderleri teklif bedeline dâhildir.",
        "Fiyatlarımıza KDV (%20) dâhil değildir.",
        "Ödeme Koşulları peşin.",
        "Teklif 15 gün geçerlidir."
    ]

if 'musteriler' not in st.session_state:
    st.session_state.musteriler = {
        "Murat Bey": {"tel": "+90 533 741 38 60", "mail": "alp.orme1@gmail.com"}
    }

# --- 1. ÜST BİLGİLER VE MÜŞTERİ SEÇİMİ ---
with st.expander("📄 Teklif ve Müşteri Ayarları", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**📌 Detaylar**")
        t_baslik1 = st.text_input("Başlık 1", "TEKNİK SERVİS TEKLİFİ")
        t_tarih = st.text_input("Tarih", date.today().strftime("%d.%m.%Y"))
        para_birimi = st.selectbox("Para Birimi", ["EUR", "TL", "USD"])
        kdv_ekle = st.checkbox("KDV Hesapla", value=True)
        kdv_oran = st.number_input("KDV (%)", value=20)

    with c2:
        st.markdown("**🏢 Müşteri**")
        secenekler = ["-- Yeni --"] + list(st.session_state.musteriler.keys())
        secilen = st.selectbox("Kayıtlı Müşteri", secenekler)
        
        m_ad = st.text_input("Firma Adı", value="" if secilen=="-- Yeni --" else secilen)
        m_tel = st.text_input("Telefon", value="" if secilen=="-- Yeni --" else st.session_state.musteriler[secilen]["tel"])
        
        if st.button("💾 Müşteriyi Kaydet"):
            st.session_state.musteriler[m_ad] = {"tel": m_tel, "mail": ""}
            st.success("Kaydedildi!")

    with c3:
        st.markdown("**🧑‍💻 Teklifi Veren**")
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon ", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta ", "info@alpinetech.com.tr")

st.divider()

# --- 2. ÇOKLU RESİMLİ İŞ KALEMLERİ ---
st.subheader("📋 İş Kalemleri")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([2, 1])
    with col_k1:
        kat_adi = st.text_input("İş Kalemi Adı")
        kat_aciklama = st.text_area("Teknik Detaylar")
        yuklenenler = st.file_uploader("Resimleri Seçin", type=['jpg','png','jpeg'], accept_multiple_files=True)
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        ekle_btn = st.form_submit_button("➕ Listeye Ekle")
        
    if ekle_btn and kat_adi:
        resim_listesi = []
        if yuklenenler:
            for i, dosya in enumerate(yuklenenler):
                # Resimleri database yerine yerel klasöre geçici isimle atıyoruz
                yol = os.path.join(TEMP_DIR, f"temp_{len(st.session_state.kategoriler)}_{i}.jpg")
                with open(yol, "wb") as f:
                    f.write(dosya.getbuffer())
                resim_listesi.append(yol)
        
        st.session_state.kategoriler.append({
            "baslik": kat_adi, "aciklama": kat_aciklama, "adet": kat_adet,
            "fiyat": kat_fiyat, "toplam": kat_adet * kat_fiyat, "resimler": resim_listesi
        })

# Listeleme
for i, k in enumerate(st.session_state.kategoriler):
    with st.container(border=True):
        c_l1, c_l2, c_l3 = st.columns([1, 4, 1])
        with c_l1:
            if k['resimler']: st.image(k['resimler'][0], width=100)
        with c_l2:
            st.write(f"**{k['baslik']}** - {k['toplam']:,.2f} {para_birimi}")
        with c_l3:
            if st.button("Sil", key=f"del_{i}"):
                st.session_state.kategoriler.pop(i)
                st.rerun()

# --- 3. GENEL ŞARTLAR (GERİ GETİRİLDİ) ---
st.subheader("⚖️ Genel Şartlar")
with st.expander("Şartları Düzenle"):
    yeni_sart = st.text_input("Yeni Şart")
    if st.button("Ekle") and yeni_sart:
        st.session_state.sartlar.append(yeni_sart)
    for i, s in enumerate(st.session_state.sartlar):
        sc1, sc2 = st.columns([9,1])
        sc1.write(f"- {s}")
        if sc2.button("X", key=f"sdel_{i}"):
            st.session_state.sartlar.pop(i)
            st.rerun()

st.divider()

# --- 4. PDF OLUŞTURMA (HATASIZ MANTIK) ---
dosya_adi = st.text_input("Dosya Adı", "Alpinetech_Teklif")

if st.button("🚀 PDF OLUŞTUR VE İNDİR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Kalem eklemediniz!")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # Header & Logo
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=150, y=10, w=50)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "ALPINETECH MÜHENDİSLİK", ln=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, f"Tarih: {t_tarih}", ln=1)
        pdf.ln(10)

        ara_toplam = 0
        for k in st.session_state.kategoriler:
            if pdf.get_y() > 230: pdf.add_page()
            
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(46, 116, 181)
            pdf.cell(0, 8, k['baslik'], ln=1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.ln(2)
            pdf.multi_cell(0, 5, k['aciklama'])
            
            # Resimler (Eğer varsa yan yana diz)
            if k['resimler']:
                pdf.ln(2)
                y_konum = pdf.get_y()
                for idx, r in enumerate(k['resimler']):
                    pdf.image(r, x=10 + (idx%4)*48, y=y_konum + (idx//4)*40, w=45)
                    if idx == len(k['resimler'])-1:
                        pdf.set_y(y_konum + (idx//4 + 1)*45)
            
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 7, f"Tutar: {k['toplam']:,.2f} {para_birimi}", ln=1, align='R')
            pdf.ln(5)
            ara_toplam += k['toplam']

        # Hesaplamalar
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        if kdv_ekle:
            kdv = ara_toplam * (kdv_oran/100)
            pdf.cell(0, 6, f"Ara Toplam: {ara_toplam:,.2f} {para_birimi}", ln=1, align='R')
            pdf.cell(0, 6, f"KDV (%{kdv_oran}): {kdv:,.2f} {para_birimi}", ln=1, align='R')
            pdf.cell(0, 7, f"GENEL TOPLAM: {ara_toplam+kdv:,.2f} {para_birimi}", ln=1, align='R', border='T')
        else:
            pdf.cell(0, 7, f"TOPLAM: {ara_toplam:,.2f} {para_birimi}", ln=1, align='R', border='T')

        # Şartlar
        if st.session_state.sartlar:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "GENEL SARTLAR", ln=1)
            pdf.set_font("Arial", '', 10)
            for s in st.session_state.sartlar:
                pdf.multi_cell(0, 6, f"- {s}")

        out_pdf = os.path.join(SAVE_DIR, dosya_adi_yap(dosya_adi)+".pdf")
        pdf.output(out_pdf)
        
        with open(out_pdf, "rb") as f:
            st.download_button("📩 PDF Hazır - İndir", f, file_name=os.path.basename(out_pdf))
