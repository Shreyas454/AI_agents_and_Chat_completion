from agent import run_agent

def main():
    print("=" * 60)
    print("  Coding Agent CLI")
    print("  Type 'exit' to quit")
    print("=" * 60)
    print()
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        try:
            response, conversation_history = run_agent(user_input, conversation_history)
            print(f"\nAssistant: {response}\n")
        except Exception as e:
            print(f"\n[Error] {str(e)}\n")


if __name__ == "__main__":
    main()