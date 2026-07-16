import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv("weather_agent/.env")

client = Groq()  # picks up GROQ_API_KEY from env

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hi"}]
)

print(response.choices[0].message.content)