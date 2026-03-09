import streamlit as st
from fpdf import FPDF
from datetime import date
import os
from PIL import Image
import io

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
        def_tel = st.session_state.musteriler[secilen_musteri].get("tel", "") if def_ad else ""
        def_mail = st.session_state.musteriler[secilen_musteri].get("mail", "") if def_ad else ""
        m_ad = st.text_input("Müşteri Firma/Kişi", value=def_ad)
        m_tel = st.text_input("Müşteri Tel", value=def_tel)
        m_mail = st.text_input("Müşteri E-Posta", value=def_mail)

    with c3:
        st.markdown("**🧑‍💻 Teklifi Veren**")
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

# --- 2. KATEGORİ VE RESİM EKLEME ---
st.subheader("📋 İş Kalemleri")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1:
        kat_adi = st.text_input("Kategori Adı")
        kat_aciklama = st.text_area("Maddeler")
        yuklenenler = st.file_uploader("Ürün Görselleri", type=['jpg','png','jpeg'], accept_multiple_files=True)
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        ekle_btn = st.form_submit_button("➕ Kategori Ekle")
        
    if ekle_btn and kat_adi:
        resim_yollari = []
        if yuklenenler:
            for i, dosya in enumerate(yuklenenler):
                try:
                    # Resmi doğrula ve güvenli kaydet
                    img = Image.open(dosya)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    yol = os.path.join(TEMP_DIR, f"temp_{len(st.session_state.kategoriler)}_{i}.jpg")
                    img.save(yol, "JPEG")
                    resim_yollari.append(yol)
                except:
                    st.error(f"Resim işlenemedi: {dosya.name}")
        
        st.session_state.kategoriler.append({
            "baslik": kat_adi, "aciklama": kat_aciklama, "adet": kat_adet,
            "fiyat": kat_fiyat, "toplam": kat_adet * kat_fiyat, "resimler": resim_yollari
        })

# Önizleme
if st.session_state.kategoriler:
    for i, k in enumerate(st.session_state.kategoriler):
        c_disp1, c_disp2 = st.columns([9, 1])
        with c_disp1:
            st.markdown(f"**<span style='color:#2E74B5'>{k['baslik']}</span>**", unsafe_allow_html=True)
            if k['resimler']:
                res_cols = st.columns(min(len(k['resimler']), 4))
                for idx, r in enumerate(k['resimler']):
                    res_cols[idx % 4].image(r, width=120)
            st.text(k['aciklama'])
            st.write(f"*Adet: {k['adet']} | Toplam: {k['toplam']:,.0f} {para_birimi}*")
        with c_disp2:
            if st.button("🗑️", key=f"kat_sil_{i}"):
                st.session_state.kategoriler.pop(i); st.rerun()
        st.write("---")

# --- 3. ŞARTLAR ---
st.subheader("⚖️ Genel Şartlar")
# (Tasarımın aynısı korunmuştur...)
for i, sart in enumerate(st.session_state.sartlar):
    sc1, sc2 = st.columns([9, 1])
    sc1.write(f"- {sart}")
    if sc2.button("🗑️", key=f"sart_sil_{i}"):
        st.session_state.sartlar.pop(i); st.rerun()

st.divider()

# --- 4. PDF OLUŞTURMA ---
dosya_adi = st.text_input("Kaydedilecek Dosya Adı", value="Yeni_Teklif_Dosyasi")

if st.button("🚀 TEKLİFİ OLUŞTUR VE İNDİR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Lütfen kategori ekleyin!")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        def p(metin):
            rep = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C', 'â':'a', 'Â':'A', '₺':'TL'}
            m = str(metin)
            for k, v in rep.items(): m = m.replace(k, v)
            return m.encode('latin-1', 'ignore').decode('latin-1')

        # Header ve Logo
        if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=130, y=14, w=72)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_xy(10, 15)
        pdf.cell(0, 4.5, p("Alpinetech Muhendislik Makine"), ln=1)
        pdf.cell(0, 4.5, p("Sanayi ve Ticaret Limited Sirketi"), ln=1)
        pdf.ln(12)
        pdf.set_font("Arial", 'B', 16); pdf.cell(0, 8, p(f"TEKLIF: {t_baslik1}"), ln=1)
        pdf.set_font("Arial", 'B', 14); pdf.cell(100, 8, p(t_baslik2), ln=0)
        pdf.set_font("Arial", '', 11); pdf.cell(90, 8, p(t_tarih), ln=1, align='R')
        pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2); pdf.ln(10)

        # Kalemler ve Resimler
        ara_toplam = 0
        for k in st.session_state.kategoriler:
            if pdf.get_y() > 210: pdf.add_page()
            pdf.set_text_color(46, 116, 181); pdf.set_font("Arial", '', 14); pdf.cell(0, 8, p(k['baslik']), ln=1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.set_text_color(0, 0, 0); pdf.ln(2)
            
            # Resim Gridi
            if k['resimler']:
                y_resim = pdf.get_y()
                for idx, r in enumerate(k['resimler']):
                    if os.path.exists(r): # Dosya var mı kontrolü
                        pdf.image(r, x=10 + (idx%4)*48, y=y_resim + (idx//4)*38, w=45)
                    if idx == len(k['resimler'])-1:
                        pdf.set_y(y_resim + (idx//4 + 1)*42)
            
            pdf.set_font("Arial", 'B', 9); pdf.multi_cell(0, 5, p(k['aciklama']))
            pdf.cell(0, 6, p(f"Fiyat : {k['toplam']:,.0f} {para_birimi}"), border=1, align='R', ln=1); pdf.ln(5)
            ara_toplam += k['toplam']

        # Alt Toplam Tablosu
        pdf.ln(5); pdf.set_font("Arial", 'B', 10)
        g_str = f"{ara_toplam * 1.2 if kdv_ekle else ara_toplam:,.0f}"
        pdf.cell(145, 7, "GENEL TOPLAM", ln=0, align='R'); pdf.cell(45, 7, p(f"{g_str} {para_birimi}"), ln=1, align='C', border=1)

        safe_name = dosya_adi_yap(dosya_adi)+".pdf"
        out_name = os.path.join(SAVE_DIR, safe_name)
        pdf.output(out_name)
        st.success("✅ Teklif hazır!")
        st.download_button("📩 İndir", open(out_name, "rb"), file_name=safe_name)
