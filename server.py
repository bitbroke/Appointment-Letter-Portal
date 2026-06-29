import os
import re
import io
import tempfile
import fitz  # PyMuPDF
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="VITronix Appointment Portal")

# Load excel data
EXCEL_PATH = "members.xlsx"
TEMPLATE_PATH = "template.pdf"
LOGO_PATH = "logo.jpeg"

def extract_reg_no(email):
    if not isinstance(email, str):
        return ""
    email = email.strip().lower()
    if '@' in email:
        prefix = email.split('@')[0]
        parts = prefix.split('.')
        for part in parts:
            if re.match(r'^\d{2}[a-z]{3}\d{4,5}$', part):
                return part.upper()
    return ""

def load_members():
    if not os.path.exists(EXCEL_PATH):
        return None
    df = pd.read_excel(EXCEL_PATH)
    df['Name_Clean'] = df['Name'].astype(str).str.strip().str.lower()
    df['Team_Clean'] = df['Team'].astype(str).str.strip().str.lower()
    df['Reg_No'] = df['Email ID'].apply(extract_reg_no)
    df['Email_Clean'] = df['Email ID'].astype(str).str.strip().str.lower()
    return df

# API Request model
class VerifyRequest(BaseModel):
    name: str
    team: str
    reg_no: str

@app.get("/api/teams")
def get_teams():
    df = load_members()
    if df is None:
        return []
    return sorted(list(df['Team'].dropna().unique()))

@app.post("/api/verify")
def verify_member(req: VerifyRequest):
    df = load_members()
    if df is None:
        raise HTTPException(status_code=500, detail="Members database not found.")
    
    search_name = req.name.strip().lower()
    search_team = req.team.strip().lower()
    search_reg = req.reg_no.strip().lower()
    
    # Match name & team
    matched_rows = df[
        (df['Name_Clean'] == search_name) & 
        (df['Team_Clean'] == search_team)
    ]
    
    matched_member = None
    for idx, row in matched_rows.iterrows():
        row_reg = str(row['Reg_No']).lower()
        row_email = str(row['Email_Clean']).lower()
        
        # Match registration number or email address
        if (row_reg and search_reg == row_reg) or (search_reg == row_email) or (search_reg in row_email):
            matched_member = row
            break
            
    if matched_member is None:
        raise HTTPException(status_code=400, detail="Verification failed. Details do not match our records.")
    
    return {
        "status": "verified",
        "name": matched_member['Name'],
        "position": matched_member['Position'],
        "team": matched_member['Team']
    }

@app.get("/api/download")
def download_pdf(name: str, team: str, reg_no: str):
    df = load_members()
    if df is None:
        raise HTTPException(status_code=500, detail="Members database not found.")
    
    search_name = name.strip().lower()
    search_team = team.strip().lower()
    search_reg = reg_no.strip().lower()
    
    matched_rows = df[
        (df['Name_Clean'] == search_name) & 
        (df['Team_Clean'] == search_team)
    ]
    
    matched_member = None
    for idx, row in matched_rows.iterrows():
        row_reg = str(row['Reg_No']).lower()
        row_email = str(row['Email_Clean']).lower()
        if (row_reg and search_reg == row_reg) or (search_reg == row_email) or (search_reg in row_email):
            matched_member = row
            break
            
    if matched_member is None:
        raise HTTPException(status_code=400, detail="Verification failed.")
        
    if not os.path.exists(TEMPLATE_PATH):
        raise HTTPException(status_code=500, detail="Template not found.")
        
    try:
        doc = fitz.open(TEMPLATE_PATH)
        page = doc[0]
        
        MARGIN_LEFT = 65
        MARGIN_RIGHT = 65
        MARGIN_TOP = 170
        MARGIN_BOTTOM = 700
        FONT_SIZE = 15
        
        rect = fitz.Rect(MARGIN_LEFT, MARGIN_TOP, page.rect.width - MARGIN_RIGHT, MARGIN_BOTTOM)
        
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
        
        css_style = f"* {{ font-family: sans-serif; font-size: {FONT_SIZE}px; text-align: justify; line-height: 1.4; }}"
        page.insert_htmlbox(rect, html_text, css=css_style)
        
        temp_filename = f"temp_{member_name.replace(' ', '_')}.pdf"
        temp_filepath = os.path.join(tempfile.gettempdir(), temp_filename)
        doc.save(temp_filepath)
        doc.close()
        
        with open(temp_filepath, "rb") as f:
            pdf_bytes = f.read()
            
        try:
            os.remove(temp_filepath)
        except:
            pass
        
        filename = f"{member_name.replace(' ', '_')}_Appointment_Letter.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.get("/logo.jpeg")
def get_logo():
    if os.path.exists(LOGO_PATH):
        return FileResponse(LOGO_PATH)
    raise HTTPException(status_code=404, detail="Logo not found.")

@app.get("/")
def get_index():
    if os.path.exists("templates/index.html"):
        return FileResponse("templates/index.html")
    return HTMLResponse("<h1>Frontend Template index.html Not Found</h1>", status_code=404)
