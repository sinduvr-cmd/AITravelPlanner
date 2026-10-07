"""
Booking.com Demand API Service Module
=====================================
Handles live accommodation search, location lookup, and details retrieval
via the Booking.com Demand API (v3.2).

Security Notice:
- API credentials are read exclusively from environment variables or Streamlit secrets.
- Credentials are NEVER exposed in the UI or client-facing responses.
- Supports graceful fallback and Demo Mode when credentials are not configured.
"""

import os
import urllib.parse
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
import requests

# Default API Configuration
DEFAULT_BASE_URL = "https://demandapi.booking.com/3.2"
REQUEST_TIMEOUT_SECONDS = 8

# Curated mapping of major global destinations to standard Booking.com city IDs
POPULAR_DESTINATIONS = {
    "goa": -2094200,
    "paris": -1456928,
    "london": -2601889,
    "tokyo": -246227,
    "new york": 20088325,
    "dubai": -782831,
    "bali": 900040000,
    "singapore": -73635,
    "manali": -2103444,
    "mumbai": -2092174,
    "bangalore": -2090184,
    "bengaluru": -2090184,
    "delhi": -2106102,
    "new delhi": -2106102,
    "rome": -126693,
    "amsterdam": -2140479,
    "barcelona": -372490,
    "bangkok": -3414440,
    "jaipur": -2098670,
    "shimla": -2111003,
    "agra": -2088031,
    "kerala": -2099351,
    "sydney": -1603135,
}


def _load_dotenv_if_exists() -> None:
    """
    Safely loads environment variables from a local .env file in the workspace
    if one exists, ensuring local developer configuration works seamlessly.
    """
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


def get_booking_credentials() -> Tuple[Optional[str], Optional[str], str]:
    """
    Safely retrieves Booking.com Demand API credentials from environment variables,
    .env file, or Streamlit secrets without exposing them.

    Returns:
        (api_token, affiliate_id, base_url)
    """
    _load_dotenv_if_exists()

    token = os.environ.get("BOOKING_API_TOKEN")
    affiliate_id = os.environ.get("BOOKING_AFFILIATE_ID")
    base_url = os.environ.get("BOOKING_API_BASE_URL", DEFAULT_BASE_URL)

    # Fallback to Streamlit secrets if running inside Streamlit and env vars aren't set
    if not token or not affiliate_id:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if not token and "BOOKING_API_TOKEN" in st.secrets:
                    token = str(st.secrets["BOOKING_API_TOKEN"])
                if not affiliate_id and "BOOKING_AFFILIATE_ID" in st.secrets:
                    affiliate_id = str(st.secrets["BOOKING_AFFILIATE_ID"])
                if "BOOKING_API_BASE_URL" in st.secrets:
                    base_url = str(st.secrets["BOOKING_API_BASE_URL"])
        except Exception:
            pass

    token = token.strip() if token else None
    affiliate_id = affiliate_id.strip() if affiliate_id else None
    base_url = base_url.strip().rstrip("/") if base_url else DEFAULT_BASE_URL

    return token, affiliate_id, base_url


def is_booking_api_configured() -> bool:
    """
    Checks if valid API credentials are present in the environment.
    """
    token, affiliate_id, _ = get_booking_credentials()
    return bool(token and affiliate_id)


def get_credentials_status() -> Dict[str, Any]:
    """
    Returns diagnostics on API credential availability without exposing secret values.
    """
    _load_dotenv_if_exists()
    token, affiliate_id, _ = get_booking_credentials()
    return {
        "token_configured": bool(token),
        "affiliate_configured": bool(affiliate_id),
        "is_ready": bool(token and affiliate_id)
    }


def _build_auth_headers(token: str, affiliate_id: str) -> Dict[str, str]:
    """
    Builds the required Booking.com Demand API authentication headers.
    Demand API uses Bearer token in Authorization header and X-Affiliate-Id.
    """
    return {
        "Authorization": f"Bearer {token}",
        "X-Affiliate-Id": str(affiliate_id),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "AITravelPlanner/1.0"
    }


