import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# --- 1. AI CONFIGURATION (DIRECT KEY) ---
# Replace the string below if you ever regenerate your key
API_KEY = "AIzaSyBw1yb2etrB_fRFpd_q2PE0JbXVrddlIfw"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 2. TTA BRANDING COLORS ---
NAVY = colors.HexColor("#0D2B4E")
GOLD = colors.HexColor("#C9A84C")
LIGHT_BLUE = colors.HexColor("#F5F7FA")

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="TTA Itinerary Architect", page_icon="✈️", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #fcfcfc; }}
    .stButton>button {{ 
        background-color: {NAVY.hexval()}; 
        color: white; 
        border: 2px solid {GOLD.hexval()};
        font-weight: bold;
        width: 100%;
    }}
    h1 {{ color: {NAVY.hexval()}; border-bottom: 3px solid {GOLD.hexval()}; }}
    </style>
    """, unsafe_allow_html=True)

st.title("TTA Group | AI Itinerary Architect")
st.write("Professional DMC Automation for WeAsia/TTA Group")

# --- 4. INPUT FIELDS ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Trip Details")
    ref_no = st.text_input("Quotation Ref", "CS" + "001")
    dest = st.text_input("Destination", placeholder="e.g. Phuket, Thailand")
    pax = st.text_input("Number of Pax", placeholder="e.g. 10 Adults")
    price = st.text_input("Price per Pax (USD)", placeholder="e.g. 253")
    hotel = st.text_input("Hotel Name & Room Type", placeholder="e.g. Hiso Hotel (Superior)")

with col2:
    st.subheader("📅 Raw Itinerary")
    raw_itinerary = st.text_area("Paste your rough notes here:", height=200, 
                                 placeholder="Day 1: Arrival, breakfast at hotel...\nDay 2: Island tour...")

# --- 5. PROCESSING LOGIC ---
if st.button("✨ GENERATE PROFESSIONAL PROPOSAL"):
    if not (dest and raw_itinerary and price):
        st.error("Missing information! Please fill in Destination, Price, and Itinerary.")
    else:
        with st.spinner("Gemini is rewriting your itinerary..."):
            # AI Prompt to "Beautify" the script
            prompt = f"""
            Act as a professional travel consultant for TTA Group. 
            Rewrite this raw itinerary into a polished, inviting, and professional travel script.
            Use elegant language suitable for a high-end DMC proposal.
            Keep it day by day.
            Itinerary Notes: {raw_itinerary}
            """
            
            try:
                response = model.generate_content(prompt)
                polished_text = response.text
            except Exception as e:
                polished_text = raw_itinerary 
                st.error(f"AI Error: {e}")

            # PDF Generation
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
            styles = getSampleStyleSheet()
            
            # Custom PDF Styles
            header_style = ParagraphStyle('H', parent=styles['Heading1'], textColor=colors.white, backColor=NAVY, alignment=1, spaceAfter=20, borderPadding=10)
            sub_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=10, textColor=NAVY, fontName='Helvetica-Bold')
            body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14)

            story = []
            
            # PDF Content
            story.append(Paragraph(f"TOUR PROPOSAL: {dest.upper()}", header_style))
            story.append(Paragraph(f"<b>Reference:</b> {ref_no}", body_style))
            story.append(Spacer(1, 12))

            # Pricing Table
            data = [
                [Paragraph("<b>Destination</b>", sub_style), Paragraph(dest, body_style)],
                [Paragraph("<b>Total Pax</b>", sub_style), Paragraph(pax, body_style)],
                [Paragraph("<b>Hotel</b>", sub_style), Paragraph(hotel, body_style)],
                [Paragraph("<b>Cost per Pax</b>", sub_style), Paragraph(f"USD {price}", body_style)],
                [Paragraph("<b>ROE Logic</b>", sub_style), Paragraph("Xe + 1.2 INR", body_style)]
            ]
            t = Table(data, colWidths=[120, 330])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), LIGHT_BLUE),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 8)
            ]))
            story.append(t)
            story.append(Spacer(1, 20))

            # Detailed Itinerary Section
            story.append(Paragraph("DETAILED ITINERARY", sub_style))
            story.append(Spacer(1, 5))
            story.append(Paragraph(polished_text.replace('\n', '<br/>'), body_style))
            
            # Footer Remarks
            story.append(Spacer(1, 30))
            story.append(Paragraph("<i>Note: This is a system-generated proposal from TTA Group. Rates are subject to ROE fluctuations.</i>", body_style))

            doc.build(story)
            buffer.seek(0)
            
            st.success("Proposal Ready!")
            st.download_button(
                label="📥 DOWNLOAD PDF PROPOSAL",
                data=buffer,
                file_name=f"TTA_Proposal_{dest}.pdf",
                mime="application/pdf"
            )
