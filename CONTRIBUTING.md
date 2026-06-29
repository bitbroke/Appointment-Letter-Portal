# Contributing to VITronix Appointment Letters Portal

Thank you for planning to contribute to our project! Please read these guidelines to keep development consistent and clean.

## Code of Conduct

Please maintain professional, respectful, and constructive communication at all times.

## Workflow

1. Fork the repository and create your feature branch from the main branch:
   ```bash
   git checkout -b feature/your-awesome-feature
   ```
2. Set up your local environment and verify the FastAPI server runs correctly:
   ```bash
   python -m uvicorn server:app --port 8501
   ```
3. Implement your changes. Please make sure the layout remains responsive across all desktop, tablet, and mobile screens.
4. Verify code format and functionality.
5. Commit your changes with clear, structured messages:
   ```bash
   git commit -m "feat: description of the change"
   ```
6. Push to your branch and open a Pull Request.

## Design Rules

- **Color Scheme**: Strict dark theme with neon cyan detailing (`#00e5ff`). No generic or conflicting colors.
- **Aesthetics**: Electronic/robotics/schematic theme details only. No emojis are permitted anywhere in the layout.
- **Responsiveness**: Always use mobile-first or highly responsive class constraints (`w-full md:w-1/2`, etc.) to prevent clipping or scroll breaks.
