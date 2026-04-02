# Parents Bank 🏦

[![CI](https://github.com/USERNAME/ai_bank_tato/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/ai_bank_tato/actions/workflows/ci.yml)
![Parents Bank](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)

**Parents Bank** is a lightweight, mobile-first web application built with Python (Flask) and Tailwind CSS. It serves as a virtual "family bank" to help parents track their children's allowances, chores, and expenditures. It supports up to 4 child slots, with real-time updates without page reloads (SPA-like experience via Vanilla JS).

### 🤖 AI-Assisted Development (Vibe-Coding)
**Disclaimer:** This project is a deliberate exercise in **AI-assisted development** (sometimes referred to as "vibe-coding"). *Not a single line of code in this repository was written manually.* The entire application—including architecture, backend logic, frontend design, and documentation—was generated using an AI coding assistant. The primary purpose of this project is to develop and showcase competencies in AI orchestration, prompt engineering, and rapid AI-driven software development.

### Features
- **Multiple Slots**: Tracks up to 4 children (Slot 1 is always active, Slots 2-4 can be toggled).
- **Modern UI**: Dark mode, mobile-first design using Tailwind CSS.
- **Async Operations**: Fetch API integration for a smooth user experience.
- **Data Integrity**: Local JSON storage with file locking to prevent data corruption from concurrent access (e.g., accessed by two parents simultaneously).
- **Simple Security**: PIN-based login system to protect access.

### ⚠️ Security Disclaimer
**This is an educational project and is NOT designed to handle real financial data or real money.**
- The application stores the login PIN as plain-text inside the `.env` file for demonstration purposes.
- There is no database encryption implemented out-of-the-box.
- Do not expose this app to the public internet without wrapping it in a secure environment (e.g., reverse proxy with HTTPS and proper authentication).

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd ai_bank_tato
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # Install Playwright browser
   playwright install chromium
   ```

4. **Environment Variables:**
   Rename `.env.example` to `.env` and configure your settings:
   ```env
   APP_PIN=1234
   SECRET_KEY=your-secret-key
   DATA_FILE_PATH=data.json
   CHILD_1_NAME=Alice
   # ...
   ```

5. **Run the Application:**
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in your browser.

6. **Run Tests:**
   ```bash
   # Make sure venv is activated
   # Unit tests:
   pytest tests/test_logic.py
   # E2E tests:
   pytest tests/test_e2e.py
   ```

### 🛠️ Future Roadmap (TODO)
- [x] Implement unit tests using `pytest` for backend logic.
- [x] Implement end-to-end (E2E) tests using `playwright`.
- [x] Configure CI/CD Pipeline (e.g., GitHub Actions) for automated testing and linting.
