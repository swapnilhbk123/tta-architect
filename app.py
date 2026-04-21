import subprocess
import sys
import os

# --- STAGE 1: AUTO-INSTALL MISSING PACKAGES ---
def install_dependencies():
    packages = ["google-generativeai", "fpdf", "streamlit"]
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- STAGE 2: BRANDING & CONTACT CONFIG ---
TTA_EMAIL = "salesindia@ttagroups.net"
TTA_PHONE = "+91 90282 27102"
TTA_WEB = "ttagroups.net"
TTA_NAVY = (13, 43, 78)   
TTA_GOLD = (201, 168, 76) 

# --- STAGE 3: PDF GENERATION ENGINE ---
class TTA_PDF(FPDF):
    def header(self):
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'TTA GROUP | PREMIUM PROPOSAL', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(*TTA_GOLD)
        self.cell(0, 5, 'Destination Management Company', 0, 1, 'L')
        self.ln(20)

    def footer(self):
        self.set_y(-25)
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 272, 210, 25, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"Email: {TTA_EMAIL} | Phone: {TTA_PHONE} | Web: {TTA_WEB}", 0, 0, 'C')

# --- STAGE 4: STREAMLIT INTERFACE ---
st.set_page_config(page_title="TTA Itinerary Automator", layout="wide")

# Apply custom CSS for the TTA look in the app
st.markdown(f"""
    <style>
    .stButton>button {{ background-color: #0D2B4E; color: white; border: 1px solid #C9A84C; }}
    h1 {{ color: #0D2B4E; border-bottom: 2px solid #C9A84C; }}
    </style>
    """, unsafe_allow_html=True)

st.title("✈️ TTA Group | Itinerary Architect")

# Setup Gemini API using the secret key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add GEMINI_API_KEY to your Streamlit Secrets.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Trip Logistics")
    dest = st.text_input("Destination")
    pax = st.text_input("Group Size (e.g. 45 Pax)")
    cost = st.text_input("Price per Adult (USD)")
    hotel = st.text_input("Accommodation")

with col2:
    st.subheader("📝 Itinerary Data")
    raw_notes = st.text_area("Paste rough itinerary/notes here...", height=250)

if st.button("Generate Professional Proposal"):
    if not dest or not raw_notes:
        st.warning("Please enter a Destination and Itinerary notes.")
    else:
        with st.spinner("AI is formatting your proposal..."):
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Act as a professional travel consultant for TTA Group. Refine this itinerary for a client. Use professional language, bullet points, and highlight key attractions. Destination: {dest}. Notes: {raw_notes}"
            
            response = model.generate_content(prompt)
            beautified_text = response.text
            
            # Preview for the user
            st.info("### AI Generated Preview")
            st.write(beautified_text)
            
            # PDF Creation
            pdf = TTA_PDF()
            pdf.add_page()
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"PROPOSAL: {dest.upper()}", 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, f"Pax: {pax} | Hotel: {hotel}", 0, 1)
            pdf.cell(0, 8, f"Cost: USD {cost} | ROE: Xe + 1.2 INR", 0, 1)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 10)
            # Encoding handling for PDF
            clean_text = beautified_text.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 7, clean_text)
            
            pdf_bytes = pdf.output(dest="S").encode('latin-1')
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="TTA_Proposal_{dest}.pdf" style="text-decoration:none;"><button style="width:100%; padding:10px; background-color:#C9A84C; color:white; border:none; border-radius:5px;">📥 Download PDF</button></a>'
            st.markdown(href, unsafe_allow_html=True)
