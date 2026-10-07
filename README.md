# AI Travel Planner ✈️

A modern, responsive single-page travel planning web application built with Python and Streamlit.

🌐 **Live Application:** [https://aitravelplanner-cgbcs3jvqusfwjrd8u84sa.streamlit.app/](https://aitravelplanner-cgbcs3jvqusfwjrd8u84sa.streamlit.app/)

## Overview

**AI Travel Planner** helps travelers configure itineraries and calculate customized recommendations without requiring any external APIs. It implements pure algorithmic logic in Python to categorize budgets, recommend specialized packages, organize preparation checklists, and compute a dynamic Travel Readiness Score.

---

## Features

- **Intuitive Single-Page Interface:**
  - Modern travel-themed UI with deep azure blues, vibrant teals, and warm amber accents.
  - Responsive layouts, card containers, and typography.
  - Interactive inputs for Destination, Travel Date, Budget (INR), Travel Type, and Multiselect Interests.

- **Robust Pre-Generation Validation:**
  - Validates that Destination is not empty.
  - Validates that a valid Travel Date is selected.
  - Validates that Budget is greater than zero.
  - Ensures at least one interest is selected.
  - Displays friendly, distinct alert warnings for missing or invalid parameters.

- **Conditional Budget Categorization:**
  - **Low Budget:** Below ₹10,000
  - **Medium Budget:** ₹10,000 to ₹30,000
  - **Premium Budget:** ₹30,000 to ₹60,000
  - **Luxury Budget:** Above ₹60,000

- **Targeted Package Recommendations:**
  - **Solo:** Backpacking & Exploration
  - **Family:** Family-Friendly Resort Package
  - **Couple:** Romantic Getaway Package
  - **Business:** Corporate Hotel & Meeting Facilities

- **Loop-Driven Interest Cards:**
  - Iterates over selected interests (`Beach`, `Nature`, `Adventure`) to display individual highlight cards, activity focus, and packing recommendations.

- **Loop-Generated Preparation Checklist:**
  - Generates essential travel preparation items stored in Python lists:
    - Passport / ID
    - Flight Tickets
    - Hotel Booking Confirmation
    - Mobile Charger
    - Medicines
  - Real-time packing progress counter.

- **Travel Readiness Score (out of 100):**
  - **+25 points** if budget > ₹30,000
  - **+25 points** if travel type is Family or Couple
  - **+15 points** for each selected interest
  - Capped at **100 points maximum**
  - Displayed prominently with an animated progress bar and detailed breakdown.

- **Exportable Travel Briefing:**
  - Generates a quick text summary dossier that users can copy for their records.

---

## Installation & Running Locally

### Prerequisites
- Python 3.9+
- Streamlit (`pip install streamlit`)

### Launch Application
From this project directory, run:
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Project Structure

```text
AITravelPlanner/
├── .streamlit/
│   └── config.toml       # Streamlit theme and server configuration
├── app.py                # Main Streamlit application logic and UI
└── README.md             # Project documentation and guide
```
