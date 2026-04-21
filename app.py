import subprocess
import sys
import os

# --- STAGE 1: SELF-HEALING INSTALLATION ---
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
TTA_NAVY = (13, 43, 78)   # Navy Blue
TTA_GOLD = (201, 168, 76) # Gold

# --- STAGE 3: PDF GENERATION ENGINE ---
class TTA_PDF(FPDF):
    def header(self):
        # Navy Header Bar
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
        # Hard-coded contact info in footer
        self.cell(0, 10, f"Email: {TTA_EMAIL} | Phone: {TTA_PHONE} | Web: {TTA_WEB}", 0, 0, 'C')

# --- STAGE 4: STREAMLIT INTERFACE ---
st.set_page_config(page_title="TTA Itinerary Automator", layout="wide")

st.title("✈️ TTA Group | AI Itinerary Architect")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Trip Details")
    dest = st.text_input("Destination")
    pax = st.text_input("Number of Pax", placeholder="e.g. 45 Adults")
    cost = st.text_input("Cost per Pax (USD)")
    hotel = st.text_input("Hotel Name")

with col2:
    st.subheader("📝 Raw Notes")
    raw_notes = st.text_area("Paste your rough itinerary here...", height=250)

if st.button("Generate Luxury Itinerary"):
    if not (dest and raw_notes):
        st.error("Please provide at least a Destination and Itinerary notes.")
    else:
        with st.spinner("AI is beautifying your itinerary..."):
            # Note: You will need to set your GEMINI_API_KEY in Streamlit Secrets
            # genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Formatting the data for the PDF
            pdf = TTA_PDF()
            pdf.add_page()
            
            # Summary Table Header
            pdf.set_fill_color(*TTA_NAVY)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"PROPOSAL FOR: {dest.upper()}", 0, 1, 'C', True)
            
            # Content
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            pdf.ln(5)
            pdf.cell(0, 10, f"Pax: {pax}", 0, 1)
            pdf.cell(0, 10, f"Accommodation: {hotel}", 0, 1)
            pdf.cell(0, 10, f"Cost: USD {cost} Per Adult", 0, 1)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 10, "ROE: Rate of Exchange will be Xe + 1.2 INR", 0, 1)
            
            pdf.ln(10)
            pdf.set_text_color(*TTA_NAVY)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, "DETAILED ITINERARY", 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)
            
            # Clean and add itinerary notes
            pdf.multi_cell(0, 7, raw_notes)
            
            # Download link
            pdf_output = pdf.output(dest="S").encode('latin-1')
            b64 = base64.b64encode(pdf_output).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="TTA_Proposal_{dest}.pdf">📥 Download TTA PDF Proposal</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Proposal Ready!")

st.sidebar.image("https://ttagroups.net/wp-content/uploads/2023/04/TTA-Logo.png", width=150)
st.sidebar.info("This tool uses Gemini AI to transform rough travel notes into professional client-ready proposals.")
