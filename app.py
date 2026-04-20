import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# --- 1. AI CONFIGURATION ---
# Direct API Key integration
API_KEY = "AIzaSyBw1yb2etrB_fRFpd_q2PE0JbXVrddlIfw"

try:
    genai.configure(api_key=API_KEY)
    # Using gemini-1.5-flash for faster response
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Setup Error: {e}")

# --- 2. TTA BRANDING & COLORS ---
NAVY = colors.HexColor("#0D2B4E")
GOLD = colors.HexColor("#C9A84C")
WHITE = colors.white
BLACK = colors.black
GHOST_WHITE = colors.HexColor("#F8F9FA")

st.set_page_config(page_title="TTA Itinerary Architect", page_icon="✈️", layout="wide")

# Custom CSS for the web interface
st.markdown(f"""
    <style>
    .stApp {{ background-color: #ffffff; }}
    .stButton>button {{ 
        background-color: {NAVY.hexval()}; 
        color: white; 
        border: 1px solid {GOLD.hexval()};
        font-weight: bold;
    }}
    h1 {{ color: {NAVY.hexval()}; border-bottom: 2px solid {GOLD.hexval()}; padding-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI LAYOUT ---
st.title("TTA Group | AI Itinerary Architect")
st.info("Fill in the details below to generate a professional PDF proposal.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Trip Details")
    ref_no = st.text_input("Quotation Reference", "TTA-QT-" + "2026")
    dest = st.text_input("Destination", placeholder="e.g. Bali, Indonesia")
    pax = st.text_input("Total Pax / Group Size", placeholder="e.g. 04 Adults")
    price = st.text_input("Cost per Pax (USD)", placeholder="e.g. 450")
    hotel = st.text_input("Hotel Details", placeholder="e.g. Grand Zuri (Superior Room)")

with col2:
    st.subheader("📅 Itinerary Points")
    raw_itinerary = st.text_area("Paste rough daily notes here:", height=220, 
                                 placeholder="1. Arrival\n2. Uluwatu Tour\n3. Departure")

# --- 4. CORE ENGINE ---
if st.button("✨ CREATE LUXURY PROPOSAL"):
    if not (dest and raw_itinerary):
        st.warning("⚠️ Please provide at least a Destination and some Itinerary notes.")
    else:
        with st.spinner("Gemini AI is crafting your luxury travel script..."):
            # The 'Magic' Prompt
            prompt = f"""
            System: You are a senior travel consultant for WeAsia / TTA Group. 
            Task: Rewrite the rough itinerary notes for {dest} into a professional, persuasive, and elegant travel brochure format.
            
            Style Guidelines:
            - Use descriptive, inviting language (e.g., 'Immerse yourself', 'Hand-picked experiences', 'Seamless transfers').
            - Maintain a clear Day-by-Day structure.
            - Ensure all locations mentioned in the notes are included but expanded into full sentences.
            
            ROUGH NOTES:
            {raw_itinerary}
            """
            
            try:
                response = model.generate_content(prompt)
                polished_text = response.text if response.text else raw_itinerary
            except Exception as ai_err:
                st.error(f"AI Handshake failed: {ai_err}")
                polished_text = raw_itinerary

            # --- PDF GENERATION ---
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            
            # Custom PDF Styles (Fixed for Legibility)
            title_style = ParagraphStyle('T', parent=styles['Heading1'], textColor=WHITE, backColor=NAVY, alignment=1, spaceAfter=20, borderPadding=12)
            label_style = ParagraphStyle('L', parent=styles['Normal'], fontSize=11, textColor=NAVY, fontName='Helvetica-Bold')
            val_style = ParagraphStyle('V', parent=styles['Normal'], fontSize=11, textColor=BLACK)
            day_style = ParagraphStyle('D', parent=styles['Normal'], fontSize=12, textColor=NAVY, fontName='Helvetica-Bold', spaceBefore=15, spaceAfter=5)
            body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14, textColor=BLACK, alignment=4)

            story = []
            
            # 1. Header Title
            story.append(Paragraph(f"PROPOSAL: {dest.upper()} SPECIAL", title_style))
            story.append(Paragraph(f"<b>Ref No:</b> {ref_no}", val_style))
            story.append(Spacer(1, 15))

            # 2. Pricing Summary Table
            table_data = [
                [Paragraph("<b>Destination</b>", label_style), Paragraph(dest, val_style)],
                [Paragraph("<b>Pax Count</b>", label_style), Paragraph(pax, val_style)],
                [Paragraph("<b>Accommodation</b>", label_style), Paragraph(hotel, val_style)],
                [Paragraph("<b>Package Cost</b>", label_style), Paragraph(f"USD {price} per person", val_style)],
                [Paragraph("<b>ROE Applied</b>", label_style), Paragraph("Xe + 1.2 INR", val_style)]
            ]
            summary_table = Table(table_data, colWidths=[140, 360])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), GHOST_WHITE),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 25))

            # 3. Itinerary Section
            story.append(Paragraph("CURATED TRAVEL EXPERIENCE", day_style))
            story.append(Spacer(1, 5))
            
            # Convert AI text into Paragraphs (handling line breaks)
            formatted_itinerary = polished_text.replace('\n', '<br/>')
            story.append(Paragraph(formatted_itinerary, body_style))
            
            # 4. Footer
            story.append(Spacer(1, 40))
            footer_text = "<i>Note: This is an automated proposal generated by TTA Group. All rates are subject to change based on actual availability and ROE at the time of booking.</i>"
            story.append(Paragraph(footer_text, body_style))

            doc.build(story)
            buffer.seek(0)
            
            st.success("✅ Your professional proposal is ready for download!")
            st.download_button(
                label="📥 DOWNLOAD PDF PROPOSAL",
                data=buffer,
                file_name=f"TTA_Proposal_{dest}.pdf",
                mime="application/pdf"
            )
