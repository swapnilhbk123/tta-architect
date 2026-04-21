# app.py  —  TTA Itinerary Builder  |  Streamlit Frontend
import streamlit as st
from datetime import date, timedelta
from pdf_generator import build_pdf

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="TTA Itinerary Builder",
    page_icon="compass",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D2B4E 0%, #0a2240 100%);
    }
    section[data-testid="stSidebar"] * { color: #E8F0F8 !important; }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #C9A84C !important;
        font-family: 'Lora', serif;
        font-size: 1.1rem;
        border-bottom: 1px solid #C9A84C44;
        padding-bottom: 6px;
        margin-bottom: 8px;
    }

    /* Main headings */
    h1 { font-family: 'Lora', serif !important; color: #0D2B4E !important; }
    h2, h3 { font-family: 'Lora', serif !important; color: #0D2B4E !important; }

    /* Expander */
    .streamlit-expanderHeader {
        background: #F5F7FA;
        border: 1px solid #C8D4E3;
        border-radius: 6px;
        font-weight: 600;
        color: #0D2B4E !important;
    }

    /* Tab active */
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #C9A84C !important;
        color: #0D2B4E !important;
        font-weight: 700;
    }

    /* Metric boxes */
    div[data-testid="metric-container"] {
        background: #F5F7FA;
        border: 1px solid #C8D4E3;
        border-radius: 8px;
        padding: 12px;
    }

    /* Download button */
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #C9A84C, #e0b85c) !important;
        color: #0D2B4E !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 0.6rem 2rem !important;
        letter-spacing: 0.5px;
    }

    /* Primary button */
    div[data-testid="stButton"] button[kind="primary"] {
        background: #0D2B4E !important;
        color: white !important;
        border-radius: 6px !important;
    }

    /* Section cards */
    .section-card {
        background: #F5F7FA;
        border: 1px solid #C8D4E3;
        border-left: 4px solid #C9A84C;
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    /* Gold tag */
    .gold-tag {
        background: #C9A84C;
        color: #0D2B4E;
        font-weight: 700;
        font-size: 0.72rem;
        padding: 2px 10px;
        border-radius: 20px;
        display: inline-block;
        letter-spacing: 0.8px;
    }

    .navy-tag {
        background: #0D2B4E;
        color: white;
        font-weight: 600;
        font-size: 0.72rem;
        padding: 2px 10px;
        border-radius: 20px;
        display: inline-block;
    }

    hr { border-color: #C8D4E3 !important; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar — Company Info ────────────────────────────────────────
with st.sidebar:
    st.markdown("## Company Profile")
    company_name = st.text_input("Company Name", value="TTA Group")
    email        = st.text_input("Email",   value="Salesindia@ttagroups.net")
    phone        = st.text_input("Phone",   value="+91 9028227102")
    website      = st.text_input("Website", value="Ttagroups.net")

    st.markdown("---")
    st.markdown("## Default T&C")
    st.caption("Add company-wide terms below. You can add trip-specific ones in the main form.")
    default_tnc_raw = st.text_area(
        "One term per line",
        value=(
            "All prices are subject to availability at time of confirmation.\n"
            "Payment schedule as per booking confirmation.\n"
            "Rates are non-commissionable.\n"
            "The company reserves the right to amend itinerary due to operational reasons."
        ),
        height=160,
    )
    default_tnc = [t.strip() for t in default_tnc_raw.strip().splitlines() if t.strip()]

    st.markdown("---")
    st.caption("TTA Itinerary Builder v2.0")


# ── Main Area ────────────────────────────────────────────────────
st.markdown('<h1 style="margin-bottom:0">Itinerary & Quotation Builder</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#8A9BB0;margin-top:4px;font-size:0.95rem">Build professional travel quotations with PDF export — free, fast, yours.</p>', unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "  Trip Details",
    "  Hotels",
    "  Day-wise Itinerary",
    "  Costs & Pricing",
    "  Inclusions / Exclusions",
    "  Preview & Export",
])


# ═══════════════════════════════════════════════════════════════
#  TAB 1 — TRIP DETAILS
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Trip Overview")
    col1, col2 = st.columns(2)
    with col1:
        trip_title    = st.text_input("Trip Title *", value="AZERBAIJAN & GEORGIA COMBO",
                                       help="e.g. BALI FAMILY ESCAPE")
        trip_subtitle = st.text_input("Trip Tagline / Subtitle",
                                       value="THE GREAT CAUCASUS CROSSING",
                                       help="e.g. 7 Days of Paradise")
        trip_type     = st.text_input("Package Type", value="Combined Land Package",
                                       help="e.g. Leisure, MICE, Honeymoon")

    with col2:
        start_date  = st.date_input("Start Date", value=date(2026, 5, 18))
        num_pax     = st.number_input("Number of Passengers (Pax)", min_value=1, max_value=500, value=6)
        total_nights= st.number_input("Total Nights", min_value=1, max_value=60, value=6)

    st.markdown("---")
    st.subheader("Introduction Paragraph")
    intro_text = st.text_area(
        "This appears at the top of the PDF after the header",
        value=(
            f"Greetings from {company_name}! We are pleased to present this exclusive travel "
            "itinerary crafted especially for you. Please review the details below and feel free "
            "to reach out for any customization."
        ),
        height=100,
    )


# ═══════════════════════════════════════════════════════════════
#  TAB 2 — HOTELS
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Accommodation Details")
    num_hotels = st.number_input("How many hotel entries?", min_value=1, max_value=10, value=2)

    hotels = []
    for i in range(int(num_hotels)):
        with st.expander(f"Hotel {i + 1}", expanded=(i == 0)):
            h1, h2, h3, h4 = st.columns([2, 3, 2, 1])
            with h1:
                loc  = st.text_input("City / Location", key=f"hloc_{i}",
                                      value="Baku" if i == 0 else "Tbilisi")
            with h2:
                name = st.text_input("Hotel Name",     key=f"hname_{i}",
                                      value="Antique Hotel" if i == 0 else "Hotel Irmisa")
            with h3:
                room = st.text_input("Room Type",      key=f"hroom_{i}", value="Standard Room")
            with h4:
                nts  = st.number_input("Nights", min_value=1, max_value=30,
                                        key=f"hnts_{i}", value=3)
            hotels.append({"location": loc, "hotel_name": name, "room_type": room, "nights": nts})

    st.markdown("---")
    breakfast_note = st.text_input(
        "Meal Inclusion Note",
        value="Daily Breakfast is included at all hotels.",
    )


# ═══════════════════════════════════════════════════════════════
#  TAB 3 — DAY-WISE ITINERARY
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Day-wise Itinerary")
    st.caption("Each day auto-numbers. Fill in the activity and details for each day.")

    num_days = int(total_nights) + 1  # nights + 1 = total days
    st.info(f"Based on {total_nights} nights you have **{num_days} days** to fill in.")

    days = []
    for i in range(num_days):
        day_date = start_date + timedelta(days=i)
        day_label = f"Day {i + 1:02d}  —  {day_date.strftime('%d %b')}"

        with st.expander(day_label, expanded=(i == 0)):
            dc1, dc2 = st.columns(2)
            with dc1:
                location = st.text_input(
                    "Location / City",
                    key=f"dloc_{i}",
                    value=["BAKU", "BAKU", "ABSHERON", "GABALA / TBILISI",
                           "TBILISI", "KAZBEGI", "DEPARTURE"][i]
                    if i < 7 else "",
                )
            with dc2:
                activity = st.text_input(
                    "Activity / Day Theme",
                    key=f"dact_{i}",
                    value=["Arrival", "City Heritage Tour", "Fire & Rock Tour",
                           "Cross-Border Transfer", "Old Tbilisi City Tour",
                           "Ananuri - Gudauri - Kazbegi", "Final Departure"][i]
                    if i < 7 else "",
                )

            details_raw = st.text_area(
                "Details — one bullet per line",
                key=f"ddet_{i}",
                value="\n".join([
                    ["Airport pickup and transfer to hotel\nCheck-in and evening at leisure",
                     "Old City visit including Maiden Tower\nHeydar Aliyev Centre Photostop\nHighland Park overview",
                     "Gobustan Rock Museum & Mud Volcano by 4x4 UAZ\nAteshgah Fire Temple & Yanardag visit",
                     "Gabala Cable Car ride & Lake Nohur\nTransfer to Lagodekhi Border\nDrive to Tbilisi; check-in at hotel",
                     "Tbilisi Cable Car to Narikala Fortress\nSulphur Baths & Peace Bridge\nMetekhi Church & Shardeni Street",
                     "Ananuri Fortress & Zhinvali Reservoir\nGudauri Friendship Monument\nKazbegi: Gergety Church by 4x4 Jeep",
                     "Check-out after breakfast\nPrivate transfer to Tbilisi Airport for departure"][i]
                ] if i < 7 else [""]),
                height=90,
            )
            details = [d.strip() for d in details_raw.strip().splitlines() if d.strip()]

            days.append({
                "day_num":  f"Day {i + 1:02d}",
                "date":     day_date.strftime("%d %b %Y"),
                "location": location,
                "activity": activity,
                "details":  details,
            })


# ═══════════════════════════════════════════════════════════════
#  TAB 4 — COSTS
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Pricing & Cost Details")
    pr1, pr2, pr3 = st.columns(3)
    with pr1:
        currency    = st.selectbox("Currency", ["USD", "EUR", "GBP", "AED", "INR", "SGD", "THB", "Other"], index=0)
        if currency == "Other":
            currency = st.text_input("Enter currency code", value="USD")
    with pr2:
        total_cost  = st.text_input("Total Group Cost", value="2,390",
                                     help="e.g. 2,390  or  2390")
    with pr3:
        per_pax_cost= st.text_input("Per Pax Cost (optional)", value="",
                                     placeholder="Leave blank if not needed")

    roe_note = st.text_input(
        "Rate of Exchange (ROE) Note",
        value="Rate of Exchange applicable at the time of payment will be Xe + 1.2 INR.",
        help="Leave blank to omit",
    )

    st.markdown("---")
    st.subheader("Cost Breakdown Table (Optional)")
    st.caption("Add line items for a detailed cost breakdown in the PDF.")
    show_breakdown = st.checkbox("Include cost breakdown table")

    cost_items = []
    if show_breakdown:
        num_cost_rows = st.number_input("Number of line items", min_value=1, max_value=20, value=4)
        for ci in range(int(num_cost_rows)):
            cc1, cc2 = st.columns([3, 1])
            with cc1:
                clabel = st.text_input("Component", key=f"clabel_{ci}",
                                        placeholder="e.g. Hotel Accommodation (6 nights)")
            with cc2:
                camt   = st.text_input("Amount",    key=f"camt_{ci}",
                                        placeholder=f"e.g. {currency} 800")
            if clabel:
                cost_items.append((clabel, camt))


# ═══════════════════════════════════════════════════════════════
#  TAB 5 — INCLUSIONS / EXCLUSIONS / T&C
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Inclusions")
    inclusions_raw = st.text_area(
        "One item per line",
        value=(
            "Airport transfers on private basis throughout the tour\n"
            "Hotel accommodation as per itinerary\n"
            "Daily breakfast at all hotels\n"
            "All sightseeing and entrance fees as per program\n"
            "English-speaking local guide"
        ),
        height=160,
    )
    inclusions = [l.strip() for l in inclusions_raw.strip().splitlines() if l.strip()]

    st.markdown("---")
    st.subheader("Exclusions")
    exclusions_raw = st.text_area(
        "One item per line",
        value=(
            "International airfare and airport taxes\n"
            "Travel insurance\n"
            "Personal expenses, tips and gratuities\n"
            "Meals not mentioned in the itinerary\n"
            "Visa fees"
        ),
        height=140,
    )
    exclusions = [l.strip() for l in exclusions_raw.strip().splitlines() if l.strip()]

    st.markdown("---")
    st.subheader("Additional Trip-Specific Terms & Conditions")
    trip_tnc_raw = st.text_area(
        "One term per line (company T&C from sidebar will also be included)",
        placeholder="e.g. Rates are valid until 30 June 2026.",
        height=100,
    )
    trip_tnc = [t.strip() for t in trip_tnc_raw.strip().splitlines() if t.strip()]
    all_tnc  = trip_tnc + default_tnc


# ═══════════════════════════════════════════════════════════════
#  TAB 6 — PREVIEW & EXPORT
# ═══════════════════════════════════════════════════════════════
with tab6:
    st.subheader("Summary Preview")

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Trip",          trip_title[:22] + "..." if len(trip_title) > 22 else trip_title)
    mc2.metric("Passengers",    f"{num_pax} Pax")
    mc3.metric("Total Cost",    f"{currency} {total_cost}")
    mc4.metric("Days",          f"{num_days} Days / {total_nights} Nights")

    st.markdown("---")

    # Show itinerary preview table
    st.markdown("**Day-wise Summary**")
    preview_data = {
        "Day":      [d["day_num"] for d in days],
        "Date":     [d["date"]    for d in days],
        "Location": [d["location"]for d in days],
        "Theme":    [d["activity"]for d in days],
    }
    import pandas as pd
    st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Hotels**")
    if hotels:
        hotel_preview = pd.DataFrame(hotels)
        hotel_preview.columns = ["Location", "Hotel", "Room Type", "Nights"]
        st.dataframe(hotel_preview, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Build and export
    if st.button("Generate PDF", type="primary", use_container_width=True):
        with st.spinner("Building your professional PDF..."):

            pdf_data = {
                # Trip info
                "trip_title":    trip_title,
                "trip_subtitle": trip_subtitle,
                "intro_text":    intro_text,
                "start_date":    start_date.strftime("%d %b %Y"),
                "num_pax":       f"{num_pax:02d} Pax",
                "total_nights":  f"{total_nights:02d} Nights",
                "trip_type":     trip_type,
                # Cost
                "currency":      currency,
                "total_cost":    total_cost,
                "per_pax_cost":  per_pax_cost.strip() if per_pax_cost else "",
                "roe_note":      roe_note.strip(),
                "cost_items":    cost_items if show_breakdown else [],
                # Hotels
                "hotels":        hotels,
                "breakfast_note":breakfast_note,
                # Itinerary
                "days":          days,
                # Inc / Exc / TnC
                "inclusions":    inclusions,
                "exclusions":    exclusions,
                "tnc":           all_tnc,
                # Company
                "company_name":  company_name,
                "email":         email,
                "phone":         phone,
                "website":       website,
            }

            try:
                pdf_bytes = build_pdf(pdf_data)
                safe_title = trip_title.replace(" ", "_").replace("/", "-")[:40]
                filename   = f"{company_name.replace(' ','_')}_{safe_title}_Quotation.pdf"

                st.success("PDF generated successfully! Click below to download.")
                st.download_button(
                    label="Download PDF Quotation",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
                st.exception(e)

    st.markdown("---")
    st.caption(f"Generated by TTA Itinerary Builder | {company_name} | {website}")
