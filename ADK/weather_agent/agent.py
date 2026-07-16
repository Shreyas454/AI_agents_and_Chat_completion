from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

def get_weather(city: str) -> dict:
    """Returns the current weather for a specified city.
    
    Args:
        city: The name of the city to get weather for
    
    Returns:
        A dictionary with the weather status, city, temperature, and condition
    """

  
    weather_data = {
        "goa": {"temp": 32, "condition": "sunny"},
        "mumbai": {"temp": 28, "condition": "humid"},
        "delhi": {"temp": 18, "condition": "foggy"}
    }
    
    city_lower = city.lower().strip()

    if city_lower in weather_data:
        data = weather_data[city_lower]
        return {
            "status": "success",
            "city": city,
            "temperature": data["temp"],
            "condition": data["condition"]
        }
    else:
        return {
            "status": "error",
            "message": f"Weather data not available for {city}"
        }


root_agent = Agent(
    name="weather_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
    description="An agent that provides current weather information for cities",
    instruction="You are a helpful weather assistant. Use the get_weather tool to fetch weather data when users ask about weather in a specific city. If the city is not in your data, politely inform the user.",
    tools=[get_weather],
)