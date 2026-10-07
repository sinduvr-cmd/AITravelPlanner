"""
AI Travel Planner
=================
A modern, responsive single-page travel planning tool built with Streamlit.
Provides live accommodation recommendations via Booking.com Demand API (with seamless
Demo Mode fallback), algorithmic package recommendations, budget categorization,
custom travel checklists, and travel readiness scoring.
"""

import datetime
import streamlit as st
import booking_service

# Configure page settings
st.set_page_config(
    page_title="AI Travel Planner • Live Booking.com Stays",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Travel-inspired palette: Azure Blue, Deep Navy, Vibrant Teal, and Sunset Coral/Warm Amber)
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container background and spacing */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1240px;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #0369a1 50%, #0d9488 100%);
        border-radius: 20px;
        padding: 2.2rem 2.4rem;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.25), 0 8px 10px -6px rgba(13, 148, 136, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.12);
        position: relative;
        overflow: hidden;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.15;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #e2e8f0;
        margin-top: 0.6rem;
        margin-bottom: 0;
        font-weight: 400;
        max-width: 760px;
        line-height: 1.5;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(8px);
        padding: 0.25rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.8rem;
    }

    /* Card styling */
    .planner-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.6rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .planner-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    }

    .card-header-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .card-header-desc {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 1.2rem;
    }

    /* Metric pill and highlights */
    .highlight-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-weight: 600;
    }

    .badge-budget-low {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }

    .badge-budget-medium {
        background-color: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }

    .badge-budget-premium {
        background-color: #ccfbf1;
        color: #0f766e;
        border: 1px solid #99f6e4;
    }

    .badge-budget-luxury {
        background-color: #fdf4ff;
        color: #86198f;
        border: 1px solid #f5d0fe;
    }

    /* Accommodation Card Aesthetics */
    .accomm-card {
        background: #ffffff;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.08), 0 3px 6px -2px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        height: 100%;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease;
        position: relative;
    }

    .accomm-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 10px 10px -5px rgba(15, 23, 42, 0.05);
        border-color: #38bdf8;
    }

    .accomm-image-wrap {
        position: relative;
        width: 100%;
        height: 195px;
        overflow: hidden;
        background-color: #0f172a;
    }

    .accomm-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        transition: transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .accomm-card:hover .accomm-image {
        transform: scale(1.05);
    }

    .accomm-type-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        background: rgba(15, 23, 42, 0.82);
        backdrop-filter: blur(8px);
        color: #f8fafc;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.3rem 0.7rem;
        border-radius: 9999px;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    .accomm-score-badge {
        position: absolute;
        bottom: 12px;
        right: 12px;
        background: #0284c7;
        color: #ffffff;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 0.25rem 0.65rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }

    .accomm-body {
        padding: 1.25rem 1.3rem 1.35rem 1.3rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        justify-content: space-between;
    }

    .accomm-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.32;
        margin: 0 0 0.45rem 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.9rem;
    }

    .accomm-meta-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.84rem;
        color: #64748b;
        margin-bottom: 1rem;
    }

    .accomm-price-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.1rem;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }

    .accomm-price-label {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
    }

    .accomm-price-value {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0369a1;
    }

    .accomm-btn-link {
        display: block;
        width: 100%;
        text-align: center;
        background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%);
        color: #ffffff !important;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 0.94rem;
        padding: 0.72rem 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
        transition: all 0.2s ease;
    }

    .accomm-btn-link:hover {
        background: linear-gradient(135deg, #0369a1 0%, #0f766e 100%);
        box-shadow: 0 6px 14px rgba(2, 132, 199, 0.4);
        transform: translateY(-1px);
        color: #ffffff !important;
        text-decoration: none !important;
    }

    /* Readiness score box */
    .readiness-container {
        background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }

    .readiness-score-number {
        font-size: 3rem;
        font-weight: 800;
        color: #0284c7;
        line-height: 1;
        margin-bottom: 0.3rem;
    }

    .readiness-score-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        font-weight: 600;
    }

    .package-spotlight {
        background: linear-gradient(135deg, #0369a1 0%, #0d9488 100%);
        border-radius: 16px;
        color: #ffffff;
        padding: 1.4rem;
        margin-top: 1rem;
    }

    .package-spotlight-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    /* Primary button aesthetic override */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.32);
        transition: all 0.25s ease;
        width: 100%;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #0369a1 0%, #0f766e 100%);
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.48);
        transform: translateY(-1px);
        color: #ffffff;
    }

    /* Sidebar info card */
    .sidebar-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.86rem;
        color: #475569;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# Helper Functions with Clear Validation & Business Logic
