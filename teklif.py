import streamlit as st
from fpdf import FPDF
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import os
import io
from PIL import Image
from datetime import date

# --- AYARLAR VE KLASÖRLER ---
SAVE_DIR = "TEKLİFLER"
TEMP_DIR = "GECICI_RESIMLER"
LOGO_PATH = "logo.png"

for k in [SAVE_DIR, TEMP_DIR]:
    if not os.path.exists(k): os.makedirs(k)

def dosya_adi_yap(metin):
    replacements = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C'}
    for k, v in replacements.items(): metin = metin.replace(k, v)
    return "".join(c for c in metin if c.isalnum() or c in (" ", "_")).replace(" ", "_")

# --- ARAYÜZ ---
st.set_page_config(page_title="Alpinetech", layout="wide")
st.title("🏔️ Alpinetech Teklif")

if 'kategoriler' not in st.session_state: st.session_state.kategoriler = []
if 'sartlar' not in st.session_state:
    st.session_state.sartlar = [
        "Ulaşım ve konaklama giderleri teklif bedeline dâhildir.",
        "İş bu teklif ve şartlar, verildiği tarihten itibaren 15 (on beş) takvim günü boyunca geçerlidir.",
        "Montaj için gerekli saha düzenlemeleri müşteriye aittir."
    ]

# --- 1. ÜST BİLGİLER ---
with st.expander("📄 Teklif ve Müşteri Ayarları", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        t_baslik1 = st.text_input("Teklif Başlığı", "40 Metre Yürüyen Bant Fiyat Teklifi")
        t_tarih = st.text_input("Tarih", date.today().strftime("%d.%m.%Y"))
        para_birimi = st.selectbox("Para Birimi", ["EUR", "TL", "USD"])
    with c2:
        m_ad = st.text_input("Müşteri", "Necati Bey'in Dikkatine")
        kdv_ekle = st.checkbox("KDV Hesapla (%20)", value=True)
    with c3:
        v_ad = st.text_input("Teklifi Veren", "Kürşad Nuri Örme")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. İŞ KALEMLERİ VE GÖRSELLER ---
st.subheader("📋 İş Kalemleri ve Görseller")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([2, 1])
    with col_k1:
        kat_adi = st.text_input("İş/Ürün Adı")
        kat_aciklama = st.text_area("Teknik Özellikler (Maddeler halinde)")
        yuklenenler = st.file_uploader("Ürün Görselleri (Yan yana dizilecek)", type=['jpg','png','jpeg'], accept_multiple_files=True)
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        ekle_btn = st.form_submit_button("➕ Listeye Ekle")
        
    if ekle_btn and kat_adi:
        resim_listesi = []
        if yuklenenler:
            for idx, dosya in enumerate(yuklenenler):
                yol = os.path.join(TEMP_DIR, f"img_{len(st.session_state.kategoriler)}_{idx}.jpg")
                img = Image.open(dosya).convert("RGB")
                img.save(yol, "JPEG")
                resim_listesi.append(yol)
        
        st.session_state.kategoriler.append({
            "baslik": kat_adi, "aciklama": kat_aciklama, "adet": kat_adet,
            "fiyat": kat_fiyat, "toplam": kat_adet * kat_fiyat, "resimler": resim_listesi
        })

# Önizleme ve Silme
for i, k in enumerate(st.session_state.kategoriler):
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{k['baslik']}** - {k['toplam']:,.0f} {para_birimi}")
        if col2.button("Sil", key=f"del_{i}"):
            st.session_state.kategoriler.pop(i); st.rerun()

st.divider()

# --- 3. FORMAT SEÇİMİ VE OLUŞTURMA ---
format_secimi = st.radio("Dosya Formatı:", ["PDF", "Word (.docx)"], horizontal=True)

if st.button("🚀 TEKLİFİ OLUŞTUR VE İNDİR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Lütfen önce bir iş kalemi ekleyin!")
    else:
        safe_name = dosya_adi_yap(t_baslik1)
        
        if format_secimi == "PDF":
            pdf = FPDF()
            pdf.add_page()
            def p(metin): return str(metin).encode('latin-1', 'ignore').decode('latin-1').replace('₺', 'TL')
            
            # --- Header (Logo ve Bilgiler) ---
            if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=135, y=10, w=65)
            pdf.set_font("Arial", 'B', 10); pdf.set_xy(10, 10)
            pdf.cell(0, 5, p("Alpinetech Muhendislik Makine"), ln=1)
            pdf.set_font("Arial", '', 9); pdf.cell(0, 5, p("Nilufer / Bursa"), ln=1)
            pdf.ln(15)
            
            pdf.set_font("Arial", 'B', 15); pdf.cell(0, 10, p(f"TEKLIF: {t_baslik1}"), ln=1)
            pdf.set_font("Arial", '', 10); pdf.cell(0, 5, p(f"Tarih: {t_tarih}"), ln=1, align='R')
            pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)

            ara_toplam = 0
            for k in st.session_state.kategoriler:
                # Başlık (Mavi)
                pdf.set_text_color(46, 116, 181); pdf.set_font("Arial", 'B', 13)
                pdf.cell(0, 10, p(k['baslik']), ln=1)
                
                # Açıklama
                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 5, p(k['aciklama']))
                
                # Resimler (Örnekteki gibi yan yana)
                if k['resimler']:
                    pdf.ln(5)
                    img_x = 10
                    img_y = pdf.get_y()
                    for r in k['resimler'][:2]: # Yan yana 2 resim
                        pdf.image(r, x=img_x, y=img_y, w=85)
                        img_x += 90
                    pdf.set_y(img_y + 65) # Resimlerin altına geç

                pdf.ln(5); pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 8, p(f"Fiyat: {k['toplam']:,.0f} {para_birimi}"), border=1, align='R', ln=1)
                ara_toplam += k['toplam']

            # Alt Toplam ve Şartlar
            pdf.add_page() # Özet ve Şartlar 2. sayfaya
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, p("Genel Sartlar"), ln=1)
            for s in st.session_state.sartlar: pdf.multi_cell(0, 6, p(f"- {s}"))
            
            st.download_button("📩 PDF İndir", pdf.output(dest='S').encode('latin-1'), file_name=f"{safe_name}.pdf")

        else: # WORD OLUŞTURMA
            doc = Document()
            doc.add_heading(f"TEKLİF: {t_baslik1}", 0)
            for k in st.session_state.kategoriler:
                p = doc.add_paragraph()
                run = p.add_run(k['baslik'])
                run.bold = True; run.font.color.rgb = RGBColor(46, 116, 181); run.font.size = Pt(14)
                doc.add_paragraph(k['aciklama'])
                if k['resimler']:
                    table = doc.add_table(rows=1, cols=len(k['resimler'][:2]))
                    for idx, r in enumerate(k['resimler'][:2]):
                        table.cell(0, idx).paragraphs[0].add_run().add_picture(r, width=Inches(2.5))
            
            bio = io.BytesIO()
            doc.save(bio)
            st.download_button("📩 Word İndir", bio.getvalue(), file_name=f"{safe_name}.docx")
