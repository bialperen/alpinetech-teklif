import streamlit as st
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import os
import io

# --- AYARLAR ---
SAVE_DIR = "TEKLİFLER"
LOGO_PATH = "logo.png"

if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

def dosya_adi_yap(metin):
    replacements = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C', 'â':'a', 'Â':'A'}
    metin = str(metin)
    for k, v in replacements.items():
        metin = metin.replace(k, v)
    return metin.replace(" ", "_")

# --- ARAYÜZ ---
st.set_page_config(page_title="Alpinetech Teklif Hazırlama", layout="wide")
st.title("🏔️ Alpinetech")

# --- HAFIZA ---
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
        if secilen_musteri != "-- Yeni Müşteri Gir --":
            def_ad, def_tel, def_mail = secilen_musteri, st.session_state.musteriler[secilen_musteri].get("tel", ""), st.session_state.musteriler[secilen_musteri].get("mail", "")
        else:
            def_ad, def_tel, def_mail = "", "", ""
        m_ad = st.text_input("Müşteri Firma/Kişi", value=def_ad)
        m_tel = st.text_input("Müşteri Tel", value=def_tel)
        m_mail = st.text_input("Müşteri E-Posta", value=def_mail)

    with c3:
        st.markdown("**🧑‍💻 Teklifi Veren Bilgileri**")
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. KATEGORİ EKLEME ---
st.subheader("📋 İş Kalemleri")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1:
        kat_adi = st.text_input("Kategori Adı")
        kat_aciklama = st.text_area("Maddeler")
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        ekle_btn = st.form_submit_button("➕ Kategori Ekle")
        
    if ekle_btn and kat_adi:
        st.session_state.kategoriler.append({
            "baslik": kat_adi, "aciklama": kat_aciklama, "adet": kat_adet,
            "fiyat": kat_fiyat, "toplam": kat_adet * kat_fiyat
        })

for i, k in enumerate(st.session_state.kategoriler):
    c_disp1, c_disp2 = st.columns([9, 1])
    with c_disp1:
        st.markdown(f"**<span style='color:#2E74B5'>{k['baslik']}</span>**", unsafe_allow_html=True)
        st.write(f"*Adet: {k['adet']} | Toplam: {k['toplam']:,.0f} {para_birimi}*")
    with c_disp2:
        if st.button("🗑️", key=f"kat_sil_{i}"):
            st.session_state.kategoriler.pop(i); st.rerun()

st.divider()

# --- 3. GENEL ŞARTLAR ---
st.subheader("⚖️ Genel Şartlar")
# (Mevcut şartlar listeleme kodun burada çalışmaya devam eder...)

# --- 4. DOSYA OLUŞTURMA VE İNDİRME ---
st.subheader("💾 Kayıt ve İndirme Seçenekleri")
dosya_adi_input = st.text_input("Dosya Adı", value="Alpinetech_Teklif")
format_secimi = st.radio("İndirme Formatı Seçin:", ["PDF Dosyası", "Word Dosyası (.docx)"], horizontal=True)

if st.button("🚀 TEKLİFİ HAZIRLA", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Önce iş kalemi eklemelisin!")
    else:
        safe_name = dosya_adi_yap(dosya_adi_input)
        
        # --- PDF OLUŞTURMA MANTIGI ---
        if format_secimi == "PDF Dosyası":
            pdf = FPDF()
            pdf.add_page()
            font_adi = 'Arial' # Font kontrol mantığın burada devreye girer
            def p(metin): return str(metin).replace('₺', 'TL').encode('latin-1', 'ignore').decode('latin-1')
            
            if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=130, y=14, w=72)
            pdf.set_font(font_adi, 'B', 9)
            pdf.set_xy(10, 15)
            pdf.cell(0, 4.5, p("Alpinetech Muhendislik Makine"), ln=1)
            # ... (Diğer PDF hücrelerin burada devam eder)
            
            pdf_output = pdf.output(dest='S').encode('latin-1')
            st.download_button("📩 PDF'i İndir", pdf_output, file_name=f"{safe_name}.pdf")

        # --- WORD OLUŞTURMA MANTIGI ---
        else:
            doc = Document()
            
            # Header Alanı
            header_table = doc.add_table(rows=1, cols=2)
            header_table.width = Inches(6)
            
            # Sol taraf: Şirket Bilgileri
            shirket_hucre = header_table.rows[0].cells[0]
            p1 = shirket_hucre.paragraphs[0]
            p1.add_run("Alpinetech Mühendislik Makine\nSanayi ve Ticaret Limited Şirketi").bold = True
            p1.add_run("\n30 Ağustos Zafer Mah. Nilüfer / Bursa")
            
            # Sağ taraf: Logo (Varsa)
            if os.path.exists(LOGO_PATH):
                logo_hucre = header_table.rows[0].cells[1]
                logo_para = logo_hucre.paragraphs[0]
                logo_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                logo_para.add_run().add_picture(LOGO_PATH, width=Inches(1.5))

            doc.add_paragraph("\n")
            title = doc.add_paragraph()
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title.add_run(f"TEKLİF: {t_baslik1}\n{t_baslik2}").bold = True
            
            # Müşteri Bilgileri Tablosu
            doc.add_paragraph(f"Tarih: {t_tarih}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            doc.add_paragraph(f"Müşteri: {m_ad}\nTel: {m_tel}")
            
            doc.add_paragraph("-" * 50)
            
            # İş Kalemleri
            ara_toplam = 0
            for k in st.session_state.kategoriler:
                p_item = doc.add_paragraph()
                p_item.add_run(k['baslik']).bold = True
                p_item.add_run(f"\n{k['aciklama']}")
                p_item.add_run(f"\nToplam: {k['toplam']:,.0f} {para_birimi}").italic = True
                ara_toplam += k['toplam']
            
            doc.add_paragraph("-" * 50)
            sonuc = doc.add_paragraph()
            genel_toplam = ara_toplam * 1.2 if kdv_ekle else ara_toplam
            sonuc.add_run(f"GENEL TOPLAM: {genel_toplam:,.0f} {para_birimi}").bold = True
            sonuc.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # Şartlar
            doc.add_page_break()
            doc.add_heading('Genel Şartlar', level=2)
            for s in st.session_state.sartlar:
                doc.add_paragraph(f"• {s}", style='List Bullet')

            # Hafızada oluştur ve indir
            bio = io.BytesIO()
            doc.save(bio)
            st.download_button("📩 Word Dosyasını İndir", bio.getvalue(), file_name=f"{safe_name}.docx")
