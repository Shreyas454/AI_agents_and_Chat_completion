from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


hotels = {
    "H001": {
        "name": "Beach Resort Goa",
        "city": "goa",
        "price_per_night": 3500,
        "rating": 4.2,
        "rooms_available": 10
    },
    "H002": {
        "name": "The Grand Palace",
        "city": "goa",
        "price_per_night": 7200,
        "rating": 4.8,
        "rooms_available": 5
    },
    "H003": {
        "name": "City Center Inn",
        "city": "mumbai",
        "price_per_night": 4200,
        "rating": 4.0,
        "rooms_available": 15
    },
    "H004": {
        "name": "Marine Drive Hotel",
        "city": "mumbai",
        "price_per_night": 6500,
        "rating": 4.5,
        "rooms_available": 8
    },
    "H005": {
        "name": "Delhi Heritage",
        "city": "delhi",
        "price_per_night": 5500,
        "rating": 4.3,
        "rooms_available": 12
    },
    "H006": {
        "name": "Capital Suites",
        "city": "delhi",
        "price_per_night": 8900,
        "rating": 4.7,
        "rooms_available": 3
    }
}

bookings = {}


def search_hotels(city: str, guests: int) -> dict:
    """Search for available hotels in a city that can accommodate the required number of guests.
    
    Args:
        city: The city to search in (e.g., "Mumbai", "Goa", "Delhi"). Case-insensitive.
        guests: The number of rooms needed. Only hotels with at least this many rooms available will be returned.
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "hotels": list of matching hotels (each with hotel_id, name, price_per_night, rating, rooms_available) if success
        - "message": error message if no hotels found or city invalid
    """
    city_lower = city.lower().strip()
    matching_hotels = []
    for hotel_id, hotel in hotels.items():
        if hotel["city"] == city_lower and hotel["rooms_available"] >= guests:
            matching_hotels.append({
                "hotel_id": hotel_id,
                "name": hotel["name"],
                "price_per_night": hotel["price_per_night"],
                "rating": hotel["rating"],
                "rooms_available": hotel["rooms_available"]
            })

    if matching_hotels:
        return {
            "status": "success",
            "hotels": matching_hotels
        }    
    else:   
        return {
            "status": "error",
            "message": f"No hotels found in {city} that can accommodate {guests} guests."
        }
    
def get_hotel_details(hotel_id: str) -> dict:
    """Get detailed information about a specific hotel by its ID.
    
    Args:
        hotel_id: The unique hotel identifier (e.g., "H001", "H004").
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "hotel": full details of the hotel if found
        - "message": error message if hotel_id doesn't exist
    """
    if hotel_id in hotels:
        return {
            "status": "success",
            "hotel": hotels[hotel_id]
        }
    else:
        return {
            "status": "error",
            "message": f"Hotel with ID {hotel_id} not found."
        }
   
def book_hotel(hotel_id: str, guest_name: str, rooms: int) -> dict:
    """Book one or more rooms at a specific hotel for a guest. Reduces available room count.
    
    Args:
        hotel_id: The unique hotel identifier (e.g., "H001").
        guest_name: The full name of the guest making the booking.
        rooms: The number of rooms to book. Must be less than or equal to rooms_available.
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "booking_id": unique booking identifier if success (format: "BK" + 4 digit number)
        - "hotel_name": name of the booked hotel
        - "rooms_booked": number of rooms booked
        - "total_cost": total price (rooms * price_per_night)
        - "message": error message if hotel not found or not enough rooms
    """     
    if hotel_id not in hotels:
        return {
            "status": "error",
            "message": f"Hotel with ID {hotel_id} not found."
        }
    
    hotel = hotels[hotel_id]
    if rooms > hotel["rooms_available"]:
        return {
            "status": "error",
            "message": f"Not enough rooms available at {hotel['name']}. Only {hotel['rooms_available']} left."
        }
    
    
    booking_id = f"BK{len(bookings) + 1:04d}"
    total_cost = rooms * hotel["price_per_night"]
    
    
    bookings[booking_id] = {
        "hotel_id": hotel_id,
        "guest_name": guest_name,
        "rooms_booked": rooms,
        "total_cost": total_cost
    }
    
    
    hotel["rooms_available"] -= rooms
    
    return {
        "status": "success",
        "booking_id": booking_id,
        "hotel_name": hotel["name"],
        "rooms_booked": rooms,
        "total_cost": total_cost
    }

def check_booking(booking_id: str) -> dict:
    """Retrieve details of an existing booking by its booking ID.
    
    Args:
        booking_id: The unique booking identifier returned when the booking was made (e.g., "BK0001").
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "booking": full booking details if found
        - "message": error message if booking_id doesn't exist
    """
    if booking_id in bookings:
        return {
            "status": "success",
            "booking": bookings[booking_id]
        }
    else:
        return {
            "status": "error",
            "message": f"Booking with ID {booking_id} not found."
        }
    
   
root_agent = Agent(
    name="hotel_booking_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
    description="An agent that provides hotel availability for cities and allows users to book hotels",
    instruction="""You are a helpful hotel booking assistant. You can search for hotels, get hotel details, book rooms, and check existing bookings.

    When a user wants to search for hotels:
    - If they don't specify how many rooms they need, ask before searching.
    - Show them the results with hotel name, price, rating, and availability.

    When a user wants to book a hotel:
    - Confirm the hotel_id, number of rooms, and get their full name before booking.
    - Do not book until the user explicitly confirms.
    - Always share the booking_id after a successful booking so they can reference it later.

    If any tool returns an error, explain the issue clearly and offer alternatives when possible.""",
    tools=[search_hotels, get_hotel_details, book_hotel, check_booking],
)