# ==============================================================================

def validate_planner_inputs(
    destination: str,
    checkin_date: datetime.date,
    checkout_date: datetime.date,
    budget: float,
    adults: int,
    rooms: int,
    interests: list
):
    """
    Validates form inputs before plan generation.
    Returns a list of friendly warning error messages.
    """
    validation_errors = []

    # Validation: Destination cannot be empty
    if not destination or not destination.strip():
        validation_errors.append("Destination cannot be empty. Please enter where you want to travel.")

    # Validation: Check-in date must be selected and not in the past
    if checkin_date is None:
        validation_errors.append("Check-in date must be selected.")
    elif checkin_date < datetime.date.today():
        validation_errors.append("Check-in date cannot be in the past.")

    # Validation: Check-out date must be selected and after check-in date
    if checkout_date is None:
        validation_errors.append("Check-out date must be selected.")
    elif checkin_date and checkout_date <= checkin_date:
        validation_errors.append("Check-out date must be at least one day after the check-in date.")

    # Validation: Budget must be greater than zero
    if budget is None or budget <= 0:
        validation_errors.append("Budget must be greater than zero. Please specify a valid amount in INR.")

    # Validation: Number of adults must be at least 1
    if adults is None or adults < 1:
        validation_errors.append("Number of adults must be at least 1.")

    # Validation: Number of rooms must be at least 1
    if rooms is None or rooms < 1:
        validation_errors.append("Number of rooms must be at least 1.")

    # Validation: Rooms cannot unreasonably exceed adult count
    if adults and rooms and rooms > adults:
        validation_errors.append("Number of rooms cannot exceed the number of adult travelers.")

    # Validation: At least one interest must be selected
    if not interests or len(interests) == 0:
        validation_errors.append("At least one interest must be selected (Beach, Nature, or Adventure).")

    return validation_errors


def categorize_budget(budget_amount: float):
    """
    Categorizes budget using conditional logic (if-elif-else).
    - Below ₹10,000: Low Budget
    - ₹10,000 to ₹30,000: Medium Budget
    - ₹30,000 to ₹60,000: Premium Budget
    - Above ₹60,000: Luxury Budget
    """
    if budget_amount < 10000:
        category = "Low Budget"
        badge_class = "badge-budget-low"
        icon = "🪙"
        description = "Ideal for budget hostels, public transit, and local street exploration."
    elif budget_amount <= 30000:
        category = "Medium Budget"
        badge_class = "badge-budget-medium"
        icon = "💳"
        description = "Balanced comfort with boutique stays, regional cuisine, and guided day tours."
    elif budget_amount <= 60000:
        category = "Premium Budget"
        badge_class = "badge-budget-premium"
        icon = "✨"
        description = "Elevated journey with 4-star hotels, curated dining, and private transfers."
    else:
        category = "Luxury Budget"
        badge_class = "badge-budget-luxury"
        icon = "💎"
        description = "First-class indulgence featuring 5-star resorts, private excursions, and bespoke concierge."

    return category, badge_class, icon, description


def recommend_package_by_travel_type(travel_type: str):
    """
    Recommends a package based on the selected travel type using conditional logic (if-elif-else).
    - Solo: Backpacking & Exploration
    - Family: Family-Friendly Resort Package
    - Couple: Romantic Getaway Package
    - Business: Corporate Hotel & Meeting Facilities
    """
    if travel_type == "Solo":
        package_name = "Backpacking & Exploration"
        package_icon = "🎒"
        package_perk = "Includes walking routes, social hubs, local experiences, and solo traveler safety pointers."
    elif travel_type == "Family":
        package_name = "Family-Friendly Resort Package"
        package_icon = "👨‍👩‍👧‍👦"
        package_perk = "Includes child-friendly recreation, spacious resort suites, leisure pools, and group dining options."
    elif travel_type == "Couple":
        package_name = "Romantic Getaway Package"
        package_icon = "💑"
        package_perk = "Features scenic viewpoints, candlelit dining venues, serene hideaways, and private sunset tours."
    elif travel_type == "Business":
        package_name = "Corporate Hotel & Meeting Facilities"
        package_icon = "💼"
        package_perk = "Features high-speed fiber internet, executive club access, ergonomic workspaces, and airport shuttle."
    else:
        package_name = "Custom Travel Package"
        package_icon = "🗺️"
        package_perk = "Tailored itinerary adjusted to standard traveler preferences."

    return package_name, package_icon, package_perk


