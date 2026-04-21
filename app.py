import streamlit as st
import os

# --- CRITICAL FIX: FORCE THE ENVIRONMENT VARIABLE ---
# This must happen BEFORE importing the AI library
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
else:
    st.error("API Key not found in Secrets!")
    st.stop()

import google.generativeai as genai
from fpdf import FPDF
import base64

# --- TTA BRANDING ---
TTA_EMAIL = "salesindia@ttagroups.net"
TTA_PHONE = "+91 90282 27102"
TTA_WEB = "ttagroups.net"
TTA_NAVY = (13, 43, 78)   
TTA_GOLD = (201, 168, 76) 

def clean_text(text):
    if not text: return ""
    replacements = {'\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'", 
                    '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u2023': '*', '\u2219': '*'}
    for char, rep in replacements.items():
        text = text.replace(char, rep)
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

# --- CONFIG AI ---
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

st.set_page_config(page_title="TTA Itinerary Architect", layout="wide")
st.title("✈️ TTA Group | Itinerary Architect")

col1, col2 = st.columns([1, 1])
with col1:
    dest = st.text_input("Destination")
    pax = st.text_input("Group Size")
    cost = st.text_input("Cost (USD)")
    hotel = st.text_input("Accommodation")
with col2:
    raw_notes = st.text_area("Paste notes here...", height=200)

if st.button("Generate Final PDF"):
    if dest and raw_notes:
        with st.spinner("Connecting to Gemini AI..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Create a high-end itinerary for {dest}: {raw_notes}")
                itinerary_text = response.text
                
                pdf = TTA_PDF()
                pdf.set_auto_page_break(auto=True, margin=25)
                pdf.add_page()
                
                # Header Summary
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
                
                pdf_bytes = pdf.output()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="TTA_{dest}.pdf" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#0D2B4E; color:white; border-radius:8px; cursor:pointer; font-weight:bold;">📥 DOWNLOAD PROPOSAL</button></a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("TTA Proposal Generated!")
            except Exception as e:
                st.error(f"Error: {e}")
