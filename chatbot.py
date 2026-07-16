from groq import Groq

client = Groq()
conversation_history = []

SYSTEM_PROMPT = """You are Jarvis, a sharp and slightly sarcastic AI assistant. 
You are helpful but never sugarcoat things. Keep responses concise."""

def chat(user_message, temperature=0.7, max_tokens=200,top_p = 1.0):
    conversation_history.append({
        "role": "user", 
        "content": user_message
    })
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=top_p,
        stop = ["blue"]
    )
    
    assistant_message = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return assistant_message


def chat_stream(user_message, temperature=0.7, max_tokens=200, top_p=1.0):
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=top_p,
        stream=True,
        stop = ["blue"]
    )
    
    print("\nJarvis: ", end="", flush=True)
    full_response = ""
    
    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            print(token, end="", flush=True)
            full_response += token
    
    print("\n")
    conversation_history.append({
        "role": "assistant",
        "content": full_response
    })
    
    return full_response
print("Jarvis is online. Type 'quit' to exit.")
print("Commands: !temp 0.9 (change temperature) | !tokens 500 (change max tokens) | !history (see conversation)\n")

current_temp = 0.7
current_tokens = 200
top_p_value = 1.0

while True:
    user_input = input("You: ").strip()
    
    if user_input.lower() == 'quit':
        break
    elif user_input.startswith('!temp'):
        current_temp = float(user_input.split()[1])
        print(f"Temperature set to {current_temp}")
        continue
    elif user_input.startswith('!tokens'):
        current_tokens = int(user_input.split()[1])
        print(f"Max tokens set to {current_tokens}")
        continue
    elif user_input.startswith('!topp'):
        top_p_value = float(user_input.split()[1])
        print(f"Top P set to {top_p_value}")
        continue
    elif user_input == '!history':
        print("\n--- Conversation History ---")
        for msg in conversation_history:
            print(f"{msg['role'].upper()}: {msg['content'][:80]}...")
        print("---------------------------\n")
        continue
    
    response = chat_stream(user_input, current_temp, current_tokens , top_p_value)
    'print(f"\nJarvis: {response}\n")'