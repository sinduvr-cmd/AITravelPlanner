"""
AI Travel Planner
=================
A modern, responsive single-page travel planning tool built with Streamlit.
Provides algorithmic package recommendations, budget categorization,
custom travel checklists, and a readiness score calculation.
"""

import datetime
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="AI Travel Planner",
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
        padding-bottom: 3rem;
        max-width: 1200px;
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
        font-size: 1.1rem;
        color: #e2e8f0;
        margin-top: 0.6rem;
        margin-bottom: 0;
        font-weight: 400;
        max-width: 720px;
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

    /* Interest Card */
    .interest-pill {
        background: #f0fdfa;
        border: 1px solid #99f6e4;
        color: #0d9488;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .interest-pill-desc {
        font-size: 0.82rem;
        color: #0f766e;
        font-weight: 400;
        margin-top: 0.2rem;
    }

    /* Checklist Item Card */
    .checklist-row {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.95rem;
        color: #1e293b;
        font-weight: 500;
    }

    .checklist-icon {
        background: #0284c7;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        flex-shrink: 0;
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
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
        transition: all 0.25s ease;
        width: 100%;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #0369a1 0%, #0f766e 100%);
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45);
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
        font-size: 0.88rem;
        color: #475569;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# Helper Functions with Clear Conditional Logic and Loops
# ==============================================================================

def validate_planner_inputs(destination, travel_date, budget, interests):
    """
    Validates form inputs before plan generation.
    Returns a list of friendly warning error messages.
    """
    validation_errors = []

    # Validation: Destination cannot be empty
    if not destination or not destination.strip():
        validation_errors.append("Destination cannot be empty. Please enter where you want to travel.")

    # Validation: Travel date must be selected
    if travel_date is None:
        validation_errors.append("Travel date must be selected. Please choose a future travel date.")

    # Validation: Budget must be greater than zero
    if budget is None or budget <= 0:
        validation_errors.append("Budget must be greater than zero. Please specify a valid amount in INR.")

    # Validation: At least one interest must be selected
    if not interests or len(interests) == 0:
        validation_errors.append("At least one interest must be selected (Beach, Nature, or Adventure).")

    return validation_errors


def categorize_budget(budget_amount):
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


def recommend_package_by_travel_type(travel_type):
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


