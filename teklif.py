import streamlit as st
from fpdf import FPDF
from datetime import date
import os

# --- AYARLAR ---
SAVE_DIR = "TEKLİFLER"
LOGO_PATH = "logo.png"
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

def t(metin):
    """Bulutta PDF'in çökmemesi için Türkçe karakterleri çevirir"""
    replacements = {'ı':'i','İ':'I','ş':'s','Ş':'S','ğ':'g','Ğ':'G','ü':'u','Ü':'U','ö':'o','Ö':'O','ç':'c','Ç':'C', 'â':'a', 'Â':'A'}
    metin = str(metin)
    for k, v in replacements.items():
        metin = metin.replace(k, v)
    return metin

def dosya_adi_yap(metin):
    return t(metin).replace(" ", "_")

# --- ARAYÜZ ---
st.set_page_config(page_title="Alpinetech PRO Format", layout="wide")
st.title("🏔️ Alpinetech Orijinal Teklif Sistemi")

if 'kategoriler' not in st.session_state:
    st.session_state.kategoriler = []
    
if 'sartlar' not in st.session_state:
    st.session_state.sartlar = [
        "Ulaşım ve konaklama giderleri teklif bedeline dâhildir.",
        "Fiyatlarımıza KDV (%20) dâhil değildir.",
        "Ödeme Koşulları peşin.",
        "İş bu teklif ve şartlar, verildiği tarihten itibaren 15 (on beş) takvim günü boyunca geçerlidir."
    ]