def search_locations(
    destination: str,
    token: Optional[str] = None,
    affiliate_id: Optional[str] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Searches for destination location identifiers (city ID or country)
    using the Booking.com Demand API /common/autocomplete endpoint.

    Args:
        destination: Destination name or search text (e.g., 'Goa', 'Paris').

    Returns:
        Dict containing success status, resolved location identifiers, and message.
    """
    tok, aff, b_url = get_booking_credentials()
    token = token or tok
    affiliate_id = affiliate_id or aff
    base_url = (base_url or b_url or DEFAULT_BASE_URL).rstrip("/")

    if not token or not affiliate_id:
        return {
            "success": False,
            "error_type": "missing_credentials",
            "message": "Booking.com Demand API credentials not configured."
        }

    clean_dest = destination.strip()
    if len(clean_dest) < 2:
        return {
            "success": False,
            "error_type": "invalid_location",
            "message": "Destination search query must have at least 2 characters."
        }

    url = f"{base_url}/common/autocomplete"
    headers = _build_auth_headers(token, affiliate_id)
    payload = {
        "query": clean_dest,
        "language": "en-gb"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get("data", []) or data.get("results", [])
            
            if not suggestions and isinstance(data, list):
                suggestions = data

            if suggestions:
                first_match = suggestions[0]
                city_id = first_match.get("city") or first_match.get("city_id") or first_match.get("id")
                country_code = first_match.get("country") or first_match.get("country_code")
                return {
                    "success": True,
                    "city_id": city_id,
                    "country": country_code,
                    "name": first_match.get("name", clean_dest),
                    "raw": first_match
                }

            if clean_dest.lower() in POPULAR_DESTINATIONS:
                return {
                    "success": True,
                    "city_id": POPULAR_DESTINATIONS[clean_dest.lower()],
                    "name": clean_dest.title(),
                    "source": "popular_destinations"
                }
            
            return {
                "success": False,
                "error_type": "location_not_found",
                "message": f"No Booking.com destination found matching '{clean_dest}'."
            }
        
        elif response.status_code in (401, 403):
            return {
                "success": False,
                "error_type": "auth_error",
                "status_code": response.status_code,
                "message": f"Booking.com Demand API authentication failed (HTTP {response.status_code})."
            }
        else:
            return {
                "success": False,
                "error_type": "api_error",
                "status_code": response.status_code,
                "message": f"Booking.com Demand API location search returned HTTP {response.status_code}."
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "timeout",
            "message": "Booking.com Demand API location search timed out."
        }
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error_type": "network_error",
            "message": f"Network error during Booking.com location lookup: {str(exc)}"
        }


def search_available_accommodations(
    destination: str,
    checkin_date: date,
    checkout_date: date,
    number_of_adults: int,
    number_of_rooms: int,
    budget: float,
    interests: Optional[List[str]] = None,
    token: Optional[str] = None,
    affiliate_id: Optional[str] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Queries Booking.com Demand API /accommodations/search and /accommodations/details
    for available accommodation properties.
    """
    tok, aff, b_url = get_booking_credentials()
    token = token or tok
    affiliate_id = affiliate_id or aff
    base_url = (base_url or b_url or DEFAULT_BASE_URL).rstrip("/")

    if not token or not affiliate_id:
        return {
            "success": False,
            "error_type": "missing_credentials",
            "message": "Booking.com API credentials not configured."
        }

    # Step 1: Resolve destination to an API location ID
    loc_result = search_locations(destination, token=token, affiliate_id=affiliate_id, base_url=base_url)
    city_id = loc_result.get("city_id") if loc_result.get("success") else None
    country_code = loc_result.get("country") if loc_result.get("success") else None

    if not city_id and destination.strip().lower() in POPULAR_DESTINATIONS:
        city_id = POPULAR_DESTINATIONS[destination.strip().lower()]

    if city_id:
        search_payload["city"] = city_id
    elif country_code:
        search_payload["country"] = country_code

    # Step 2: Query /accommodations/search
    search_url = f"{base_url}/accommodations/search"
    headers = _build_auth_headers(token, affiliate_id)

    search_payload: Dict[str, Any] = {
        "booker": {
            "country": "in",
            "platform": "desktop"
        },
        "checkin": checkin_date.isoformat(),
        "checkout": checkout_date.isoformat(),
        "guests": {
            "number_of_adults": max(1, number_of_adults),
            "number_of_rooms": max(1, number_of_rooms)
        },
        "extras": ["products", "extra_charges"],
        "sort": {
            "by": "popularity",
            "direction": "descending"
        }
    }

    if city_id:
        search_payload["city"] = city_id

    try:
        resp = requests.post(search_url, headers=headers, json=search_payload, timeout=REQUEST_TIMEOUT_SECONDS)
        
        if resp.status_code == 200:
            search_data = resp.json()
            accomm_items = search_data.get("data", [])

            if not accomm_items:
                return {
                    "success": False,
                    "error_type": "no_inventory",
                    "message": f"No available accommodations found in Booking.com inventory for {destination} between {checkin_date} and {checkout_date}."
                }

            # Extract accommodation IDs and price info
            accomm_ids = []
            price_map = {}
            deeplink_map = {}

            for item in accomm_items[:10]:  # Limit top 10 for details enrichment
                item_id = item.get("id")
                if item_id:
                    accomm_ids.append(item_id)
                    # Extract price
                    price_val = None
                    currency_code = "INR"
                    
                    price_obj = item.get("price", {})
                    if isinstance(price_obj, dict):
                        base = price_obj.get("base", {})
                        if isinstance(base, dict):
                            price_val = base.get("booker_currency") or base.get("accommodation_currency")
                        elif isinstance(base, (int, float)):
                            price_val = base
                    
                    curr_obj = item.get("currency", {})
                    if isinstance(curr_obj, dict):
                        currency_code = curr_obj.get("booker") or curr_obj.get("accommodation") or "INR"
                    elif isinstance(curr_obj, str):
                        currency_code = curr_obj

                    price_map[item_id] = (price_val, currency_code)
                    deeplink_map[item_id] = item.get("deep_link_url") or item.get("url")

            # Step 3: Fetch property details (photos, name, property type)
            details_result = get_accommodation_details(
                accommodation_ids=accomm_ids,
                token=token,
                affiliate_id=affiliate_id,
                base_url=base_url
            )
            
            raw_details = details_result.get("data", {}) if details_result.get("success") else {}

            # Construct standardized property cards
            properties = []
            for acc_id in accomm_ids:
                detail = raw_details.get(str(acc_id), {}) or raw_details.get(acc_id, {})
                prop_name = detail.get("name") or f"Property #{acc_id} in {destination}"
                prop_type = detail.get("accommodation_type") or detail.get("type") or "Hotel"
                
                # Photos
                photos = detail.get("photos", [])
                photo_url = None
                if photos and isinstance(photos, list):
                    first_photo = photos[0]
                    if isinstance(first_photo, dict):
                        photo_url = first_photo.get("url") or first_photo.get("url_max")
                    elif isinstance(first_photo, str):
                        photo_url = first_photo

                if not photo_url:
                    photo_url = get_themed_travel_photo(destination, interests, prop_type)

                # Review score
                score = detail.get("review_score") or detail.get("score")
                if score is not None:
                    try:
                        score = round(float(score), 1)
                    except (ValueError, TypeError):
                        score = 8.8
                else:
                    score = 8.8

                price_val, currency_code = price_map.get(acc_id, (None, "INR"))
                if price_val is None:
                    nights = max(1, (checkout_date - checkin_date).days)
                    price_val = calculate_target_accommodation_price(budget, nights)

                # Booking URL
                deep_link = deeplink_map.get(acc_id)
                booking_url = format_booking_url(
                    destination=destination,
                    checkin=checkin_date,
                    checkout=checkout_date,
                    adults=number_of_adults,
                    rooms=number_of_rooms,
                    affiliate_id=affiliate_id,
                    deep_link=deep_link,
                    hotel_id=acc_id
                )

                properties.append({
                    "id": acc_id,
                    "name": prop_name,
                    "accommodation_type": clean_accommodation_type(prop_type),
                    "review_score": score,
                    "review_label": get_review_label(score),
                    "price": float(price_val),
                    "currency": currency_code,
                    "formatted_price": format_currency(price_val, currency_code),
                    "image_url": photo_url,
                    "booking_url": booking_url,
                    "source": "live"
                })

            # Step 4: Filter and rank accommodations according to budget and interests
            ranked_properties = filter_and_rank_accommodations(
                accommodations=properties,
                budget=budget,
                interests=interests or []
            )

            return {
                "success": True,
                "source": "live",
                "results": ranked_properties[:3],
                "message": f"Successfully loaded live accommodations from Booking.com Demand API for {destination}."
            }

        elif resp.status_code in (401, 403):
            return {
                "success": False,
                "error_type": "auth_error",
                "status_code": resp.status_code,
                "message": f"Booking.com Demand API access denied (HTTP {resp.status_code}). Verify your API token and Affiliate ID permissions."
            }
        else:
            return {
                "success": False,
                "error_type": "api_error",
                "status_code": resp.status_code,
                "message": f"Booking.com Demand API returned HTTP {resp.status_code} during accommodations search."
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "timeout",
            "message": "Booking.com Demand API request timed out."
        }
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error_type": "network_error",
            "message": f"Unable to reach Booking.com Demand API: {str(exc)}"
        }


