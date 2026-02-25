import os
from pydantic_ai.messages import ModelMessage
from pydantic import TypeAdapter
from src.brain import orchestrator_agent

# Path for persistent chat history
MEMORY_PATH = "memory/chat_history.json"
# Pydantic adapter for complex message serialization
HistoryAdapter = TypeAdapter(list[ModelMessage])


def load_memory():
    """Load chat history from local storage."""
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "rb") as f:
                return HistoryAdapter.validate_json(f.read())
        except Exception as e:
            print(f"⚠️ Memory load error: {e}")
    return []


def save_memory(messages):
    """Save chat history to local storage."""
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "wb") as f:
        f.write(HistoryAdapter.dump_json(messages, indent=2))


def run_brain():
    # TODO: - 1. Start Telemetry (Arize Phoenix)
    # init_telemetry(project_name="second-brain-foundation")

    print("🧠 Second Brain: Foundation Layer Online")
    print("(Type 'exit' to quit or 'clear' to reset memory)")

    # 2. Initialize Memory
    chat_history = load_memory()
    if chat_history:
        print(f"📜 Loaded {len(chat_history)} previous message events.")

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "clear":
            chat_history = []
            if os.path.exists(MEMORY_PATH):
                os.remove(MEMORY_PATH)
            print("✨ Memory cleared.")
            continue

        # 3. Run the Multi-Agent Orchestrator
        try:
            # We pass the history so the agent remembers previous turns
            result = orchestrator_agent.run_sync(
                user_input, message_history=chat_history
            )

            # TODO: - 4. Apply PII Guardrail
            # safe_answer = clean_pii(result.output)
            # print(f"\n🧠 Brain: {safe_answer}")
            print(f"\n🧠 Brain: {result.output}")

            # 5. Persist the updated history
            chat_history = result.all_messages()
            save_memory(chat_history)

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_brain()
