import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- TTA IDENTITY & BRANDING ---
TTA_EMAIL = "salesindia@ttagroups.net"
TTA_PHONE = "+91 90282 27102"
TTA_WEB = "ttagroups.net"
TTA_NAVY = (13, 43, 78)   
TTA_GOLD = (201, 168, 76) 

def clean_text(text):
    """Removes all special characters that crash standard PDF fonts."""
    if not text: return ""
    # Map high-unicode to standard keyboard characters
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'", 
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u2023': '*', 
        '\u2219': '*', '\u2605': '*', '\u2728': '*'
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    # Strip any emojis or remaining non-latin characters
    return text.encode('ascii', 'ignore').decode('ascii')

class TTA_PDF(FPDF):
    def header(self):
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 15)
        self.set_xy(10, 10)
        self.cell(0, 10, 'TTA GROUP | TRAVEL PROPOSAL', 0, 1, 'L')
        self.set_font('Arial', '', 9)
        self.set_text_color(*TTA_GOLD)
        self.set_x(10)
        self.cell(0, 5, 'Expert Destination Management Services', 0, 1, 'L')
        self.ln(20)

    def footer(self):
        self.set_y(-20)
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 277, 210, 20, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        self.cell(0, 10, f"Email: {TTA_EMAIL}  |  Web: {TTA_WEB}  |  Contact: {TTA_PHONE}", 0, 0, 'C')

# --- UI SETUP ---
st.set_page_config(page_title="TTA Itinerary Architect", layout="wide")
st.title("✈️ TTA Group | Itinerary Architect")

# --- AUTHENTICATION ---
# Using the most standard way to connect
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key missing! Add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Logistics")
    dest = st.text_input("Destination")
    pax = st.text_input("Group Size")
    cost = st.text_input("Cost (USD)")
    hotel = st.text_input("Accommodation")
with col2:
    st.subheader("Itinerary Notes")
    raw_notes = st.text_area("Paste notes here...", height=200)

if st.button("Generate Final PDF"):
    if dest and raw_notes:
        with st.spinner("AI is formatting..."):
            try:
                # Use the stable flash model
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Create a professional day-by-day travel itinerary for {dest} based on: {raw_notes}. Mention TTA Group."
                
                response = model.generate_content(prompt)
                itinerary_text = response.text
                
                # PDF Assembly
                pdf = TTA_PDF()
                pdf.set_auto_page_break(auto=True, margin=25)
                pdf.add_page()
                
                # Summary Box
                pdf.set_fill_color(245, 245, 245)
                pdf.rect(10, 45, 190, 30, 'F')
                pdf.set_xy(15, 48)
                pdf.set_font('Arial', 'B', 11)
                pdf.set_text_color(*TTA_NAVY)
                pdf.cell(0, 7, clean_text(f"DESTINATION: {dest.upper()}"), 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.set_text_color(50, 50, 50)
                pdf.cell(0, 6, clean_text(f"Pax: {pax} | Hotel: {hotel}"), 0, 1)
                pdf.cell(0, 6, clean_text(f"Cost: USD {cost} | ROE: Xe + 1.2 INR"), 0, 1)
                
                pdf.ln(15)
                pdf.set_font('Arial', '', 10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, clean_text(itinerary_text))
                
                # Output
                pdf_bytes = pdf.output()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="TTA_{dest}.pdf" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#0D2B4E; color:white; border-radius:8px; cursor:pointer; font-weight:bold;">📥 DOWNLOAD PROPOSAL</button></a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("TTA Proposal Generated Successfully!")
                
            except Exception as e:
                st.error(f"Error: {e}")