def calculate_travel_readiness_score(budget, travel_type, interests):
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
    if travel_type == "Family" or travel_type == "Couple":
        score += 25
        breakdown.append((f"Travel Type Bonus ({travel_type})", 25))
    else:
        breakdown.append((f"Travel Type Bonus ({travel_type})", 0))

    # Rule 3: Add 15 points for each selected interest using a loop
    interest_points = 0
    for interest_item in interests:
        interest_points += 15

    score += interest_points
    breakdown.append((f"Selected Interests ({len(interests)} x 15 pts)", interest_points))

    # Rule 4: Cap the score at 100
    if score > 100:
        capped_score = 100
    else:
        capped_score = score

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
        <span class="hero-tag">✈️ Smart Travel Assistant</span>
        <h1 class="hero-title">AI Travel Planner</h1>
        <p class="hero-subtitle">
            Configure your destination, budget, and travel preferences to generate instant package recommendations,
            budget analytics, preparation checklists, and your travel readiness score.
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
        2. **Date:** Pick your scheduled departure date.
        3. **Budget:** Enter your planned budget in INR (₹).
        4. **Travel Style:** Choose your party type.
        5. **Interests:** Pick one or more interests.
        6. Click **Generate Travel Plan** to view your comprehensive briefing!
        """
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
        <div class="card-header-desc">Enter your journey details below to calculate recommendations and preparation score.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Form grid layout for clean responsiveness
col_dest, col_date = st.columns([1.2, 1])
with col_dest:
    destination_input = st.text_input(
        "📍 Destination",
        placeholder="e.g. Goa, Manali, Paris, Bali, Tokyo...",
        help="Enter the city, state, or country you intend to visit."
    )

with col_date:
    today = datetime.date.today()
    default_travel_date = today + datetime.timedelta(days=14)
    travel_date_input = st.date_input(
        "📅 Travel Date",
        value=default_travel_date,
        min_value=today,
        help="Select your planned start date of travel."
    )

col_budget, col_type = st.columns([1, 1])
with col_budget:
    budget_input = st.number_input(
        "💰 Budget (in ₹ INR)",
        min_value=0,
        max_value=10000000,
        value=35000,
        step=5000,
        help="Enter your total estimated travel budget in Indian Rupees."
    )

with col_type:
    travel_type_options = ["Solo", "Family", "Couple", "Business"]
    travel_type_input = st.selectbox(
        "👥 Travel Type",
        options=travel_type_options,
        index=0,
        help="Choose who you are traveling with."
    )

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Multiselect for interests (using predefined Python list)
selected_interests_input = st.multiselect(
    "🎯 Interests (Select at least one)",
    options=AVAILABLE_INTERESTS,
    default=["Beach", "Nature"],
    help="Pick the travel vibes and themes you wish to experience."
)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Generate Action Button
generate_clicked = st.button("🚀 Generate Travel Plan", use_container_width=True)

# Maintain state so results remain visible during interactions
if generate_clicked:
    st.session_state["has_run_planner"] = True
    st.session_state["saved_destination"] = destination_input
    st.session_state["saved_date"] = travel_date_input
    st.session_state["saved_budget"] = budget_input
    st.session_state["saved_type"] = travel_type_input
    st.session_state["saved_interests"] = selected_interests_input

# ==============================================================================
# Validation & Results Presentation Area
# ==============================================================================

if st.session_state.get("has_run_planner", False):
    current_destination = st.session_state.get("saved_destination", "")
    current_date = st.session_state.get("saved_date", None)
    current_budget = st.session_state.get("saved_budget", 0)
    current_type = st.session_state.get("saved_type", "Solo")
    current_interests = st.session_state.get("saved_interests", [])

    # Validate inputs
    errors = validate_planner_inputs(
        destination=current_destination,
        travel_date=current_date,
        budget=current_budget,
        interests=current_interests
    )

    if len(errors) > 0:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.error("⚠️ **Please resolve the following input requirements to generate your plan:**")
        # Loop through validation error messages
        for error_message in errors:
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

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.success("🎉 **Travel Plan Successfully Generated!** Review your personalized briefing below.")

        # ======================================================================
        # Section 1: Travel Summary Overview & Readiness Score
        # ======================================================================
        st.markdown("### 📋 Travel Summary")

        summary_col1, summary_col2 = st.columns([1.5, 1])

        with summary_col1:
            formatted_date = current_date.strftime("%B %d, %Y") if current_date else "Not specified"
            formatted_budget = f"₹{current_budget:,.2f}"

            summary_card_html = f"""
            <div class="planner-card">
                <div class="card-header-title">🌍 Trip Overview</div>
                <div class="card-header-desc">Essential parameters registered for this travel itinerary.</div>
                <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.6rem 0; color: #64748b; font-weight: 500;">Destination</td>
                        <td style="padding: 0.6rem 0; font-weight: 700; color: #0f172a; text-align: right;">📍 {current_destination}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.6rem 0; color: #64748b; font-weight: 500;">Travel Date</td>
                        <td style="padding: 0.6rem 0; font-weight: 600; color: #0f172a; text-align: right;">📅 {formatted_date}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.6rem 0; color: #64748b; font-weight: 500;">Allocated Budget</td>
                        <td style="padding: 0.6rem 0; font-weight: 700; color: #0369a1; text-align: right;">{formatted_budget}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.6rem 0; color: #64748b; font-weight: 500;">Budget Category</td>
                        <td style="padding: 0.6rem 0; text-align: right;">
                            <span class="highlight-badge {budget_badge_class}">{budget_icon} {budget_category}</span>
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.6rem 0; color: #64748b; font-weight: 500;">Travel Type</td>
                        <td style="padding: 0.6rem 0; font-weight: 600; color: #0f172a; text-align: right;">👤 {current_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.6rem 0; color: #64748b; font-weight: 500;">Package Recommendation</td>
                        <td style="padding: 0.6rem 0; font-weight: 700; color: #0d9488; text-align: right;">{package_icon} {package_name}</td>
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
        # Section 2: Package Recommendation Spotlight
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
        # Section 3: Selected Interests (Displayed Individually via Loop)
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
        # Section 4: Travel Checklist (Generated using a Loop)
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
        # Section 5: Itinerary Summary Dossier
        # ======================================================================
        st.markdown("---")
        with st.expander("📄 Exportable Travel Briefing Text", expanded=False):
            briefing_text = f"""
AI TRAVEL PLANNER - TRIP DOSSIER
===================================
Destination: {current_destination}
Date of Departure: {formatted_date}
Budget: {formatted_budget} ({budget_category})
Travel Style: {current_type}
Recommended Package: {package_name}
Interests: {', '.join(current_interests)}
Readiness Score: {final_readiness_score}/100

CHECKLIST STATUS:
"""
            for chk in DEFAULT_TRAVEL_CHECKLIST:
                briefing_text += f" [x] {chk}\n"

            st.text_area("Copy your travel summary:", briefing_text, height=220)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.caption("AI Travel Planner • Built with Streamlit • Pure Python Algorithmic Intelligence")
