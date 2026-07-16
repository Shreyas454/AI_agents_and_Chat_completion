from groq import Groq
client = Groq()

# Turn 1 - tell the model your name
turn1 = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "My name is Shreyas."}
    ],
    temperature=0,
    max_completion_tokens=50
)
turn1_reply = turn1.choices[0].message.content
print("Turn 1:", turn1_reply)

# Turn 2 - ask WITHOUT resending history
turn2_no_history = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "What is my name?"}
    ],
    temperature=0,
    max_completion_tokens=50
)
print("\nTurn 2 (no history):", turn2_no_history.choices[0].message.content)

# Turn 2 - ask WITH resending history
turn2_with_history = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "My name is Shreyas."},
        {"role": "assistant", "content": turn1_reply},
        {"role": "user", "content": "What is my name?"}
    ],
    temperature=0,
    max_completion_tokens=50
)
print("\nTurn 2 (with history):", turn2_with_history.choices[0].message.content)