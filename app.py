import subprocess
import sys

# --- EMERGENCY FORCE INSTALL ---
# This forces the server to install the missing libraries immediately
try:
    import google.generativeai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai", "reportlab"])

import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# --- 1. AI CONFIGURATION ---
API_KEY = "AIzaSyBw1yb2etrB_fRFpd_q2PE0JbXVrddlIfw"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. TTA BRANDING ---
NAVY = colors.HexColor("#0D2B4E")
GOLD = colors.HexColor("#C9A84C")

st.set_page_config(page_title="TTA Itinerary Architect", layout="wide")

st.title("TTA Group | AI Itinerary Architect")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Logistics")
    dest = st.text_input("Destination", "Bali")
    pax = st.text_input("Total Pax", "4")
    price = st.text_input("Cost (USD)", "337")
    hotel = st.text_input("Hotel", "Grand Zuri")

with col2:
    st.subheader("📅 Raw Notes")
    raw_itinerary = st.text_area("Paste notes here:", height=200)

if st.button("✨ GENERATE PROPOSAL"):
    with st.spinner("AI is working..."):
        prompt = f"Rewrite this as a luxury travel brochure for {dest}: {raw_itinerary}"
        
        try:
            response = model.generate_content(prompt)
            polished_text = response.text
        except:
            polished_text = raw_itinerary

        # PDF Build
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Style Fix: Ensuring Black Text on White Background
        body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, textColor=colors.black)
        header_style = ParagraphStyle('H', parent=styles['Heading1'], textColor=colors.white, backColor=NAVY, alignment=1)

        story = [Paragraph(f"TTA PROPOSAL: {dest.upper()}", header_style), Spacer(1, 20)]
        story.append(Paragraph(polished_text.replace('\n', '<br/>'), body_style))
        
        doc.build(story)
        buffer.seek(0)
        
        st.success("Done!")
        st.download_button("📥 DOWNLOAD PDF", data=buffer, file_name=f"TTA_{dest}.pdf")
