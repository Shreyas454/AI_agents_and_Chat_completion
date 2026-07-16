from groq import Groq

client = Groq()

def test_temperature(temp):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": "Write a one line description of the ocean."}
        ],
        temperature=temp,
        max_completion_tokens=50
    )
    print(f"\nTemperature {temp}:")
    print(response.choices[0].message.content)

# Run the same prompt at 3 different temperatures
test_temperature(0)
test_temperature(0)   # run 0 twice to show it's consistent
test_temperature(1.5)
test_temperature(1.5) # run 1.5 twice to show it varies