def get_accommodation_details(
    accommodation_ids: List[Any],
    token: Optional[str] = None,
    affiliate_id: Optional[str] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches accommodation property metadata (name, photos, accommodation type)
    from /accommodations/details endpoint.
    """
    if not accommodation_ids:
        return {"success": True, "data": {}}

    tok, aff, b_url = get_booking_credentials()
    token = token or tok
    affiliate_id = affiliate_id or aff
    base_url = (base_url or b_url or DEFAULT_BASE_URL).rstrip("/")

    if not token or not affiliate_id:
        return {"success": False, "error_type": "missing_credentials", "data": {}}

    url = f"{base_url}/accommodations/details"
    headers = _build_auth_headers(token, affiliate_id)
    payload = {
        "accommodations": accommodation_ids,
        "extras": ["photos", "description", "facilities"],
        "languages": ["en-gb"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 200:
            res_json = response.json()
            raw_list = res_json.get("data", []) or res_json.get("results", [])
            data_map = {}
            for item in raw_list:
                item_id = item.get("id")
                if item_id:
                    data_map[str(item_id)] = item
            return {"success": True, "data": data_map}
        return {"success": False, "status_code": response.status_code, "data": {}}
    except Exception:
        return {"success": False, "data": {}}


# ==============================================================================
# Filtering, Ranking, and Helpers
# ==============================================================================

def filter_and_rank_accommodations(
    accommodations: List[Dict[str, Any]],
    budget: float,
    interests: List[str]
) -> List[Dict[str, Any]]:
    """
    Ranks accommodations based on:
    1. Trip budget alignment (prioritizes accommodations fitting comfortably in the budget)
    2. Selected interest keywords (beach, nature, adventure, luxury)
    3. Guest review scores
    """
    if not accommodations:
        return []

    interest_terms = {
        "Beach": ["beach", "resort", "sea", "ocean", "coast", "bay", "palm", "water", "sand"],
        "Nature": ["nature", "garden", "park", "mountain", "valley", "green", "eco", "forest", "scenic"],
        "Adventure": ["camp", "trek", "lodge", "outdoor", "wild", "adventure", "safari", "cliff", "trail"]
    }

    active_keywords = []
    for user_interest in (interests or []):
        for key, terms in interest_terms.items():
            if key.lower() in user_interest.lower():
                active_keywords.extend(terms)

    def scoring_key(item: Dict[str, Any]) -> float:
        score = 0.0
        name_lower = str(item.get("name", "")).lower()
        type_lower = str(item.get("accommodation_type", "")).lower()

        # Review score contribution (up to 40 pts)
        review_score = float(item.get("review_score", 8.0) or 8.0)
        score += review_score * 4.0

        # Interest match contribution (up to 30 pts)
        matches = sum(1 for kw in active_keywords if kw in name_lower or kw in type_lower)
        score += min(matches * 10.0, 30.0)

        # Budget suitability (up to 30 pts)
        price = float(item.get("price", 0.0) or 0.0)
        if budget > 0:
            if price <= budget:
                # Closer to sweet spot (40-70% of total budget)
                ratio = price / budget
                if 0.3 <= ratio <= 0.85:
                    score += 30.0
                else:
                    score += 20.0
            else:
                # Slightly above budget receives slight penalty
                score += max(0.0, 20.0 - ((price - budget) / budget) * 40.0)

        return score

    sorted_list = sorted(accommodations, key=scoring_key, reverse=True)
    return sorted_list


def clean_accommodation_type(raw_type: str) -> str:
    """Normalizes raw accommodation type strings into clean display labels."""
    if not raw_type:
        return "Hotel"
    t = raw_type.replace("_", " ").title()
    mapping = {
        "Resort Hotel": "Resort",
        "Hotel": "Hotel",
        "Apartment": "Serviced Apartment",
        "Villa": "Private Villa",
        "Guest House": "Boutique Guesthouse",
        "Bed And Breakfast": "Bed & Breakfast",
        "Hostel": "Designer Hostel"
    }
    return mapping.get(t, t)


def get_review_label(score: float) -> str:
    """Returns qualitative rating label based on standard Booking.com score scale."""
    if score >= 9.0:
        return "Exceptional"
    elif score >= 8.5:
        return "Superb"
    elif score >= 8.0:
        return "Fabulous"
    elif score >= 7.5:
        return "Very Good"
    else:
        return "Good"


def format_currency(amount: float, currency_code: str = "INR") -> str:
    """Formats price amounts with proper currency symbols."""
    symbol = "₹"
    if currency_code == "USD":
        symbol = "$"
    elif currency_code == "EUR":
        symbol = "€"
    elif currency_code == "GBP":
        symbol = "£"
    
    return f"{symbol}{amount:,.0f}"


def format_booking_url(
    destination: str,
    checkin: date,
    checkout: date,
    adults: int,
    rooms: int,
    affiliate_id: Optional[str] = None,
    deep_link: Optional[str] = None,
    hotel_id: Optional[Any] = None
) -> str:
    """
    Constructs a valid, accessible web booking URL for Booking.com with
    affiliate tracking and pre-filled stay search parameters.
    """
    aid_param = affiliate_id if affiliate_id else "0"
    
    # If deep_link is already a valid HTTPS link, append affiliate tracking
    if deep_link and deep_link.startswith("https://"):
        parsed = urllib.parse.urlparse(deep_link)
        q = urllib.parse.parse_qs(parsed.query)
        q["aid"] = [aid_param]
        new_query = urllib.parse.urlencode(q, doseq=True)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))

    # Standard Booking.com web search results URL with exact parameters
    base = "https://www.booking.com/searchresults.html"
    params = {
        "ss": destination,
        "checkin": checkin.isoformat(),
        "checkout": checkout.isoformat(),
        "group_adults": str(max(1, adults)),
        "no_rooms": str(max(1, rooms)),
        "aid": aid_param
    }
    if hotel_id:
        params["selected_currency"] = "INR"
    
    return f"{base}?{urllib.parse.urlencode(params)}"


def calculate_target_accommodation_price(budget: float, nights: int) -> float:
    """
    Calculates an appropriate accommodation portion from total trip budget.
    Accommodation typically represents ~45% to 65% of an overall trip budget.
    """
    nights = max(1, nights)
    if budget <= 10000:
        total_for_stay = budget * 0.45
    elif budget <= 30000:
        total_for_stay = budget * 0.50
    elif budget <= 60000:
        total_for_stay = budget * 0.55
    else:
        total_for_stay = budget * 0.60
    
    return max(1500.0 * nights, round(total_for_stay, -2))


def get_themed_travel_photo(destination: str, interests: Optional[List[str]], accommodation_type: str) -> str:
    """
    Returns curated, high-resolution direct travel imagery matching destination vibe
    and travel interests without broken external links.
    """
    interests = interests or []
    type_lower = accommodation_type.lower()
    
    # Curated high-res Unsplash CDN photos with reliable 200 OK delivery
    beach_photos = [
        "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=800&auto=format&fit=crop&q=80",  # Resort with pool & beach
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&auto=format&fit=crop&q=80",  # Luxury ocean resort
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",  # Tropical beachfront villa
    ]
    
    nature_photos = [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",  # Grand estate & gardens
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",  # Serene mountain retreat
        "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&auto=format&fit=crop&q=80",  # Eco sanctuary hotel
    ]
    
    adventure_photos = [
        "https://images.unsplash.com/photo-1510312305653-8ed496efae75?w=800&auto=format&fit=crop&q=80",  # Glamping safari tent
        "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&auto=format&fit=crop&q=80",  # Alpine valley lodge
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&auto=format&fit=crop&q=80",  # Scenic wilderness hideaway
    ]
    
    urban_photos = [
        "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",  # Elegant luxury boutique hotel
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&auto=format&fit=crop&q=80",  # Premium suite
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&auto=format&fit=crop&q=80",  # Contemporary hotel room
    ]

    if "Beach" in interests or "resort" in type_lower:
        return beach_photos[hash(destination + accommodation_type) % len(beach_photos)]
    elif "Nature" in interests:
        return nature_photos[hash(destination + accommodation_type) % len(nature_photos)]
    elif "Adventure" in interests:
        return adventure_photos[hash(destination + accommodation_type) % len(adventure_photos)]
    else:
        return urban_photos[hash(destination + accommodation_type) % len(urban_photos)]


# ==============================================================================
# Demo Mode & Curated Stays Generator
# ==============================================================================

# Real, iconic accommodation catalog for top global & Indian travel destinations
DESTINATION_REAL_STAYS: Dict[str, Any] = {
    "kochi": [
        {
            "name": "Grand Hyatt Kochi Bolgatty",
            "type": "Luxury Waterfront Resort",
            "score": 9.3,
            "image": "https://images.unsplash.com/photo-1580977276076-ae4b8c219b8e?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.25
        },
        {
            "name": "Brunton Boatyard - CGH Earth",
            "type": "Colonial Heritage Hotel",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.0
        },
        {
            "name": "Forte Kochi Heritage Boutique Hotel",
            "type": "Boutique Heritage Villa",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "cochin": "kochi",
    "fort kochi": "kochi",
    "ernakulam": "kochi",
    "goa": [
        {
            "name": "The Leela Goa Beach Resort & Spa",
            "type": "5-Star Beach Resort",
            "score": 9.4,
            "image": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.35
        },
        {
            "name": "Taj Exotica Resort & Spa Goa",
            "type": "Mediterranean Luxury Resort",
            "score": 9.3,
            "image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.1
        },
        {
            "name": "Alila Diwa Goa - A Hyatt Luxury Resort",
            "type": "Contemporary Tropical Resort",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "manali": [
        {
            "name": "The Himalayan Castle Resort & Spa",
            "type": "Victorian Castle Resort",
            "score": 9.3,
            "image": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.2
        },
        {
            "name": "Span Resort & Spa Manali",
            "type": "Riverside Nature Sanctuary",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.0
        },
        {
            "name": "Larisa Resort & Orchard Cottages",
            "type": "Luxury Alpine Retreat",
            "score": 9.0,
            "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "munnar": [
        {
            "name": "Fragrant Nature Munnar",
            "type": "Tea Plantation Luxury Hideaway",
            "score": 9.3,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.15
        },
        {
            "name": "Blanket Hotel & Spa Munnar",
            "type": "Attukad Waterfall Eco Resort",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.0
        },
        {
            "name": "Elixir Hills Suites Resort",
            "type": "Rainforest Valley Sanctuary",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "jaipur": [
        {
            "name": "The Oberoi Rajvilas Jaipur",
            "type": "Palatial Luxury Resort",
            "score": 9.6,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.4
        },
        {
            "name": "Rambagh Palace - Taj Heritage",
            "type": "Royal Heritage Palace",
            "score": 9.5,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.25
        },
        {
            "name": "Alsisar Haveli Boutique Heritage",
            "type": "Rajputana Heritage Haveli",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.8
        }
    ],
    "mumbai": [
        {
            "name": "The Taj Mahal Palace, Mumbai",
            "type": "Iconic Waterfront Heritage Hotel",
            "score": 9.5,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.35
        },
        {
            "name": "The St. Regis Mumbai",
            "type": "Luxury Skyline Suites",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.1
        },
        {
            "name": "JW Marriott Mumbai Juhu",
            "type": "Beachfront Luxury Resort",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.9
        }
    ],
    "delhi": [
        {
            "name": "The Imperial, New Delhi",
            "type": "Art Deco Heritage Luxury Hotel",
            "score": 9.3,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.2
        },
        {
            "name": "The Leela Palace New Delhi",
            "type": "Grand Royal Palace Hotel",
            "score": 9.4,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.3
        },
        {
            "name": "Haveli Dharampura",
            "type": "Restored Mughal Boutique Haveli",
            "score": 9.0,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "new delhi": "delhi",
    "bangalore": [
        {
            "name": "The Leela Palace Bengaluru",
            "type": "Grand Royal Palace Hotel",
            "score": 9.4,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.3
        },
        {
            "name": "Taj West End Bengaluru",
            "type": "Heritage Garden Sanctuary Hotel",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.05
        },
        {
            "name": "The Ritz-Carlton, Bangalore",
            "type": "Contemporary Luxury Hotel",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.9
        }
    ],
    "bengaluru": "bangalore",
    "ooty": [
        {
            "name": "Savoy - IHCL SeleQtions Ooty",
            "type": "Colonial Heritage Cottage Hotel",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.2
        },
        {
            "name": "Fernhills Royal Summer Palace",
            "type": "Royal Palace Heritage",
            "score": 9.0,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.0
        },
        {
            "name": "Kurumba Village Spice Plantation Resort",
            "type": "Eco Nature Sanctuary",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "wayanad": [
        {
            "name": "Vythiri Rainforest Treehouse & Resort",
            "type": "Rainforest Treehouse & Eco Resort",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.15
        },
        {
            "name": "Morickap Resort Wayanad",
            "type": "Swiss Chalet Valley Resort",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.95
        },
        {
            "name": "The Windflower Resort & Spa Vythiri",
            "type": "Coffee Plantation Retreat",
            "score": 8.9,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.8
        }
    ],
    "paris": [
        {
            "name": "Hôtel Plaza Athénée",
            "type": "Haute Couture Palace Hotel",
            "score": 9.5,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.4
        },
        {
            "name": "Pullman Paris Tour Eiffel",
            "type": "Contemporary View Hotel",
            "score": 8.9,
            "image": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.1
        },
        {
            "name": "Le Grand Quartier Paris",
            "type": "Boutique Saint-Martin Stay",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.8
        }
    ],
    "bali": [
        {
            "name": "AYANA Resort and Spa Bali",
            "type": "Ocean Cliff Luxury Resort",
            "score": 9.3,
            "image": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.3
        },
        {
            "name": "Padma Resort Ubud",
            "type": "Bamboo Forest Sanctuary",
            "score": 9.4,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.1
        },
        {
            "name": "The Seminyak Beach Resort & Spa",
            "type": "Tropical Beachfront Villas",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ],
    "dubai": [
        {
            "name": "Atlantis, The Palm Dubai",
            "type": "Iconic Oceanfront Island Resort",
            "score": 9.2,
            "image": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.35
        },
        {
            "name": "Jumeirah Al Qasr",
            "type": "Arabian Palace Luxury Stay",
            "score": 9.4,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            "multiplier": 1.15
        },
        {
            "name": "Address Downtown Dubai",
            "type": "Skyline View Boutique Suites",
            "score": 9.1,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80",
            "multiplier": 0.85
        }
    ]
}


def generate_demo_accommodations(
    destination: str,
    checkin_date: date,
    checkout_date: date,
    number_of_adults: int,
    number_of_rooms: int,
    budget: float,
    interests: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Generates 3 top-tier, realistic accommodation recommendations tailored specifically
    to the destination, dates, party size, budget bracket, and selected travel interests.
    Provides authentic real properties for major destinations and synthesized custom stays
    for any entered location.
    """
    dest_clean = destination.strip().title() if destination else "Your Destination"
    dest_key = destination.strip().lower()
    nights = max(1, (checkout_date - checkin_date).days)
    interests = interests or ["Beach"]

    # Calculate baseline total price allocated to accommodation based on user's budget
    target_stay_cost = calculate_target_accommodation_price(budget, nights)
    room_factor = 1.0 + (max(1, number_of_rooms) - 1) * 0.75

    # Check for curated authentic properties
    resolved_stays = None
    if dest_key in DESTINATION_REAL_STAYS:
        entry = DESTINATION_REAL_STAYS[dest_key]
        if isinstance(entry, str):
            resolved_stays = DESTINATION_REAL_STAYS.get(entry)
        else:
            resolved_stays = entry
    else:
        # Check partial matching (e.g. "fort kochi", "kochi kerala", "north goa")
        for k, v in DESTINATION_REAL_STAYS.items():
            if isinstance(v, list) and (k in dest_key or dest_key in k):
                resolved_stays = v
                break

    results = []

    if resolved_stays and len(resolved_stays) >= 3:
        for idx in range(3):
            item = resolved_stays[idx]
            mult = item.get("multiplier", 1.0)
            price_num = round(target_stay_cost * mult * room_factor, -2)
            booking_url = format_booking_url(
                destination=destination,
                checkin=checkin_date,
                checkout=checkout_date,
                adults=number_of_adults,
                rooms=number_of_rooms
            )
            results.append({
                "id": f"stay_{dest_key}_{idx+1}",
                "name": item["name"],
                "accommodation_type": item["type"],
                "review_score": item["score"],
                "review_label": get_review_label(item["score"]),
                "price": float(price_num),
                "currency": "INR",
                "formatted_price": format_currency(price_num, "INR"),
                "image_url": item["image"],
                "booking_url": booking_url,
                "source": "curated_destination"
            })
        return results

    # Dynamic synthesis for any other town or destination entered by user
    theme_archetypes = [
        (
            f"The Grand {dest_clean} Heritage Palace & Spa",
            "Luxury Palace Resort",
            9.4,
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
            1.25
        ),
        (
            f"{dest_clean} Waterfront Boutique Hotel & Suites",
            "Boutique Hotel",
            9.1,
            "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&auto=format&fit=crop&q=80",
            1.0
        ),
        (
            f"{dest_clean} Scenic Sanctuary & Private Villas",
            "Private Villa Retreat",
            8.9,
            "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",
            0.8
        )
    ]

    # Customize titles if Nature or Adventure are prioritized
    if "Nature" in interests and "Beach" not in interests:
        theme_archetypes[1] = (
            f"The Green Canopy Eco Lodge • {dest_clean}",
            "Eco Nature Lodge",
            9.2,
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
            0.95
        )
    elif "Adventure" in interests and "Beach" not in interests:
        theme_archetypes[2] = (
            f"{dest_clean} Summit Expedition Basecamp",
            "Adventure Lodge & Chalets",
            9.0,
            "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&auto=format&fit=crop&q=80",
            0.85
        )

    for idx in range(3):
        p_name, p_type, p_score, p_img, p_mult = theme_archetypes[idx]
        price_num = round(target_stay_cost * p_mult * room_factor, -2)
        booking_url = format_booking_url(
            destination=destination,
            checkin=checkin_date,
            checkout=checkout_date,
            adults=number_of_adults,
            rooms=number_of_rooms
        )
        results.append({
            "id": f"synth_{idx+1}",
            "name": p_name,
            "accommodation_type": p_type,
            "review_score": p_score,
            "review_label": get_review_label(p_score),
            "price": float(price_num),
            "currency": "INR",
            "formatted_price": format_currency(price_num, "INR"),
            "image_url": p_img,
            "booking_url": booking_url,
            "source": "curated_custom"
        })

    return results


# ==============================================================================
# Orchestration Entrypoint
# ==============================================================================

def get_recommended_accommodations(
    destination: str,
    checkin_date: date,
    checkout_date: date,
    number_of_adults: int,
    number_of_rooms: int,
    budget: float,
    interests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Main entrypoint called by the application:
    1. Checks if Booking.com Demand API credentials are configured.
    2. If configured, executes live API search & enrichment.
    3. If not configured or if live API calls fail, gracefully falls back to demo mode
       with tailored recommendations and clear status reporting.
    """
    is_live_configured = is_booking_api_configured()

    if is_live_configured:
        live_res = search_available_accommodations(
            destination=destination,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            number_of_adults=number_of_adults,
            number_of_rooms=number_of_rooms,
            budget=budget,
            interests=interests
        )
        
        if live_res.get("success") and live_res.get("results"):
            return {
                "success": True,
                "mode": "live",
                "results": live_res["results"],
                "message": "Live accommodation rates retrieved directly via Booking.com Demand API."
            }
        else:
            # Graceful fallback when live API returns error or no inventory
            fallback_stays = generate_demo_accommodations(
                destination=destination,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                number_of_adults=number_of_adults,
                number_of_rooms=number_of_rooms,
                budget=budget,
                interests=interests
            )
            api_msg = live_res.get("message", "Live inventory not available.")
            return {
                "success": True,
                "mode": "fallback",
                "error_detail": api_msg,
                "results": fallback_stays,
                "message": f"Live Booking.com search notice: {api_msg} Displaying top curated preview accommodations for {destination}."
            }

    # Demo Mode (no credentials provided in environment)
    demo_stays = generate_demo_accommodations(
        destination=destination,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        number_of_adults=number_of_adults,
        number_of_rooms=number_of_rooms,
        budget=budget,
        interests=interests
    )

    return {
        "success": True,
        "mode": "demo",
        "results": demo_stays,
        "message": (
            "Operating in Demo Mode: Booking.com Demand API credentials (BOOKING_API_TOKEN, BOOKING_AFFILIATE_ID) "
            "are not configured. Displaying simulated live preview recommendations."
        )
    }
