from dataclasses import dataclass, field

from pydantic import BaseModel
from pydantic_ai.messages import ToolCallPart
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, LLMJudge

from src.brain import orchestrator_agent

JUDGE_MODEL = "anthropic:claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Shared evaluators
# ---------------------------------------------------------------------------


@dataclass
class ContainsAny(Evaluator[str, str, None]):
    """Asserts that at least one of the expected keywords appears in the output (case-insensitive)."""

    keywords: list[str]

    def evaluate(self, ctx: EvaluatorContext[str, str, None]) -> bool:
        output_lower = ctx.output.lower()
        return any(kw.lower() in output_lower for kw in self.keywords)


# ---------------------------------------------------------------------------
# RAG retrieval task
# ---------------------------------------------------------------------------


async def ask_brain(question: str) -> str:
    result = await orchestrator_agent.run(question)
    return result.output


# ---------------------------------------------------------------------------
# Memory (multi-turn) task
# ---------------------------------------------------------------------------


class MemoryInput(BaseModel):
    setup: str
    question: str


class MemoryOutput(BaseModel):
    answer: str
    used_researcher: bool


async def ask_brain_with_memory(inputs: MemoryInput) -> MemoryOutput:
    first_result = await orchestrator_agent.run(inputs.setup)
    second_result = await orchestrator_agent.run(
        inputs.question, message_history=first_result.all_messages()
    )
    used_researcher = any(
        isinstance(part, ToolCallPart)
        and part.tool_name == "consult_researcher"
        for msg in second_result.new_messages()
        for part in msg.parts
    )
    return MemoryOutput(answer=second_result.output, used_researcher=used_researcher)


@dataclass
class MemoryContainsAny(Evaluator[MemoryInput, MemoryOutput, None]):
    """Asserts the answer contains at least one expected keyword."""

    keywords: list[str]

    def evaluate(self, ctx: EvaluatorContext[MemoryInput, MemoryOutput, None]) -> bool:
        return any(kw.lower() in ctx.output.answer.lower() for kw in self.keywords)


@dataclass
class DidNotUseResearcher(Evaluator[MemoryInput, MemoryOutput, None]):
    """Asserts the orchestrator answered from chat history, not by calling the researcher."""

    def evaluate(self, ctx: EvaluatorContext[MemoryInput, MemoryOutput, None]) -> bool:
        return not ctx.output.used_researcher


dataset = Dataset(
    name="second-brain-eval",
    cases=[
        # --- about-me.md ---
        Case(
            name="identity",
            inputs="Who is Boyu?",
            expected_output="Boyu likes creating stuff, whether it be code or music.",
            evaluators=[
                ContainsAny(keywords=["creating", "code", "music"]),
                LLMJudge(
                    rubric="The answer mentions that Boyu enjoys creating things, including code and music.",
                    include_input=True,
                    model=JUDGE_MODEL,
                ),
            ],
        ),
        Case(
            name="video_game",
            inputs="What video game has Boyu been playing recently?",
            expected_output="Hollow Knight: Silksong",
            evaluators=[
                ContainsAny(keywords=["Silksong", "Hollow Knight"]),
            ],
        ),
        Case(
            name="boss_fight",
            inputs="What boss did Boyu beat on February 10, 2026, and how many attempts did it take?",
            expected_output="Raging Conchfly, 33 attempts",
            evaluators=[
                ContainsAny(keywords=["Raging Conchfly"]),
                ContainsAny(keywords=["33"]),
            ],
        ),
        Case(
            name="music_project",
            inputs="What music project did Boyu work on in January 2026?",
            expected_output="A DJ set with picks from Taylor Swift's The Life of a Showgirl album.",
            evaluators=[
                ContainsAny(keywords=["DJ set", "Taylor Swift", "Showgirl"]),
            ],
        ),
        Case(
            name="second_brain_topic",
            inputs="What is the second brain project about?",
            expected_output="AI engineering",
            evaluators=[
                ContainsAny(keywords=["AI", "artificial intelligence"]),
            ],
        ),
    ],
    evaluators=[
        LLMJudge(
            rubric=(
                "This is a RAG chatbot that retrieves answers from the user's personal knowledge base. "
                "The expected_output contains the ground-truth facts from that knowledge base. "
                "Judge ONLY whether the response is consistent with the expected_output and "
                "directly answers the question. Do NOT penalize for facts you cannot independently verify — "
                "they come from the user's own notes."
            ),
            include_input=True,
            model=JUDGE_MODEL,
        ),
    ],
)


memory_dataset = Dataset[MemoryInput, MemoryOutput](
    name="memory-eval",
    cases=[
        Case(
            name="remember_fav_language",
            inputs=MemoryInput(
                setup="My favorite programming language is TypeScript.",
                question="What's my favorite programming language?",
            ),
            evaluators=[
                MemoryContainsAny(keywords=["TypeScript"]),
                DidNotUseResearcher(),
            ],
        ),
        Case(
            name="remember_coffee_shop_trip",
            inputs=MemoryInput(
                setup="I'm planning a trip to a coffee shop named The Southest Coffee next month.",
                question="Where am I planning to go?",
            ),
            evaluators=[
                MemoryContainsAny(keywords=["The Southest Coffee"]),
                DidNotUseResearcher(),
            ],
        ),
        Case(
            name="remember_pet",
            inputs=MemoryInput(
                setup="I just adopted a cat named Guaiguai.",
                question="What's my cat's name?",
            ),
            evaluators=[
                MemoryContainsAny(keywords=["Guaiguai"]),
                DidNotUseResearcher(),
            ],
        ),
    ],
)


if __name__ == "__main__":
    print("=" * 60)
    print("  RAG Retrieval Evaluation")
    print("=" * 60)
    rag_report = dataset.evaluate_sync(ask_brain)
    rag_report.print(include_reasons=True)

    print("\n")
    print("=" * 60)
    print("  Chat Memory Evaluation")
    print("=" * 60)
    memory_report = memory_dataset.evaluate_sync(ask_brain_with_memory)
    memory_report.print(include_reasons=True)