def calculate_travel_readiness_score(budget: float, travel_type: str, interests: list):
    """
    Calculates the Travel Readiness Score out of 100 based on the rules:
    - Add 25 points if budget is above ₹30,000.
    - Add 25 points if travel type is Family or Couple.
    - Add 15 points for each selected interest.
    - Cap the score at 100.
    """
    score = 0
    breakdown = []

    # Rule 1: Add 25 points if budget is above ₹30,000
    if budget > 30000:
        score += 25
        breakdown.append(("Budget Buffer (> ₹30,000)", 25))
    else:
        breakdown.append(("Budget Buffer (<= ₹30,000)", 0))

    # Rule 2: Add 25 points if travel type is Family or Couple
    if travel_type in ["Family", "Couple"]:
        score += 25
        breakdown.append((f"Travel Type Bonus ({travel_type})", 25))
    else:
        breakdown.append((f"Travel Type Bonus ({travel_type})", 0))

    # Rule 3: Add 15 points for each selected interest using a loop
    interest_points = 0
    for _ in interests:
        interest_points += 15

    score += interest_points
    breakdown.append((f"Selected Interests ({len(interests)} x 15 pts)", interest_points))

    # Rule 4: Cap the score at 100
    capped_score = min(100, score)

    return capped_score, score, breakdown


# Predefined master list of checklist items stored in a Python list
DEFAULT_TRAVEL_CHECKLIST = [
    "Passport / ID",
    "Flight Tickets",
    "Hotel Booking Confirmation",
    "Mobile Charger",
    "Medicines"
]

# Predefined master list of available interests stored in a Python list
AVAILABLE_INTERESTS = [
    "Beach",
    "Nature",
    "Adventure"
]

# Interest metadata dictionary for enhanced presentation
INTEREST_DETAILS = {
    "Beach": {
        "icon": "🏖️",
        "highlight": "Coastal relaxation, sea breezes, water activities, and seaside dining.",
        "tips": "Carry reef-safe sunscreen, polarized sunglasses, and breathable swimwear."
    },
    "Nature": {
        "icon": "🌲",
        "highlight": "National parks, serene walking trails, lush flora, and birdwatching.",
        "tips": "Pack insect repellent, binoculars, reusable water bottles, and lightweight rain gear."
    },
    "Adventure": {
        "icon": "🧗",
        "highlight": "Trekking, water sports, rugged outdoor terrain, and adrenaline rush.",
        "tips": "Wear sturdy grip shoes, bring a compact first aid pouch, and review safety guidelines."
    }
}


# ==============================================================================
# Main Application Layout
# ==============================================================================

