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
    "google-gla:gemini-2.0-flash",
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


# Manager: Handles the user and delegates
orchestrator_agent = Agent(
    "google-gla:gemini-2.0-flash",
    system_prompt="You are the Second Brain. Answer from history or use 'consult_researcher' for notes.",
)


@orchestrator_agent.tool
async def consult_researcher(ctx: RunContext[None], question: str) -> str:
    """Ask the specialist researcher to look through your notes."""
    result = await notes_agent.run(question)
    return result.output
