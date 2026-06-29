# VITronix Appointment Letters Portal

A minimal, professional, responsive web application for the core members of the **VITronix Club** to verify their credentials and dynamically download their official appointment letters.

## Features

- **Responsive Full-Width Dashboard**: Left-to-right split container designed to stack beautifully on both desktop and mobile viewports.
- **Rich Aesthetics**: Premium dark theme (`#08090c`) with vibrant neon cyan details (`#00e5ff`) and micro-interactions.
- **GSAP Animations**: Clean entrance transitions and interactive elements.
- **SVG Electronic Doodles**: Subtle schematics representing microcontroller circuits, resistors, and capacitors.
- **Robust Verification**: Validates Full Name, Team (from dynamic list), and Registration Number or Email Address against the official members Excel directory.
- **Dynamic PDF Customization**: Rewrites the letter text area of a base template PDF in real-time, inserting member details, and triggers native browser downloads.

## Tech Stack

- **Backend**: FastAPI (Python)
- **PDF Manipulation**: PyMuPDF (fitz)
- **Data Processor**: Pandas, OpenPyXL
- **Frontend**: HTML5, Vanilla CSS, TailwindCSS (for utility classes), GSAP (for animations)

## Project Structure

```
├── server.py              # FastAPI server containing matching logic and PDF builder
├── members.xlsx           # Official member directory
├── template.pdf           # Original appointment letter PDF template
├── logo.jpeg              # Official VITronix logo
├── templates/
│   └── index.html         # Responsive, animated UI
└── .gitignore             # Git ignore file for python caches and generated temp PDFs
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vitronixclub/Appointment-Letter-Portal.git
   cd Appointment-Letter-Portal
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pymupdf pandas openpyxl
   ```

3. Run the FastAPI development server:
   ```bash
   python -m uvicorn server:app --port 8501
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

## Development Guidelines

- The application uses `members.xlsx` for credentials verification. Do not alter the structure of columns (`Name`, `Team`, `Email ID`, `Position`).
- PDF generation uses temporary path-based writing to avoid stream lockups during concurrent downloads.
