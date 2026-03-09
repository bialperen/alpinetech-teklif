import streamlit as st
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
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
if 'kategoriler' not in st.session_state: st.session_state.kategoriler = []
if 'sartlar' not in st.session_state:
    st.session_state.sartlar = [
        "Ulaşım ve konaklama giderleri teklif bedeline dâhildir.",
        "Fiyatlarımıza KDV (%20) dâhil değildir.",
        "Ödeme Koşulları peşin.",
        "İş bu teklif ve şartlar, verildiği tarihten itibaren 15 (on beş) takvim günü boyunca geçerlidir."
    ]

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
        kdv_oran = st.number_input("KDV Oranı (%)", value=20)
    with c2:
        st.markdown("**🏢 Müşteri Bilgileri**")
        m_ad = st.text_input("Müşteri Firma/Kişi", "")
        m_tel = st.text_input("Müşteri Tel", "")
        m_mail = st.text_input("Müşteri E-Posta", "")
    with c3:
        st.markdown("**🧑‍💻 Teklifi Veren**")
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. İŞ KALEMLERİ ---
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

# Önizleme Listesi (Tasarımın aynısı)
for i, k in enumerate(st.session_state.kategoriler):
    c_disp1, c_disp2 = st.columns([9, 1])
    with c_disp1:
        st.markdown(f"**<span style='color:#2E74B5'>{k['baslik']}</span>**", unsafe_allow_html=True)
        st.text(k['aciklama'])
        st.write(f"*Adet: {k['adet']} | Birim Fiyat: {k['fiyat']:,.0f} {para_birimi} | **Toplam: {k['toplam']:,.0f} {para_birimi}***")
    with c_disp2:
        if st.button("🗑️", key=f"kat_sil_{i}"):
            st.session_state.kategoriler.pop(i); st.rerun()
    st.write("---")

# --- 3. GENEL ŞARTLAR ---
st.subheader("⚖️ Genel Şartlar")
# (Şartlar listeleme kodun burada...)

# --- 4. KAYIT VE İNDİRME ---
st.subheader("💾 Kayıt Ayarları")
dosya_adi_input = st.text_input("Dosya Adı", value="Yeni_Teklif_Dosyasi")
format_secimi = st.radio("İndirme Formatı:", ["PDF", "Word (.docx)"], horizontal=True)

if st.button("🚀 TEKLİFİ OLUŞTUR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("En az bir kategori ekle!")
    else:
        safe_name = dosya_adi_yap(dosya_adi_input)
        
        # --- PDF OLUŞTURMA (Orijinal Tasarım) ---
        if format_secimi == "PDF":
            pdf = FPDF()
            pdf.add_page()
            def p(metin): return str(metin).replace('₺', 'TL').encode('latin-1', 'ignore').decode('latin-1')
            
            if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=130, y=14, w=72)
            pdf.set_font("Arial", 'B', 9); pdf.set_xy(10, 15)
            pdf.cell(0, 4.5, p("Alpinetech Muhendislik Makine"), ln=1)
            pdf.cell(0, 4.5, p("Sanayi ve Ticaret Limited Sirketi"), ln=1)
            pdf.ln(12)
            pdf.set_font("Arial", 'B', 16); pdf.cell(0, 8, p(f"TEKLIF: {t_baslik1}"), ln=1)
            pdf.set_font("Arial", 'B', 14); pdf.cell(100, 8, p(t_baslik2), ln=0)
            pdf.set_font("Arial", '', 11); pdf.cell(90, 8, p(t_tarih), ln=1, align='R')
            pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2); pdf.ln(10)

            ara_toplam = 0
            for k in st.session_state.kategoriler:
                pdf.set_text_color(46, 116, 181); pdf.set_font("Arial", '', 14); pdf.cell(0, 8, p(k['baslik']), ln=1)
                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 9); pdf.multi_cell(0, 5, p(k['aciklama']))
                pdf.cell(0, 6, p(f"Fiyat : {k['toplam']:,.0f} {para_birimi}"), border=1, align='R', ln=1); pdf.ln(5)
                ara_toplam += k['toplam']

            # Alt Toplam Tablosu (Sildiğim yer burasıydı, geri geldi!)
            pdf.ln(5); pdf.set_text_color(46, 116, 181); pdf.set_font("Arial", '', 12)
            pdf.cell(90, 6, "Genel Toplam", ln=0, align='R'); pdf.cell(20, 6, "Adet", ln=0, align='C'); pdf.cell(35, 6, "Fiyat", ln=0, align='C'); pdf.cell(45, 6, "Toplam", ln=1, align='C')
            pdf.line(50, pdf.get_y(), 200, pdf.get_y()); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 9)
            for k in st.session_state.kategoriler:
                pdf.cell(90, 5, p(k['baslik']), ln=0, align='R'); pdf.cell(20, 5, str(k['adet']), ln=0, align='C'); pdf.cell(35, 5, p(f"{k['fiyat']:,.0f}"), ln=0, align='C'); pdf.cell(45, 5, p(f"{k['toplam']:,.0f}"), ln=1, align='C')
            
            kdv_tutari = ara_toplam * (kdv_oran/100) if kdv_ekle else 0
            pdf.ln(2); pdf.cell(145, 5, "TOPLAM", ln=0, align='R'); pdf.cell(45, 5, p(f"{ara_toplam:,.0f} {para_birimi}"), ln=1, align='C')
            if kdv_ekle:
                pdf.cell(145, 5, p(f"KDV(%{kdv_oran})"), ln=0, align='R'); pdf.cell(45, 5, p(f"{kdv_tutari:,.0f} {para_birimi}"), ln=1, align='C')
            pdf.cell(145, 5, "GENEL TOPLAM", ln=0, align='R'); pdf.cell(45, 5, p(f"{ara_toplam+kdv_tutari:,.0f} {para_birimi}"), ln=1, align='C')

            st.download_button("📩 PDF İndir", pdf.output(dest='S').encode('latin-1'), file_name=f"{safe_name}.pdf")

        # --- WORD OLUŞTURMA (Tasarımı PDF'e Benzetmeye Çalıştım) ---
        else:
            doc = Document()
            title = doc.add_heading(f'TEKLİF: {t_baslik1}', 0)
            doc.add_paragraph(f"{t_baslik2}").bold = True
            doc.add_paragraph(f"Tarih: {t_tarih}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            ara_toplam = 0
            for k in st.session_state.kategoriler:
                p = doc.add_paragraph()
                run = p.add_run(k['baslik'])
                run.font.color.rgb = RGBColor(46, 116, 181)
                run.font.size = Pt(14)
                doc.add_paragraph(k['aciklama'])
                doc.add_paragraph(f"Tutar: {k['toplam']:,.0f} {para_birimi}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
                ara_toplam += k['toplam']

            doc.add_page_break()
            doc.add_heading('Genel Toplam', level=1)
            table = doc.add_table(rows=1, cols=4)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'İş Kalemi'; hdr_cells[1].text = 'Adet'; hdr_cells[2].text = 'Birim Fiyat'; hdr_cells[3].text = 'Toplam'
            
            for k in st.session_state.kategoriler:
                row_cells = table.add_row().cells
                row_cells[0].text = k['baslik']; row_cells[1].text = str(k['adet']); row_cells[2].text = f"{k['fiyat']:,.0f}"; row_cells[3].text = f"{k['toplam']:,.0f}"
            
            bio = io.BytesIO()
            doc.save(bio)
            st.download_button("📩 Word İndir", bio.getvalue(), file_name=f"{safe_name}.docx")
