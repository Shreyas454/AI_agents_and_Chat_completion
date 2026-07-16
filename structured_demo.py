from groq import Groq
import json

client = Groq()

def extract_hotel_details(user_message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content":"""You are a data extraction tool. 
                          Extract hotel booking details and return ONLY a JSON object.
                          You MUST use EXACTLY these field names with EXACTLY this spelling:
                          - "destination" 
                          - "checkin_date" (format: YYYY-MM-DD)
                          - "duration_nights" (integer)
                          - "guests" (integer)

                          Example output:
                          {"destination": "Mumbai", "checkin_date": "2024-12-01", "duration_nights": 3, "guests": 2}

                          Any other field names are WRONG. Copy the field names exactly from the example."""
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0,
        max_completion_tokens=200,
        response_format={
    "type": "json_object",
    "json_object": {
        "name": "hotel_search",
        "schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "checkin_date": {"type": "string"},
                "duration_nights": {"type": "integer"},
                "guests": {"type": "integer"}
            },
            "required": ["destination", "checkin_date", "duration_nights", "guests"]
        }
    }
}
    )
    
    raw = response.choices[0].message.content
    parsed = json.loads(raw)
    return parsed

# Test it
test_messages = [
    "I want a hotel in Goa for 3 nights from December 1st for 2 people",
    "Book me something in Mumbai, checking in Jan 5th, 2 nights, just me",
    "Need a room in Delhi from 15th March for a week, 4 guests"
]

for msg in test_messages:
    print(f"\nInput: {msg}")
    result = extract_hotel_details(msg)
    print(f"Extracted: {result}")
    print(f"Type: {type(result)}")  # proves it's a dict, not a string