from groq import Groq
import json

client = Groq()

# Step 1 — Define fake tool functions (simulating real APIs)
def get_weather(city):
    # In real life this would call a weather API
    weather_data = {
        "Goa": {"temp": 32, "condition": "sunny"},
        "Mumbai": {"temp": 28, "condition": "humid"},
        "Delhi": {"temp": 18, "condition": "foggy"}
    }
    return weather_data.get(city, {"temp": 25, "condition": "unknown"})

def search_hotels(city, checkin_date, duration_nights, guests):
    # In real life this would call a hotel booking API
    return {
        "hotels": [
            {"name": "Hotel Sunshine", "price": 3500, "rating": 4.2},
            {"name": "The Grand", "price": 7200, "rating": 4.8}
        ],
        "city": city,
        "available": True
    }

# Step 2 — Define tool schemas (what you tell the LLM about your tools)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Search for available hotels in a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string","description": "The city name"},
                    "checkin_date": {"type": "string", "description": "Format YYYY-MM-DD"},
                    "duration_nights": {"type": "integer"},
                    "guests": {"type": "integer"}
                },
                "required": ["city", "checkin_date", "duration_nights", "guests"]
            }
        }
    }
]

# Step 3 — The agent loop
def run_agent(user_message):
    print(f"\nUser: {user_message}")
    
    messages = [
        {"role": "system", "content": "You are a helpful hotel booking assistant."},
        {"role": "user", "content": user_message}
    ]
    
    # Map function names to actual functions
    available_functions = {
        "get_weather": get_weather,
        "search_hotels": search_hotels
    }
    
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="required",
            temperature=0
        )
        
        choice = response.choices[0]
        
        # Did the LLM want to call a tool?
        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            
            # Add LLM's tool request to messages
            messages.append(choice.message)
            
            # Execute each tool call
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                print(f"\n[Tool Call] {fn_name}({fn_args})")
                
                # Actually execute the function
                result = available_functions[fn_name](**fn_args)
                print(f"[Tool Result] {result}")
                
                # Feed result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        
        else:
            # LLM gave a final answer, no more tool calls
            print(f"\nAssistant: {choice.message.content}")
            break

# Test it
run_agent("What's the weather like in Goa?")
run_agent("Find me hotels in Mumbai for Dec 1st, 2 nights, 2 guests")
run_agent("I'm planning a trip to Delhi. What's the weather and are there hotels available for Dec 20th, 3 nights, 1 guest?")