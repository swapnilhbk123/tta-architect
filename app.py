import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- STAGE 1: TTA BRANDING & CONFIG ---
TTA_EMAIL = "salesindia@ttagroups.net"
TTA_PHONE = "+91 90282 27102"
TTA_WEB = "ttagroups.net"
TTA_NAVY = (13, 43, 78)   
TTA_GOLD = (201, 168, 76) 

def safe_encode(text):
    """
    Cleans text to prevent PDF crashes by replacing 
    Unicode symbols with safe ASCII equivalents.
    """
    if not text:
        return ""
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", 
        '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2022': '*', '\u2023': '*', '\u2219': '*',
        '\u20ac': 'EUR ', '\u00a3': 'GBP '
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    # Final safety net: drop any character fpdf2 can't render in Latin-1
    return text.encode('latin-1', 'ignore').decode('latin-1')

# --- STAGE 2: PDF ENGINE ---
class TTA_PDF(FPDF):
    def header(self):
        # Professional Navy Banner
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 0, 210, 35, 'F')
        
        # Title
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 15)
        self.set_xy(10, 10)
        self.cell(0, 10, 'TTA GROUP | PREMIUM TRAVEL PROPOSAL', 0, 1, 'L')
        
        # Subtitle
        self.set_font('Arial', '', 9)
        self.set_text_color(*TTA_GOLD)
        self.set_x(10)
        self.cell(0, 5, 'Expert Destination Management Services', 0, 1, 'L')
        self.ln(20)

    def footer(self):
        # Professional Footer with Hard-coded Contact Info
        self.set_y(-20)
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 277, 210, 20, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        contact_text = f"Email: {TTA_EMAIL}  |  Web: {TTA_WEB}  |  Contact: {TTA_PHONE}"
        self.cell(0, 10, contact_text, 0, 0, 'C')

# --- STAGE 3: STREAMLIT INTERFACE ---
st.set_page_config(page_title="TTA Itinerary Architect", layout="wide", page_icon="✈️")

# Custom CSS for the UI
st.markdown(f"""
    <style>
    .stButton>button {{ background-color: #0D2B4E; color: white; border-radius: 8px; border: 1px solid #C9A84C; }}
    h1 {{ color: #0D2B4E; border-bottom: 2px solid #C9A84C; padding-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

st.title("✈️ TTA Group | Itinerary Architect")

# Initialize Gemini with Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key missing! Please add GEMINI_API_KEY to Streamlit Secrets.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Logistics")
    dest = st.text_input("Destination", placeholder="e.g. Switzerland & France")
    pax = st.text_input("Group Size", placeholder="e.g. 25 Adults")
    cost = st.text_input("Cost per Pax (USD)", placeholder="e.g. 1250")
    hotel = st.text_input("Hotel Category/Name", placeholder="e.g. 4* Premium Hotels")

with col2:
    st.subheader("📝 Source Content")
    raw_notes = st.text_area("Paste rough notes or draft itinerary here...", height=250)

if st.button("✨ Generate & Download Professional PDF"):
    if not (dest and raw_notes):
        st.warning("Please enter a Destination and some Itinerary notes first.")
    else:
        with st.spinner("AI is transforming your notes into a luxury proposal..."):
            try:
                # FIXED MODEL NAME
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = (
                    f"Create a high-end, day-by-day travel itinerary for {dest}. "
                    f"Use professional, engaging language suitable for a premium agency like TTA Group. "
                    f"Use bullet points for activities and bold headings for days. "
                    f"Source Notes: {raw_notes}"
                )
                
                response = model.generate_content(prompt)
                final_text = response.text
                
                # PREVIEW
                st.info("### AI Preview")
                st.markdown(final_text)
                
                # CREATE PDF
                pdf = TTA_PDF()
                pdf.set_auto_page_break(auto=True, margin=25)
                pdf.add_page()
                
                # Overview Summary Box
                pdf.set_fill_color(245, 245, 245)
                pdf.rect(10, 45, 190, 32, 'F')
                pdf.set_xy(15, 48)
                pdf.set_font('Arial', 'B', 11)
                pdf.set_text_color(*TTA_NAVY)
                pdf.cell(0, 7, safe_encode(f"DESTINATION: {dest.upper()}"), 0, 1)
                
                pdf.set_font('Arial', '', 10)
                pdf.set_text_color(50, 50, 50)
                pdf.cell(0, 6, safe_encode(f"Group Size: {pax}  |  Stay: {hotel}"), 0, 1)
                
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, safe_encode(f"Price: USD {cost} Per Adult  |  ROE: Xe + 1.2 INR"), 0, 1)
                
                pdf.ln(15)
                pdf.set_font('Arial', '', 10)
                pdf.set_text_color(0, 0, 0)
                
                # Main Content
                pdf.multi_cell(0, 6, safe_encode(final_text))
                
                # Generate Download Link
                pdf_output = pdf.output()
                b64 = base64.b64encode(pdf_output).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="TTA_Proposal_{dest}.pdf" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#C9A84C; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">📥 DOWNLOAD FINAL PDF PROPOSAL</button></a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Proposal Ready for Download!")
                
            except Exception as e:
                st.error(f"An error occurred during generation: {str(e)}")

# Sidebar Info
st.sidebar.image("https://ttagroups.net/wp-content/uploads/2023/04/TTA-Logo.png", width=150)
st.sidebar.write("---")
st.sidebar.markdown("**Settings Applied:**")
st.sidebar.write("✅ ROE: Xe + 1.2 INR")
st.sidebar.write("✅ Model: Gemini 1.5 Flash")
st.sidebar.write("✅ Format: TTA Premium Branding")
