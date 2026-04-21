import subprocess
import sys
import os

# --- STAGE 1: AUTO-INSTALL ---
def install_dependencies():
    # We are switching to fpdf2 for better character support
    packages = ["google-generativeai", "fpdf2", "streamlit"]
    for package in packages:
        try:
            name = package.replace("-", "_")
            if name == "fpdf2": name = "fpdf"
            __import__(name)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- STAGE 2: CONFIG ---
TTA_EMAIL = "salesindia@ttagroups.net"
TTA_PHONE = "+91 90282 27102"
TTA_WEB = "ttagroups.net"
TTA_NAVY = (13, 43, 78)   
TTA_GOLD = (201, 168, 76) 

def safe_encode(text):
    """Forcefully cleans text to prevent PDF crashes."""
    if not text:
        return ""
    # Map common high-unicode characters to safe equivalents
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", 
        '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2022': '*', '\u2023': '*', '\u2219': '*'
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    # Encode to latin-1 and drop any remaining 'unprintable' characters
    return text.encode('latin-1', 'ignore').decode('latin-1')

# --- STAGE 3: PDF ENGINE ---
class TTA_PDF(FPDF):
    def header(self):
        self.set_fill_color(*TTA_NAVY)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 15)
        self.set_xy(10, 10)
        self.cell(0, 10, 'TTA GROUP | PREMIUM TRAVEL PROPOSAL', 0, 1, 'L')
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

# --- STAGE 4: APP INTERFACE ---
st.set_page_config(page_title="TTA Itinerary Architect", layout="wide")
st.title("✈️ TTA Group | Itinerary Architect")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key missing in Secrets!")

col1, col2 = st.columns([1, 1])
with col1:
    dest = st.text_input("Destination")
    pax = st.text_input("Group Size")
    cost = st.text_input("Cost (USD)")
    hotel = st.text_input("Accommodation")
with col2:
    raw_notes = st.text_area("Paste notes here...", height=200)

if st.button("Generate & Download PDF"):
    if dest and raw_notes:
        with st.spinner("AI is polishing your itinerary..."):
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Provide a day-by-day itinerary for {dest} based on these notes: {raw_notes}. Be professional."
            
            response = model.generate_content(prompt)
            final_text = response.text
            
            pdf = TTA_PDF()
            pdf.set_auto_page_break(auto=True, margin=25)
            pdf.add_page()
            
            # Summary Box
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, 45, 190, 30, 'F')
            pdf.set_xy(15, 48)
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(*TTA_NAVY)
            pdf.cell(0, 7, safe_encode(f"DESTINATION: {dest.upper()}"), 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 6, safe_encode(f"Pax: {pax} | Hotel: {hotel}"), 0, 1)
            pdf.cell(0, 6, safe_encode(f"Cost: USD {cost} | ROE: Xe + 1.2 INR"), 0, 1)
            
            pdf.ln(15)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)
            
            # Content
            pdf.multi_cell(0, 6, safe_encode(final_text))
            
            # Final download
            pdf_output = pdf.output()
            # FPDF2 returns bytes by default
            b64 = base64.b64encode(pdf_output).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="TTA_{dest}.pdf" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#0D2B4E; color:white; border-radius:8px; cursor:pointer;">📥 DOWNLOAD FINAL PDF</button></a>'
            st.markdown(href, unsafe_allow_html=True)
