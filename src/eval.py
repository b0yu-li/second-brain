from dataclasses import dataclass

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, LLMJudge

from src.brain import orchestrator_agent

JUDGE_MODEL = "anthropic:claude-sonnet-4-6"


@dataclass
class ContainsAny(Evaluator[str, str, None]):
    """Asserts that at least one of the expected keywords appears in the output (case-insensitive)."""

    keywords: list[str]

    def evaluate(self, ctx: EvaluatorContext[str, str, None]) -> bool:
        output_lower = ctx.output.lower()
        return any(kw.lower() in output_lower for kw in self.keywords)


async def ask_brain(question: str) -> str:
    result = await orchestrator_agent.run(question)
    return result.output


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


if __name__ == "__main__":
    report = dataset.evaluate_sync(ask_brain)
    report.print(include_reasons=True)
