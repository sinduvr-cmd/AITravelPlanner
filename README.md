# AI Travel Planner ✈️ • Booking.com Demand API Integration

A modern, responsive single-page travel planning web application built with Python and Streamlit, featuring live accommodation recommendations powered by the **Booking.com Demand API (v3.2)** and seamless algorithmic travel intelligence.

🌐 **Live Application:** [https://aitravelplanner-cgbcs3jvqusfwjrd8u84sa.streamlit.app/](https://aitravelplanner-cgbcs3jvqusfwjrd8u84sa.streamlit.app/)

---

## Overview

**AI Travel Planner** combines real-time stay discovery with intelligent travel planning heuristics. Travelers specify their destination, travel dates, party size, budget, and vibe interests. The platform queries Booking.com's live inventory, filters and ranks accommodations based on budget fit and interest alignment, recommends tailored travel packages, organizes preparation checklists, and computes an interactive Travel Readiness Score.

---

## Key Features

- **🏨 Booking.com Demand API Integration:**
  - Backend-only integration via dedicated [`booking_service.py`](file:///c:/Users/SINDHU%20SURAJ/source/repos/AITravelPlanner/booking_service.py) service module.
  - Resolves destination locations via `/common/autocomplete`.
  - Searches stay inventory via `/accommodations/search`.
  - Enriches property photos, names, and accommodation types via `/accommodations/details`.
  - Scores and ranks accommodations according to budget fit, theme keywords, and review scores.
  - Deep-linked "View Availability" CTA buttons connecting travelers directly to Booking.com with affiliate attribution.

- **🔒 Secure Credential Management:**
  - API credentials are read strictly from backend environment variables:
    - `BOOKING_API_TOKEN`
    - `BOOKING_AFFILIATE_ID`
    - *(Optional)* `BOOKING_API_BASE_URL` (defaults to `https://demandapi.booking.com/3.2`)
  - Supported also via Streamlit secrets (`.streamlit/secrets.toml`).
  - No credentials, tokens, or affiliate secrets are ever exposed in client responses or the UI.

- **🛡️ Resilient Demo Mode & Graceful Fallback:**
  - When API credentials are not configured, the app runs in **Demo Mode**, generating realistic, curated property recommendations tailored to the destination and budget.
  - If live API requests encounter authentication limits, timeouts, or empty inventory, it issues a friendly notification and displays curated preview options without interrupting the planning flow.
  - Always retains the core rule-based travel package recommendations.

- **📝 Comprehensive Journey Parameters:**
  - **Destination:** Any city, region, or country.
  - **Check-in Date:** Future departure date.
  - **Check-out Date:** Departure date validation ensuring stay duration >= 1 night.
  - **Adults & Rooms:** Party size specification with room-to-adult ratio validation.
  - **Budget (INR):** Total financial allocation.
  - **Travel Type:** Solo, Couple, Family, Business.
  - **Interests:** Beach, Nature, Adventure.

- **📊 Algorithmic Intelligence & Planning Analytics:**
  - **Budget Categorization:** Low (< ₹10k), Medium (₹10k–₹30k), Premium (₹30k–₹60k), Luxury (> ₹60k).
  - **Targeted Packages:** Backpacking, Romantic Getaway, Family-Friendly Resort, Corporate Facilities.
  - **Interactive Checklist:** Essential departure items with real-time packing progress counter.
  - **Travel Readiness Score (out of 100):** Weighted algorithmic readiness score with breakdown.
  - **Exportable Briefing Dossier:** One-click copyable itinerary summary including recommended accommodations.

---

## Project Structure

```text
AITravelPlanner/
├── .streamlit/
│   ├── config.toml           # Streamlit theme and UI styles
│   └── secrets.toml          # Optional local secrets (git-ignored)
├── app.py                    # Main Streamlit application and UI cards
├── booking_service.py        # Booking.com Demand API integration module
├── requirements.txt          # Python dependencies (streamlit, requests)
├── .gitignore                # Git ignore rules protecting credentials
└── README.md                 # Project documentation
```

---

## Installation & Running Locally

### 1. Prerequisites
- Python 3.9+
- Pip package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Booking.com Demand API Credentials
To activate live Booking.com inventory, set your environment variables:

**On Windows (PowerShell):**
```powershell
$env:BOOKING_API_TOKEN="your_booking_api_bearer_token"
$env:BOOKING_AFFILIATE_ID="your_affiliate_id"
```

**On Linux/macOS:**
```bash
export BOOKING_API_TOKEN="your_booking_api_bearer_token"
export BOOKING_AFFILIATE_ID="your_affiliate_id"
```

> **Note:** If no credentials are provided, the app automatically runs in **Demo Mode**, allowing complete feature testing without API keys!

### 4. Launch Application
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.
