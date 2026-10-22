from Core.RAG import answer_with_ollama_rag

def main():
    print("Hello! Welcome to the ICVS Assistant CLI.")
    print("Ask me anything about ICVS procedures. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if not question:
            print("Assistant: Please ask a question.")
            continue

        print("\nAssistant:")
        try:
            answer_with_ollama_rag(question)
        except Exception as e:
            print(f"Sorry, an error occurred: {e}")
        print("\n" + "-" * 50)

if __name__ == "__main__":
    main()