with st.expander("📄 Teklif, İletişim ve KDV Ayarları", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**📌 Teklif Detayları**")
        t_baslik1 = st.text_input("Başlık (1. Satır)", "")
        t_baslik2 = st.text_input("Başlık (2. Satır)", "")
        t_tarih = st.text_input("Tarih", date.today().strftime("%d.%m.%Y"))
        para_birimi = st.selectbox("Para Birimi", ["EUR", "TL", "USD"])
        
        st.markdown("**💰 Vergi Ayarları**")
        k1, k2 = st.columns(2)
        with k1:
            kdv_ekle = st.checkbox("KDV Hesapla", value=False)
        with k2:
            kdv_oran = st.number_input("KDV Oranı (%)", min_value=0, value=20, step=1)

    with c2:
        st.markdown("**🏢 Müşteri Bilgileri**")
        m_ad = st.text_input("Müşteri Firma/Kişi", "")
        m_tel = st.text_input("Müşteri Tel", "")
        m_mail = st.text_input("Müşteri E-Posta", "")
    with c3:
        st.markdown("**🧑‍💻 Teklifi Veren Bilgileri**")
        v_ad = st.text_input("İsim Soyisim", "Kürşad Nuri Örme")
        v_tel = st.text_input("Telefon", "+90 541 575 21 70")
        v_mail = st.text_input("E-Posta", "info@alpinetech.com.tr")

st.divider()

st.subheader("📋 İş Kalemleri")
with st.form("kategori_ekle", clear_on_submit=True):
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1:
        kat_adi = st.text_input("Kategori Adı (Örn: Halat Hazırlanması)")
        kat_aciklama = st.text_area("Maddeler (Alt alta yazabilirsiniz)")
    with col_k2:
        kat_adet = st.number_input("Adet", min_value=1.0, value=1.0, step=1.0)
        kat_fiyat = st.number_input("Birim Fiyat", min_value=0.0)
        st.markdown("<br>", unsafe_allow_html=True)
        ekle_btn = st.form_submit_button("➕ Kategori Ekle")
        
    if ekle_btn and kat_adi:
        adet_val = int(kat_adet) if kat_adet.is_integer() else kat_adet
        st.session_state.kategoriler.append({
            "baslik": kat_adi, 
            "aciklama": kat_aciklama, 
            "adet": adet_val,
            "fiyat": kat_fiyat,
            "toplam": adet_val * kat_fiyat
        })

if st.session_state.kategoriler:
    for i, k in enumerate(st.session_state.kategoriler):
        c_disp1, c_disp2 = st.columns([9, 1])
        with c_disp1:
            st.markdown(f"**<span style='color:#2E74B5'>{k['baslik']}</span>**", unsafe_allow_html=True)
            st.text(k['aciklama'])
            st.write(f"*Adet: {k['adet']} | Birim Fiyat: {k['fiyat']:,.0f} {para_birimi} | **Toplam: {k['toplam']:,.0f} {para_birimi}***")
        with c_disp2:
            if st.button("🗑️ Sil", key=f"kat_sil_{i}"):
                st.session_state.kategoriler.pop(i)
                st.rerun()
        st.write("---")

st.subheader("⚖️ Genel Şartlar")
with st.form("sart_ekle", clear_on_submit=True):
    c_sart1, c_sart2 = st.columns([4, 1])
    yeni_sart = c_sart1.text_input("Yeni Şart Ekle (Örn: Ekstra vinç bedeli müşteriye aittir.)")
    if c_sart2.form_submit_button("➕ Şart Ekle") and yeni_sart:
        st.session_state.sartlar.append(yeni_sart)

if st.session_state.sartlar:
    for i, sart in enumerate(st.session_state.sartlar):
        sc1, sc2 = st.columns([9, 1])
        sc1.write(f"- {sart}")
        if sc2.button("🗑️ Sil", key=f"sart_sil_{i}"):
            st.session_state.sartlar.pop(i)
            st.rerun()

st.divider()

st.subheader("💾 Kayıt Ayarları")
dosya_adi = st.text_input("Kaydedilecek Dosya Adı", value="Yeni_Teklif_Dosyasi")

if st.button("🚀 TEKLİFİ OLUŞTUR VE İNDİR", type="primary"):
    if not st.session_state.kategoriler:
        st.error("Lütfen en az bir kategori ekleyin!")
    elif not dosya_adi:
        st.error("Lütfen bir dosya adı girin!")
    else:
        pdf = FPDF()
        pdf.add_page()
        
        # --- BULUT VE WİNDOWS UYUMLU FONT SİSTEMİ ---
        font_adi = 'Arial'
        bulutta_mi = True
        if os.path.exists(r'C:\Windows\Fonts\arial.ttf'):
            try:
                pdf.add_font('ArialTR', '', r'C:\Windows\Fonts\arial.ttf', uni=True)
                pdf.add_font('ArialTR', 'B', r'C:\Windows\Fonts\arialbd.ttf', uni=True)
                font_adi = 'ArialTR'
                bulutta_mi = False
            except:
                pass
                
        def p(metin):
            """Font bulunamazsa (Buluttaysa) çökmeyi önlemek için karakterleri çevirir"""
            return t(metin) if bulutta_mi else str(metin)
        
        BLUE = (46, 116, 181)
        GREEN = (112, 173, 71)
        BLACK = (0, 0, 0)
        
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=130, y=14, w=72)
            
        pdf.set_font(font_adi, 'B', 9)
        pdf.set_xy(10, 15)
        pdf.cell(0, 4.5, p("Alpinetech Mühendislik Makine"), ln=1)
        pdf.cell(0, 4.5, p("Sanayi ve Ticaret Limited Şirketi"), ln=1)
        pdf.cell(0, 4.5, p("30 Ağustos Zafer Mahallesi 520."), ln=1)
        pdf.cell(0, 4.5, p("Cadde 4C/A Nilüfer Bursa"), ln=1)
        pdf.set_text_color(*GREEN)
        pdf.cell(0, 4.5, "www.alpinetech.com.tr", ln=1)
        pdf.set_text_color(*BLACK)
        pdf.cell(0, 4.5, "info@alpinetech.com.tr", ln=1)

        pdf.ln(12)
        pdf.set_font(font_adi, 'B', 16)
        pdf.cell(0, 8, p(f"TEKLİF: {t_baslik1}"), ln=1)
        
        pdf.set_font(font_adi, 'B', 14)
        pdf.cell(100, 8, p(t_baslik2), ln=0)
        pdf.set_font(font_adi, '', 11)
        pdf.cell(90, 8, p(t_tarih), ln=1, align='R')
        
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
        pdf.ln(5)

        pdf.set_font(font_adi, 'B', 9)
        y_info = pdf.get_y()
        
        pdf.set_xy(10, y_info)
        pdf.cell(15, 5, p("Müşteri"), ln=0); pdf.set_font(font_adi, ''); pdf.cell(70, 5, p(m_ad), ln=1)
        pdf.set_font(font_adi, 'B'); pdf.cell(15, 5, "Telefon", ln=0); pdf.set_font(font_adi, ''); pdf.cell(70, 5, p(m_tel), ln=1)
        pdf.set_font(font_adi, 'B'); pdf.cell(15, 5, "E-Posta", ln=0); pdf.set_font(font_adi, ''); pdf.cell(70, 5, p(m_mail), ln=1)
        
        pdf.set_font(font_adi, 'B', 9)
        pdf.set_xy(115, y_info)
        pdf.cell(25, 5, "Teklifi veren", ln=0); pdf.set_font(font_adi, ''); pdf.cell(50, 5, p(v_ad), ln=1)
        pdf.set_xy(115, y_info+5)
        pdf.set_font(font_adi, 'B', 9); pdf.cell(25, 5, "Telefon", ln=0); pdf.set_font(font_adi, ''); pdf.cell(50, 5, p(v_tel), ln=1)
        pdf.set_xy(115, y_info+10)
        pdf.set_font(font_adi, 'B', 9); pdf.cell(25, 5, "E-posta", ln=0); pdf.set_text_color(*GREEN); pdf.cell(50, 5, p(v_mail), ln=1)
        pdf.set_text_color(*BLACK)

        pdf.ln(3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        ara_toplam = 0
        for k in st.session_state.kategoriler:
            pdf.set_text_color(*BLUE)
            pdf.set_font(font_adi, '', 14)
            pdf.cell(0, 8, p(k['baslik']), ln=1)
            
            pdf.set_draw_color(*BLUE)
            pdf.set_line_width(0.2)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.set_draw_color(*BLACK) 
            
            pdf.set_text_color(*BLACK)
            pdf.set_font(font_adi, 'B', 9)
            pdf.ln(1)
            pdf.multi_cell(0, 5, p(k['aciklama']))
            
            pdf.ln(1)
            pdf.set_font(font_adi, '', 9)
            kutu_fiyat = f"{k['toplam']:,.0f}".replace(",", ".")
            pdf.cell(0, 6, p(f"Fiyat : {kutu_fiyat} {para_birimi}"), border=1, align='R', ln=1)
            pdf.ln(5)
            ara_toplam += k['toplam']

        if kdv_ekle:
            kdv_tutari = ara_toplam * (kdv_oran / 100)
            genel_toplam = ara_toplam + kdv_tutari
        else:
            kdv_tutari = 0
            genel_toplam = ara_toplam

        pdf.ln(5)
        pdf.set_text_color(*BLUE)
        pdf.set_font(font_adi, '', 12)
        
        pdf.cell(40, 6, "", ln=0)
        pdf.cell(50, 6, "Genel Toplam", ln=0, align='R')
        pdf.cell(20, 6, "Adet", ln=0, align='C')
        pdf.cell(35, 6, "Fiyat", ln=0, align='C')
        pdf.cell(45, 6, "Toplam", ln=1, align='C')
        
        pdf.set_draw_color(*BLUE)
        pdf.line(50, pdf.get_y(), 200, pdf.get_y())
        pdf.set_draw_color(*BLACK)
        pdf.set_text_color(*BLACK)
        
        pdf.set_font(font_adi, 'B', 9)
        pdf.ln(2)
        for k in st.session_state.kategoriler:
            f_str = f"{k['fiyat']:,.0f}".replace(",", ".")
            t_str = f"{k['toplam']:,.0f}".replace(",", ".")
            
            pdf.cell(40, 5, "", ln=0) 
            pdf.cell(50, 5, p(k['baslik']), ln=0, align='R') 
            pdf.cell(20, 5, str(k['adet']), ln=0, align='C')
            pdf.cell(35, 5, f"{f_str} {para_birimi}", ln=0, align='C')
            pdf.cell(45, 5, f"{t_str} {para_birimi}", ln=1, align='C')

        pdf.ln(2)
        if kdv_ekle:
            a_str = f"{ara_toplam:,.0f}".replace(",", ".")
            pdf.cell(110, 5, "", ln=0) 
            pdf.cell(35, 5, "Toplam", ln=0, align='R')
            pdf.cell(45, 5, f"{a_str} {para_birimi}", ln=1, align='C')
            
            k_str = f"{kdv_tutari:,.0f}".replace(",", ".")
            pdf.cell(110, 5, "", ln=0)
            pdf.cell(35, 5, p(f"KDV(%{kdv_oran})"), ln=0, align='R')
            pdf.cell(45, 5, f"{k_str} {para_birimi}", ln=1, align='C')
            
            g_str = f"{genel_toplam:,.0f}".replace(",", ".")
            pdf.cell(110, 5, "", ln=0)
            pdf.cell(35, 5, "Genel Toplam", ln=0, align='R')
            pdf.cell(45, 5, f"{g_str} {para_birimi}", ln=1, align='C')
        else:
            g_str = f"{genel_toplam:,.0f}".replace(",", ".")
            pdf.cell(110, 5, "", ln=0)
            pdf.cell(35, 5, "Genel Toplam", ln=0, align='R')
            pdf.cell(45, 5, f"{g_str} {para_birimi}", ln=1, align='C')

        if st.session_state.sartlar:
            pdf.ln(10)
            pdf.set_text_color(*BLUE)
            pdf.set_font(font_adi, '', 14)
            pdf.cell(0, 8, p("Genel Şartlar"), ln=1)
            pdf.set_draw_color(*BLUE)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.set_draw_color(*BLACK)
            
            pdf.ln(2)
            pdf.set_text_color(*BLACK)
            pdf.set_font(font_adi, '', 9)
            for sart in st.session_state.sartlar:
                pdf.cell(5, 5, "-", ln=0)
                pdf.multi_cell(0, 5, p(sart))

        pdf.set_auto_page_break(False)
        pdf.set_y(-15)
        pdf.set_font(font_adi, '', 8)
        pdf.cell(0, 10, "1", 0, 0, 'R')

        safe_name = dosya_adi_yap(dosya_adi)
        if not safe_name.lower().endswith(".pdf"):
            safe_name += ".pdf"
            
        out_name = os.path.join(SAVE_DIR, safe_name)
        pdf.output(out_name)
        
        st.success(f"✅ Teklif '{safe_name}' başarıyla oluşturuldu!")
        with open(out_name, "rb") as f:
            st.download_button("📩 PDF'i İndir", f, file_name=safe_name)
