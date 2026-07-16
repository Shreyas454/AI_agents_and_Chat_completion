from groq import Groq
client = Groq()

for limit in [10, 50, 200]:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Explain how the internet works."}],
        temperature=0,
        max_completion_tokens=limit
    )
    print(f"\n--- max_completion_tokens={limit} ---")
    print(response.choices[0].message.content)