from pydantic_ai import Agent, RunContext
import chromadb
from chromadb.utils import embedding_functions

# DB Setup
client = chromadb.PersistentClient(path="./db")
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_collection("knowledge_base", embedding_function=emb_fn)

# Specialist: Focuses only on facts
notes_agent = Agent(
    "anthropic:claude-sonnet-4-6",
    system_prompt="You are a Factual Researcher. Provide detailed facts from the search results.",
)


@notes_agent.tool
def search_tool(ctx: RunContext[None], query: str) -> str:
    """Retrieve facts from your personal notes."""
    results = collection.query(query_texts=[query], n_results=5)
    return (
        "\n\n".join(results["documents"][0])
        if results["documents"]
        else "No info found."
    )


# --- 2. THE MANAGER (Orchestrator Agent) ---
orchestrator_agent = Agent(
    "anthropic:claude-sonnet-4-6",
    system_prompt=(
        "You are the user's 'Second Brain' AI assistant. "
        "CRITICAL INSTRUCTIONS:\n"
        "1. ALWAYS check conversation history first for recent context and things the user just told you.\n"
        "2. If you find the answer in conversation history, use that and DO NOT call tools unnecessarily.\n"
        "3. If you DON'T find the answer in conversation history, you MUST use the consult_researcher tool to search the knowledge base.\n"
        "4. NEVER say you don't know something without first searching the knowledge base using the researcher tool.\n"
        "5. The knowledge base contains the user's personal notes, documents, and information - search it when needed."
    ),
)


@orchestrator_agent.tool
async def consult_researcher(ctx: RunContext[None], question: str) -> str:
    """
    Searches the user's external notes and documents (like about-me.md or meeting notes).
    CRITICAL: DO NOT use this tool for conversational questions, personal preferences, or things the user just told you in the chat history.
    """
    # Try to show researcher step in Chainlit UI (falls back gracefully if not in Chainlit)
    try:
        import chainlit as cl
        async with cl.Step(name="Researcher Agent", type="tool") as step:
            step.input = question
            result = await notes_agent.run(question)
            step.output = result.output
            return result.output
    except:
        # Fallback for CLI mode
        print(f"   [Headquarters] Delegating '{question}' to Researcher...")
        result = await notes_agent.run(question)
        return result.output