# Hero Title & Subtitle Banner
st.markdown(
    """
    <div class="hero-container">
        <span class="hero-tag">✈️ Smart Travel Assistant • Booking.com Demand API</span>
        <h1 class="hero-title">AI Travel Planner</h1>
        <p class="hero-subtitle">
            Configure your destination, stay dates, party size, and budget to receive live accommodation options
            via Booking.com Demand API, algorithmic package recommendations, and your travel readiness score.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar with application context & quick guide
with st.sidebar:
    st.markdown("### 🧭 Planner Guide")
    st.markdown(
        """
        Welcome to **AI Travel Planner**! Follow these quick steps to generate your personalized itinerary summary:

        1. **Destination:** Enter your chosen destination.
        2. **Stay Dates:** Pick your Check-in and Check-out dates.
        3. **Guests & Rooms:** Specify number of adults and rooms.
        4. **Budget:** Enter your planned budget in INR (₹).
        5. **Travel Style:** Choose your party type.
        6. **Interests:** Pick one or more interests.
        7. Click **Generate Travel Plan** for live accommodations and analytics!
        """
    )

    st.markdown("---")
    st.markdown("#### 🏨 Booking.com API Status")
    
    api_is_live = booking_service.is_booking_api_configured()
    if api_is_live:
        st.markdown(
            """
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.86rem; font-weight: 600;">
                🟢 Live Connected (Demand API v3.2)
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Authenticated securely using backend environment credentials.")
    else:
        st.markdown(
            """
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.86rem; font-weight: 600;">
                ℹ️ Demo Mode (Simulated Live)
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.expander("🔑 How to connect Live API", expanded=False):
            st.caption(
                "Set the following environment variables in your server environment:\n"
                "- `BOOKING_API_TOKEN`\n"
                "- `BOOKING_AFFILIATE_ID`\n\n"
                "Credentials are never exposed to the frontend or user interface."
            )

    st.markdown("---")
    st.markdown("#### 💡 Budget Tier Reference")
    st.markdown(
        """
        - **Low:** < ₹10,000
        - **Medium:** ₹10,000 – ₹30,000
        - **Premium:** ₹30,000 – ₹60,000
        - **Luxury:** > ₹60,000
        """
    )

    st.markdown("---")
    st.markdown("#### 📊 Readiness Formula")
    st.markdown(
        """
        - **+25 pts:** Budget > ₹30,000
        - **+25 pts:** Family or Couple trip
        - **+15 pts:** Each chosen interest
        - *Capped at 100 points maximum.*
        """
    )


# ==============================================================================
# Input Collection Area
# ==============================================================================

st.markdown(
    """
    <div class="planner-card">
        <div class="card-header-title">📝 Plan Your Next Getaway</div>
        <div class="card-header-desc">Enter your journey details below to fetch accommodation inventory and calculate recommendations.</div>
    </div>
    """,
    unsafe_allow_html=True
)

today = datetime.date.today()
default_checkin = today + datetime.timedelta(days=14)
default_checkout = default_checkin + datetime.timedelta(days=4)

# Form grid layout: Row 1 (Destination, Check-in Date, Check-out Date)
col_dest, col_checkin, col_checkout = st.columns([1.5, 1, 1])

with col_dest:
    destination_input = st.text_input(
        "📍 Destination",
        value=st.session_state.get("saved_destination", "Goa"),
        placeholder="e.g. Goa, Manali, Paris, Bali, Tokyo...",
        help="Enter the city, state, or country you intend to visit."
    )

with col_checkin:
    checkin_date_input = st.date_input(
        "📅 Check-in Date",
        value=st.session_state.get("saved_checkin", default_checkin),
        min_value=today,
        help="Select your scheduled arrival / check-in date."
    )

with col_checkout:
    min_checkout = (checkin_date_input + datetime.timedelta(days=1)) if checkin_date_input else (today + datetime.timedelta(days=1))
    saved_checkout = st.session_state.get("saved_checkout", default_checkout)
    checkout_initial = saved_checkout if saved_checkout >= min_checkout else min_checkout

    checkout_date_input = st.date_input(
        "🏁 Check-out Date",
        value=checkout_initial,
        min_value=min_checkout,
        help="Select your scheduled departure / check-out date."
    )

# Form grid layout: Row 2 (Budget, Travel Type, Adults, Rooms)
col_budget, col_type, col_adults, col_rooms = st.columns([1.2, 1, 0.9, 0.9])

with col_budget:
    budget_input = st.number_input(
        "💰 Budget (in ₹ INR)",
        min_value=0,
        max_value=10000000,
        value=st.session_state.get("saved_budget", 35000),
        step=5000,
        help="Enter your total estimated travel budget in Indian Rupees."
    )

with col_type:
    travel_type_options = ["Solo", "Family", "Couple", "Business"]
    current_saved_type = st.session_state.get("saved_type", "Couple")
    type_idx = travel_type_options.index(current_saved_type) if current_saved_type in travel_type_options else 0
    travel_type_input = st.selectbox(
        "👥 Travel Type",
        options=travel_type_options,
        index=type_idx,
        help="Choose who you are traveling with."
    )

with col_adults:
    default_adults = 2 if travel_type_input in ["Family", "Couple"] else 1
    adults_input = st.number_input(
        "🧑 Adults",
        min_value=1,
        max_value=30,
        value=st.session_state.get("saved_adults", default_adults),
        step=1,
        help="Number of adult guests (18+)."
    )

with col_rooms:
    rooms_input = st.number_input(
        "🚪 Rooms",
        min_value=1,
        max_value=15,
        value=st.session_state.get("saved_rooms", 1),
        step=1,
        help="Number of accommodation rooms required."
    )

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Multiselect for interests (using predefined Python list)
selected_interests_input = st.multiselect(
    "🎯 Interests (Select at least one)",
    options=AVAILABLE_INTERESTS,
    default=st.session_state.get("saved_interests", ["Beach", "Nature"]),
    help="Pick the travel vibes and themes you wish to experience."
)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Generate Action Button
generate_clicked = st.button("🚀 Generate Travel Plan", use_container_width=True)

# Process form submission
if generate_clicked:
    # 1. Validate inputs
    errors = validate_planner_inputs(
        destination=destination_input,
        checkin_date=checkin_date_input,
        checkout_date=checkout_date_input,
        budget=budget_input,
        adults=adults_input,
        rooms=rooms_input,
        interests=selected_interests_input
    )

    st.session_state["has_run_planner"] = True
    st.session_state["validation_errors"] = errors
    st.session_state["saved_destination"] = destination_input
    st.session_state["saved_checkin"] = checkin_date_input
    st.session_state["saved_checkout"] = checkout_date_input
    st.session_state["saved_budget"] = budget_input
    st.session_state["saved_type"] = travel_type_input
    st.session_state["saved_adults"] = adults_input
    st.session_state["saved_rooms"] = rooms_input
    st.session_state["saved_interests"] = selected_interests_input

    # 2. Fetch accommodations using Booking.com Demand API (with loading spinner)
    if not errors:
        with st.spinner(f"🔍 Searching Booking.com Demand API for live accommodations in {destination_input}..."):
            accomm_data = booking_service.get_recommended_accommodations(
                destination=destination_input,
                checkin_date=checkin_date_input,
                checkout_date=checkout_date_input,
                number_of_adults=adults_input,
                number_of_rooms=rooms_input,
                budget=budget_input,
                interests=selected_interests_input
            )
            st.session_state["saved_accommodations"] = accomm_data


# ==============================================================================
# Validation & Results Presentation Area
# ==============================================================================

if st.session_state.get("has_run_planner", False):
    current_destination = st.session_state.get("saved_destination", "")
    current_checkin = st.session_state.get("saved_checkin", today)
    current_checkout = st.session_state.get("saved_checkout", today + datetime.timedelta(days=4))
    current_budget = st.session_state.get("saved_budget", 0)
    current_type = st.session_state.get("saved_type", "Solo")
    current_adults = st.session_state.get("saved_adults", 1)
    current_rooms = st.session_state.get("saved_rooms", 1)
    current_interests = st.session_state.get("saved_interests", [])
    validation_errors = st.session_state.get("validation_errors", [])

    if len(validation_errors) > 0:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.error("⚠️ **Please resolve the following input requirements to generate your plan:**")
        # Loop through validation error messages
        for error_message in validation_errors:
            st.warning(f"• {error_message}")
    else:
        # ----------------------------------------------------------------------
        # All validations passed: Perform logic calculations
        # ----------------------------------------------------------------------
        budget_category, budget_badge_class, budget_icon, budget_desc = categorize_budget(current_budget)
        package_name, package_icon, package_perk = recommend_package_by_travel_type(current_type)
        final_readiness_score, raw_score, score_breakdown = calculate_travel_readiness_score(
            budget=current_budget,
            travel_type=current_type,
            interests=current_interests
        )

        stay_nights = max(1, (current_checkout - current_checkin).days)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.success("🎉 **Travel Plan Successfully Generated!** Review your personalized briefing below.")

        # ======================================================================
        # Section 1: Travel Summary Overview & Readiness Score
        # ======================================================================
        st.markdown("### 📋 Travel Summary")

        summary_col1, summary_col2 = st.columns([1.5, 1])

        with summary_col1:
            checkin_formatted = current_checkin.strftime("%b %d, %Y") if current_checkin else "Not specified"
            checkout_formatted = current_checkout.strftime("%b %d, %Y") if current_checkout else "Not specified"
            formatted_budget = f"₹{current_budget:,.2f}"

            summary_card_html = f"""
            <div class="planner-card">
                <div class="card-header-title">🌍 Trip Overview</div>
                <div class="card-header-desc">Essential parameters registered for this travel itinerary.</div>
                <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.55rem 0; color: #64748b; font-weight: 500;">Destination</td>
                        <td style="padding: 0.55rem 0; font-weight: 700; color: #0f172a; text-align: right;">📍 {current_destination}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.55rem 0; color: #64748b; font-weight: 500;">Dates & Duration</td>
                        <td style="padding: 0.55rem 0; font-weight: 600; color: #0f172a; text-align: right;">
                            📅 {checkin_formatted} – {checkout_formatted} ({stay_nights} Night{'s' if stay_nights > 1 else ''})
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.55rem 0; color: #64748b; font-weight: 500;">Travel Party</td>
                        <td style="padding: 0.55rem 0; font-weight: 600; color: #0f172a; text-align: right;">
                            👥 {current_adults} Adult{'s' if current_adults > 1 else ''}, {current_rooms} Room{'s' if current_rooms > 1 else ''} ({current_type})
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.55rem 0; color: #64748b; font-weight: 500;">Allocated Budget</td>
                        <td style="padding: 0.55rem 0; font-weight: 700; color: #0369a1; text-align: right;">{formatted_budget}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.55rem 0; color: #64748b; font-weight: 500;">Budget Category</td>
                        <td style="padding: 0.55rem 0; text-align: right;">
                            <span class="highlight-badge {budget_badge_class}">{budget_icon} {budget_category}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0.55rem 0; color: #64748b; font-weight: 500;">Package Recommendation</td>
                        <td style="padding: 0.55rem 0; font-weight: 700; color: #0d9488; text-align: right;">{package_icon} {package_name}</td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(summary_card_html, unsafe_allow_html=True)

        with summary_col2:
            # Travel Readiness Score Presentation
            st.markdown(
                f"""
                <div class="planner-card readiness-container">
                    <div class="readiness-score-label">Travel Readiness Score</div>
                    <div class="readiness-score-number">{final_readiness_score} <span style="font-size: 1.3rem; color: #64748b;">/ 100</span></div>
                    <div style="font-size: 0.88rem; color: #475569; margin-bottom: 1rem;">
                        {"🟢 Excellent Preparation!" if final_readiness_score >= 75 else "🟡 Good Readiness!" if final_readiness_score >= 50 else "🟠 Moderate Readiness"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Prominent Streamlit Progress Bar
            progress_ratio = final_readiness_score / 100.0
            st.progress(progress_ratio)

            # Detailed score points breakdown
            with st.expander("🔍 View Score Calculation Breakdown", expanded=False):
                st.caption("Score components evaluated:")
                for rule_name, rule_points in score_breakdown:
                    st.write(f"- **{rule_name}:** +{rule_points} pts")
                if raw_score > 100:
                    st.info(f"Raw calculated points: {raw_score} pts (capped at maximum 100).")

        # ======================================================================
        # Section 2: Booking.com Accommodation Recommendations
        # ======================================================================
        st.markdown("### 🏨 Recommended Stays via Booking.com Demand API")

        accomm_response = st.session_state.get("saved_accommodations")
        if not accomm_response:
            # Auto-retrieve if not already in session state
            accomm_response = booking_service.get_recommended_accommodations(
                destination=current_destination,
                checkin_date=current_checkin,
                checkout_date=current_checkout,
                number_of_adults=current_adults,
                number_of_rooms=current_rooms,
                budget=current_budget,
                interests=current_interests
            )
            st.session_state["saved_accommodations"] = accomm_response

        accomm_results = accomm_response.get("results", []) if isinstance(accomm_response, dict) else []
        accomm_mode = accomm_response.get("mode", "demo")
        accomm_msg = accomm_response.get("message", "")

        # Graceful status notice depending on execution mode
        if accomm_mode == "live":
            st.success(f"🟢 **Live Booking.com Demand API:** Live inventory and rates retrieved for {current_destination}.")
        elif accomm_mode == "fallback":
            st.info(f"💡 **Booking.com Notice:** {accomm_msg}")
        else:
            st.info(
                f"💡 **Demo Mode Active:** Booking.com Demand API credentials (`BOOKING_API_TOKEN` & `BOOKING_AFFILIATE_ID`) "
                f"are not configured in environment. Displaying simulated live preview recommendations tailored to {current_destination}."
            )

        if accomm_results:
            st.caption(
                f"Showing the best 3 accommodation options ranked for your **{budget_category}** budget (₹{current_budget:,}) "
                f"and selected interests (**{', '.join(current_interests)}**):"
            )

            col_a, col_b, col_c = st.columns(3)
            card_cols = [col_a, col_b, col_c]

            for idx, prop in enumerate(accomm_results[:3]):
                with card_cols[idx]:
                    prop_name = prop.get("name", f"Stay in {current_destination}")
                    prop_type = prop.get("accommodation_type", "Hotel")
                    review_score = prop.get("review_score")
                    review_label = prop.get("review_label", "")
                    price_formatted = prop.get("formatted_price", f"₹{prop.get('price', 0):,.0f}")
                    currency_code = prop.get("currency", "INR")
                    image_url = prop.get("image_url", "")
                    booking_url = prop.get("booking_url", "#")

                    score_html = f"★ {review_score:.1f}" if review_score is not None else "★ Recommended"
                    label_html = f"<span style='font-size: 0.72rem; font-weight: 500; opacity: 0.9;'>{review_label}</span>" if review_label else ""

                    card_html = f"""
                    <div class="accomm-card">
                        <div class="accomm-image-wrap">
                            <img class="accomm-image" src="{image_url}" alt="{prop_name}" loading="lazy" />
                            <span class="accomm-type-badge">{prop_type}</span>
                            <span class="accomm-score-badge">{score_html} {label_html}</span>
                        </div>
                        <div class="accomm-body">
                            <div>
                                <div class="accomm-title" title="{prop_name}">{prop_name}</div>
                                <div class="accomm-meta-row">
                                    <span>📍 {current_destination}</span>
                                    <span style="font-weight: 600; color: #0284c7;">{stay_nights} Night{'s' if stay_nights > 1 else ''} • {current_rooms} Rm</span>
                                </div>
                            </div>
                            <div>
                                <div class="accomm-price-section">
                                    <div>
                                        <div class="accomm-price-label">Total for stay ({current_adults} Adults)</div>
                                        <div class="accomm-price-value">{price_formatted}</div>
                                    </div>
                                    <span style="font-size: 0.78rem; color: #0d9488; font-weight: 700; background: #f0fdfa; padding: 0.2rem 0.5rem; border-radius: 6px;">
                                        {currency_code}
                                    </span>
                                </div>
                                <a href="{booking_url}" target="_blank" rel="noopener noreferrer" class="accomm-btn-link">
                                    View Availability ↗
                                </a>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning("No accommodation inventory returned for the requested parameters.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # ======================================================================
        # Section 3: Package Recommendation Spotlight (Retained Rule-based Package)
        # ======================================================================
        st.markdown("### 🎁 Recommended Travel Package")

        package_banner_html = f"""
        <div class="package-spotlight">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9;">Tailored for {current_type} Travel</div>
            <div class="package-spotlight-title">{package_icon} {package_name}</div>
            <p style="margin: 0.4rem 0 0.8rem 0; font-size: 0.96rem; line-height: 1.5; opacity: 0.95;">
                {package_perk}
            </p>
            <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 0.6rem 0.9rem; font-size: 0.86rem;">
                <strong>Budget Alignment:</strong> Matched with your <em>{budget_category}</em> ({budget_desc})
            </div>
        </div>
        """
        st.markdown(package_banner_html, unsafe_allow_html=True)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # ======================================================================
        # Section 4: Selected Interests (Displayed Individually via Loop)
        # ======================================================================
        st.markdown("### 🎯 Selected Interests & Activities")
        st.write("Here is how your selected interests shape your travel experience:")

        # Loop through selected interests list
        interest_cols = st.columns(len(current_interests))
        for idx, interest_item in enumerate(current_interests):
            with interest_cols[idx]:
                details = INTEREST_DETAILS.get(
                    interest_item,
                    {"icon": "🌟", "highlight": "Customized exploration.", "tips": "Prepare adequately."}
                )
                interest_card_html = f"""
                <div class="planner-card" style="height: 100%;">
                    <div style="font-size: 1.8rem; margin-bottom: 0.4rem;">{details['icon']}</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem;">
                        {interest_item}
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-bottom: 0.75rem; line-height: 1.4;">
                        {details['highlight']}
                    </div>
                    <div style="font-size: 0.8rem; background: #f0fdfa; border: 1px solid #ccfbf1; color: #0f766e; padding: 0.5rem; border-radius: 8px;">
                        💡 <strong>Packing Tip:</strong> {details['tips']}
                    </div>
                </div>
                """
                st.markdown(interest_card_html, unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # ======================================================================
        # Section 5: Travel Checklist (Generated using a Loop)
        # ======================================================================
        st.markdown("### 🧳 Essential Travel Checklist")
        st.write("Ensure you have packed and verified all essential essentials before departure:")

        checklist_col_left, checklist_col_right = st.columns([1.3, 1])

        with checklist_col_left:
            st.markdown('<div class="planner-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header-title">✅ Departure Verification Items</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-header-desc">Tick off each item to confirm packing readiness:</div>', unsafe_allow_html=True)

            # Generate checklist items using a Python for-loop
            checked_count = 0
            for item_index, item_text in enumerate(DEFAULT_TRAVEL_CHECKLIST):
                item_key = f"chk_{item_index}_{item_text.replace(' ', '_')}"
                is_checked = st.checkbox(item_text, value=True, key=item_key)
                if is_checked:
                    checked_count += 1

            st.markdown('</div>', unsafe_allow_html=True)

        with checklist_col_right:
            completion_pct = int((checked_count / len(DEFAULT_TRAVEL_CHECKLIST)) * 100) if DEFAULT_TRAVEL_CHECKLIST else 0
            st.markdown(
                f"""
                <div class="planner-card">
                    <div class="card-header-title">📊 Packing Status</div>
                    <div style="margin: 1rem 0;">
                        <span style="font-size: 2.2rem; font-weight: 800; color: #0d9488;">{checked_count} / {len(DEFAULT_TRAVEL_CHECKLIST)}</span>
                        <span style="color: #64748b; font-size: 0.9rem; margin-left: 0.4rem;">items ready ({completion_pct}%)</span>
                    </div>
                    <p style="font-size: 0.86rem; color: #64748b;">
                        All travelers should keep physical and digital photocopies of critical documents in a secure pouch.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ======================================================================
        # Section 6: Itinerary Summary Dossier
        # ======================================================================
        st.markdown("---")
        with st.expander("📄 Exportable Travel Briefing Text", expanded=False):
            accomm_summary_lines = []
            for i, p in enumerate(accomm_results[:3], start=1):
                p_n = p.get('name', 'Stay')
                p_t = p.get('accommodation_type', 'Hotel')
                p_pr = p.get('formatted_price', '')
                p_sc = f"{p.get('review_score', '')}/10" if p.get('review_score') else "N/A"
                accomm_summary_lines.append(f"{i}. {p_n} ({p_t}) - {p_pr} [Rating: {p_sc}]")
            
            accomm_text = "\n".join(accomm_summary_lines) if accomm_summary_lines else "None selected."

            briefing_text = f"""AI TRAVEL PLANNER - TRIP DOSSIER
===================================
Destination: {current_destination}
Check-in: {checkin_formatted}
Check-out: {checkout_formatted} ({stay_nights} Nights)
Party Size: {current_adults} Adults, {current_rooms} Rooms ({current_type})
Budget: {formatted_budget} ({budget_category})
Recommended Package: {package_name}
Interests: {', '.join(current_interests)}
Readiness Score: {final_readiness_score}/100

RECOMMENDED ACCOMMODATIONS (BOOKING.COM):
{accomm_text}

CHECKLIST STATUS:
"""
            for chk in DEFAULT_TRAVEL_CHECKLIST:
                briefing_text += f" [x] {chk}\n"

            st.text_area("Copy your travel summary:", briefing_text, height=260)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.caption("AI Travel Planner • Built with Streamlit • Booking.com Demand API Integration")
