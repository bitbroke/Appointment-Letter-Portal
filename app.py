import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
import io
import os

# Set page configuration
st.set_page_config(
    page_title="VITronix - Appointment Portal",
    page_icon="⚡",
    layout="centered"
)

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Helper function to extract registration number from email ID
def extract_reg_no(email):
    if not isinstance(email, str):
        return ""
    email = email.strip().lower()
    if '@' in email:
        prefix = email.split('@')[0]
        parts = prefix.split('.')
        for part in parts:
            # Check for standard VIT registration number format (e.g. 24BCE10454, 25BAI11346)
            if re.match(r'^\d{2}[a-z]{3}\d{4,5}$', part):
                return part.upper()
    return ""

# Load excel data
@st.cache_data
def load_data():
    if os.path.exists("members.xlsx"):
        df = pd.read_excel("members.xlsx")
        # Clean columns
        df['Name_Clean'] = df['Name'].astype(str).str.strip().str.lower()
        df['Team_Clean'] = df['Team'].astype(str).str.strip().str.lower()
        df['Reg_No'] = df['Email ID'].apply(extract_reg_no)
        df['Email_Clean'] = df['Email ID'].astype(str).str.strip().str.lower()
        return df
    return None

df = load_data()

# App Header
st.markdown("<h1 class='gradient-title'>VITronix</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>JOIN THE ROBOLUTION! | Appointment Letter Portal</p>", unsafe_allow_html=True)

# Logo Display
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

# Render main card container
st.markdown("""
<div class='main-card'>
    <h3 style='text-align: center; color: #a259ff; margin-bottom: 1.5rem;'>Verify Core Member Details</h3>
</div>
""", unsafe_allow_html=True)

# Main form fields (placed within the layout)
if df is not None:
    # Teams for selection
    unique_teams = sorted(list(df['Team'].dropna().unique()))
    
    with st.container():
        name_input = st.text_input("Full Name", placeholder="Enter your full name as in Excel (e.g. Ankshit Dey)")
        team_input = st.selectbox("Select Your Team", options=["-- Select Team --"] + unique_teams)
        reg_input = st.text_input("Registration Number / Email Address", placeholder="e.g. 24BCE10454 or email@gmail.com")
        
        verify_btn = st.button("Verify & Generate Appointment Letter")
        
        if verify_btn:
            if not name_input or team_input == "-- Select Team --" or not reg_input:
                st.error("Please fill in all the details correctly.")
            else:
                # Match
                search_name = name_input.strip().lower()
                search_team = team_input.strip().lower()
                search_reg = reg_input.strip().lower()
                
                # Check match
                # Check name and team first
                matched_rows = df[
                    (df['Name_Clean'] == search_name) & 
                    (df['Team_Clean'] == search_team)
                ]
                
                verified = False
                matched_member = None
                
                for idx, row in matched_rows.iterrows():
                    # Check registration number or email
                    row_reg = str(row['Reg_No']).lower()
                    row_email = str(row['Email_Clean']).lower()
                    
                    if (row_reg and search_reg == row_reg) or (search_reg == row_email) or (search_reg in row_email):
                        verified = True
                        matched_member = row
                        break
                
                if verified and matched_member is not None:
                    st.markdown("""
                    <div class='success-card'>
                        <h4 style='color: #00e5ff; margin: 0;'>Verification Successful! 🎉</h4>
                        <p style='margin: 0.5rem 0 0 0; color: #555;'>Your details have been successfully cross-referenced with the VITronix core members registry.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Generate PDF
                    try:
                        doc = fitz.open("template.pdf")
                        page = doc[0]
                        
                        # Margins from code snippet
                        FINAL_MARGIN_LEFT = 65
                        FINAL_MARGIN_RIGHT = 65
                        FINAL_MARGIN_TOP = 170
                        FINAL_MARGIN_BOTTOM = 700
                        FINAL_FONT_SIZE = 15
                        
                        rect = fitz.Rect(FINAL_MARGIN_LEFT, FINAL_MARGIN_TOP, page.rect.width - FINAL_MARGIN_RIGHT, FINAL_MARGIN_BOTTOM)
                        
                        member_name = matched_member['Name']
                        member_position = matched_member['Position']
                        member_team = matched_member['Team']
                        
                        html_text = f"""
                        <p>Dear <b>{member_name}</b>,</p>

                        <p>This letter serves as formal confirmation of your appointment to the position of <b>{member_position}</b> of <b>{member_team}</b>.</p>
                        <p>In this role, you will be expected to execute the core responsibilities associated with your role, which include attending scheduled meetings, collaborating effectively with your team members, and contributing to the successful execution of our upcoming projects and events.</p>

                        <p>We look forward to welcoming you to the VITronix Club and are confident that your skills and expertise will greatly contribute to our continued success.
                        Once again, congratulations on your appointment! We anticipate a mutually rewarding and fulfilling working relationship.</p>

                        <p>Best Regards,<br>
                        <p>VITronix Club,</b></p>
                        <b>VIT Bhopal University</b></p>
                        """
                        
                        css_style = f"* {{ font-family: sans-serif; font-size: {FINAL_FONT_SIZE}px; text-align: justify; line-height: 1.4; }}"
                        page.insert_htmlbox(rect, html_text, css=css_style)
                        
                        # Output PDF
                        pdf_buffer = io.BytesIO()
                        doc.save(pdf_buffer)
                        doc.close()
                        
                        st.download_button(
                            label="Download Appointment Letter (PDF) 📥",
                            data=pdf_buffer.getvalue(),
                            file_name=f"{member_name.replace(' ', '_')}_Appointment_Letter.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"An error occurred while generating the PDF: {e}")
                else:
                    st.error("Verification failed. Please ensure the Name, Team, and Registration Number/Email match exactly with your club registration details.")
else:
    st.error("Excel sheet 'members.xlsx' not found. Please ensure it is present in the workspace.")

# Elegant footer with electronics theme
st.markdown("""
<div style='text-align: center; margin-top: 4rem; color: #a259ff; font-size: 0.85rem; opacity: 0.8;'>
    <span>⚡ Microcontrollers • FPV Drones • Robotics • IoT ⚡</span>
    <br>
    <span style='color: #6c757d;'>VITronix Club © 2026</span>
</div>
""", unsafe_allow_html=True)
