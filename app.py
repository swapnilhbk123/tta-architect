import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# --- 1. AI CONFIGURATION ---
API_KEY = "AIzaSyBw1yb2etrB_fRFpd_q2PE0JbXVrddlIfw"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"AI Setup Error: {e}")

# --- 2. TTA BRANDING ---
NAVY = colors.HexColor("#0D2B4E")
GOLD = colors.HexColor("#C9A84C")
WHITE = colors.white
BLACK = colors.black

st.set_page_config(page_title="TTA Itinerary Architect", page_icon="✈️", layout="wide")

# --- 3. UI LAYOUT ---
st.title("TTA Group | AI Itinerary Architect")
st.write("Professional DMC Automation for WeAsia/TTA Group")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Logistics")
    ref_no = st.text_input("Quotation Ref", "CS001")
    dest = st.text_input("Destination", placeholder="e.g. Bali")
    pax = st.text_input("Total Pax", placeholder="e.g. 4")
    price = st.text_input("Cost per Pax (USD)", placeholder="337")
    hotel = st.text_input("Hotel Name", placeholder="Grand Zuri")

with col2:
    st.subheader("📅 Raw Notes")
    raw_itinerary = st.text_area("Paste rough notes here:", height=200)

if st.button("✨ GENERATE PROPOSAL"):
    if not (dest and raw_itinerary):
        st.error("Please enter Destination and Itinerary.")
    else:
        with st.spinner("Gemini is rewriting your itinerary..."):
            # The Prompt that makes the "Useless" text "Professional"
            prompt = f"Rewrite this travel itinerary for a luxury DMC proposal. Make it descriptive and exciting. Destination: {dest}. Notes: {raw_itinerary}"
            
            try:
                response = model.generate_content(prompt)
                polished_text = response.text
            except:
                polished_text = raw_itinerary # Fallback if AI fails

            # PDF GENERATION
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # FIXED READABLE STYLES
            header_style = ParagraphStyle('H', parent=styles['Heading1'], textColor=WHITE, backColor=NAVY, alignment=1, spaceAfter=20, borderPadding=10)
            sub_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=12, textColor=NAVY, fontName='Helvetica-Bold')
            body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14, textColor=BLACK)

            story = []
            story.append(Paragraph(f"TOUR PROPOSAL: {dest.upper()}", header_style))
            
            # Pricing Table
            data = [
                ["Destination", dest],
                ["Total Pax", pax],
                ["Hotel", hotel],
                ["Cost per Pax", f"USD {price}"],
                ["ROE Logic", "Xe + 1.2 INR"]
            ]
            t = Table(data, colWidths=[150, 300])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
                ('TEXTCOLOR', (0,0), (-1,-1), BLACK),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('PADDING', (0,0), (-1,-1), 10)
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
            story.append(Paragraph("DETAILED ITINERARY", sub_style))
            story.append(Spacer(1, 10))
            story.append(Paragraph(polished_text.replace('\n', '<br/>'), body_style))
            
            doc.build(story)
            buffer.seek(0)
            
            st.success("Proposal Generated!")
            st.download_button("📥 DOWNLOAD PDF", data=buffer, file_name=f"TTA_{dest}.pdf", mime="application/pdf")
